import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf
from core.data_engine import fetch_stock_data, fetch_index_data


# Transaction cost: 0.15% mỗi lệnh (phí sàn VN tiêu chuẩn)
TRANSACTION_COST = 0.0015


def run_backtrader_strategy(tickers: list, weights: dict, initial_capital: float, days_back: int = 252) -> dict:
    """
    Rolling Walk-Forward Backtest.
    
    [Expert Fix] Thay thế Buy-and-Hold tĩnh (có look-ahead bias) bằng
    Rolling Walk-Forward: re-optimize mỗi tháng trên in-sample data,
    áp dụng weights cho tháng tiếp theo (out-of-sample).
    
    Pipeline:
    1. Chia timeline thành monthly periods
    2. Tại mỗi tháng t:
       - Train: dùng 126 ngày trước đó (6 tháng in-sample)
       - Optimize weights trên train data (simplified Max Sharpe)
       - Apply weights cho tháng t (out-of-sample)
       - Tính transaction cost từ weight changes
    3. Chain monthly out-of-sample returns → cumulative return
    
    So sánh với VN30 benchmark.
    
    Tham khảo: Walk-Forward Optimization (Pardo, 2008)
    """
    if not tickers or not weights:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}

    # 1. Fetch dữ liệu giá đóng cửa
    price_data = {}
    for ticker in tickers:
        df = fetch_stock_data(ticker, days_back=days_back + 150)  # Buffer cho train window
        if not df.empty and 'close' in df.columns:
            price_data[ticker] = df['close']

    if not price_data:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}

    # 2. Tạo DataFrame và tính Log Returns
    prices_df = pd.DataFrame(price_data)
    prices_df = prices_df.dropna()

    if len(prices_df) < 60:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}

    log_returns = np.log(prices_df / prices_df.shift(1)).dropna()

    # Lọc spike (Biên độ sàn UPCOM tối đa 15%)
    for col in log_returns.columns:
        log_returns[col] = log_returns[col].clip(-0.15, 0.15)

    # Cắt lấy đúng days_back ngày gần nhất
    if len(log_returns) > days_back:
        log_returns = log_returns.tail(days_back)

    # 3. Chuẩn hóa trọng số cho các mã có sẵn dữ liệu
    available_tickers = [t for t in tickers if t in log_returns.columns]
    if not available_tickers:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}

    # -----------------------------------------------------------------
    # ROLLING WALK-FORWARD
    # -----------------------------------------------------------------
    TRAIN_WINDOW = 126   # 6 tháng in-sample
    REBALANCE_PERIOD = 21  # ~1 tháng trading days
    
    dates_all = log_returns.index
    n_days = len(dates_all)
    
    # Nếu không đủ data cho rolling, fallback về static
    if n_days < TRAIN_WINDOW + REBALANCE_PERIOD:
        return _static_backtest(log_returns, available_tickers, weights, days_back)
    
    # Tính rolling monthly returns
    portfolio_daily_returns = pd.Series(0.0, index=dates_all[TRAIN_WINDOW:], dtype=float)
    prev_weights = np.zeros(len(available_tickers))
    total_turnover = 0.0
    
    # Rolling loop
    start_idx = TRAIN_WINDOW
    while start_idx < n_days:
        end_idx = min(start_idx + REBALANCE_PERIOD, n_days)
        
        # Train window: 126 ngày trước thời điểm hiện tại
        train_data = log_returns[available_tickers].iloc[start_idx - TRAIN_WINDOW:start_idx]
        
        # Optimize on train data (simplified Max Sharpe)
        current_weights = _simplified_optimize(train_data)
        
        # Transaction cost từ weight changes
        turnover = np.abs(current_weights - prev_weights).sum()
        total_turnover += turnover
        tc = turnover * TRANSACTION_COST
        
        # Out-of-sample returns cho period này
        test_data = log_returns[available_tickers].iloc[start_idx:end_idx]
        daily_ret = test_data.dot(current_weights)
        
        # Trừ transaction cost (phân bổ đều cho các ngày trong period)
        if len(daily_ret) > 0:
            daily_tc = tc / len(daily_ret)
            daily_ret = daily_ret - daily_tc
        
        portfolio_daily_returns.iloc[start_idx - TRAIN_WINDOW:end_idx - TRAIN_WINDOW] = daily_ret.values[:end_idx - start_idx]
        
        prev_weights = current_weights
        start_idx = end_idx
    
    # Trim NaN
    portfolio_daily_returns = portfolio_daily_returns.dropna()
    if len(portfolio_daily_returns) == 0:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}
    
    # Cumulative returns
    portfolio_cum_returns = np.exp(portfolio_daily_returns.cumsum()) - 1.0

    # 6. Fetch VN30 Benchmark
    mkt_df = fetch_index_data('VN30', days_back=days_back + 30)
    market_cum_returns = _get_market_cum_returns(mkt_df, portfolio_cum_returns)

    # 7. Output
    dates_str = [d.strftime("%Y-%m-%d") for d in portfolio_cum_returns.index]

    return {
        'dates': dates_str,
        'portfolio_cum_returns': portfolio_cum_returns.tolist(),
        'market_cum_returns': market_cum_returns
    }


def _simplified_optimize(returns_df: pd.DataFrame) -> np.ndarray:
    """
    Simplified Max Sharpe optimization cho rolling backtest.
    Dùng Ledoit-Wolf shrinkage nhưng không dùng BL/Factor (vì backtest
    cần phản ánh thuần tuý price-based optimization, không look-ahead).
    """
    n = len(returns_df.columns)
    if n < 2:
        return np.ones(n) / n
    
    mean_returns = returns_df.mean() * 252  # Annualized
    
    try:
        cov_matrix = LedoitWolf().fit(returns_df).covariance_ * 252
    except Exception:
        cov_matrix = returns_df.cov().values * 252
    
    risk_free = 0.03  # 3% annually
    
    def neg_sharpe(w):
        ret = w @ mean_returns.values
        vol = np.sqrt(w @ cov_matrix @ w)
        if vol < 1e-10:
            return 0
        return -(ret - risk_free) / vol
    
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    bounds = [(0.05, 0.40)] * n
    init = np.ones(n) / n
    
    try:
        result = minimize(neg_sharpe, init, method='SLSQP', 
                         bounds=bounds, constraints=constraints)
        if result.success:
            return result.x
    except Exception:
        pass
    
    return np.ones(n) / n


def _static_backtest(log_returns: pd.DataFrame, tickers: list, 
                     weights: dict, days_back: int) -> dict:
    """
    Fallback: Static Buy-and-Hold backtest khi không đủ data cho rolling.
    """
    w_sum = sum(weights.get(t, 0) for t in tickers)
    if w_sum <= 0:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}

    norm_weights = np.array([weights.get(t, 0) / w_sum for t in tickers])
    portfolio_daily_returns = log_returns[tickers].dot(norm_weights)
    portfolio_cum_returns = np.exp(portfolio_daily_returns.cumsum()) - 1.0

    mkt_df = fetch_index_data('VN30', days_back=days_back + 30)
    market_cum_returns = _get_market_cum_returns(mkt_df, portfolio_cum_returns)

    dates_str = [d.strftime("%Y-%m-%d") for d in portfolio_cum_returns.index]
    return {
        'dates': dates_str,
        'portfolio_cum_returns': portfolio_cum_returns.tolist(),
        'market_cum_returns': market_cum_returns
    }


def _get_market_cum_returns(mkt_df: pd.DataFrame, portfolio_cum_returns: pd.Series) -> list:
    """Helper: Tính cumulative returns cho VN30 benchmark, align với portfolio dates."""
    if not mkt_df.empty and 'close' in mkt_df.columns:
        mkt_df.index = pd.to_datetime(mkt_df.index)
        mkt_log_returns = np.log(mkt_df['close'] / mkt_df['close'].shift(1)).dropna()
        aligned_mkt = mkt_log_returns.reindex(portfolio_cum_returns.index)
        aligned_mkt = aligned_mkt.ffill().bfill().fillna(0)
        return (np.exp(aligned_mkt.cumsum()) - 1.0).tolist()
    else:
        return [0.0] * len(portfolio_cum_returns)
