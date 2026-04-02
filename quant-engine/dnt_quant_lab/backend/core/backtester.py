import pandas as pd
import numpy as np
def simple_ma_crossover(df: pd.DataFrame, short_window: int = 20, long_window: int = 50) -> pd.DataFrame:
    """
    Kỳ vọng backtest dựa trên Giao cắt rãnh giá Moving Average.
    """
    signals = pd.DataFrame(index=df.index)
    signals['signal'] = 0.0

    # Tính Moving Average
    signals['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1, center=False).mean()

    # Tạo tín hiệu Bán/Mua (1.0 là Mua)
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] 
                                                > signals['long_mavg'][short_window:], 1.0, 0.0)   

    # Ghi nhận trạng thái chuyển dịch (Cross)
    signals['positions'] = signals['signal'].diff()
    return signals

from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf

def walk_forward_backtest(port_returns: pd.DataFrame, market_returns: pd.Series, 
                          train_window: int = 252, test_window: int = 21) -> dict:
    """
    [Tác Vụ 2.2 & 2.3] Walk-Forward Validation Backtesting
    Hệ thống backtest chia data thành In-Sample (train_window) để tìm Max Sharpe MVO,
    và Out-of-Sample (test_window) để đánh giá thực tế.
    Bao gồm cả Baseline: Equal Weight.
    """
    total_len = len(port_returns)
    if total_len <= train_window:
        # Nhỏ hơn train_window -> không đủ dữ liệu, fallback sang Equal Weight
        return fallback_backtest(port_returns, market_returns)

    # Khởi tạo kết quả chuỗi OOS
    oos_portfolio_returns = []
    oos_ew_returns = []
    oos_market_returns = []
    oos_dates = []

    tickers = port_returns.columns
    num_assets = len(tickers)
    
    # Baseline: Tỉ trọng đều (Equal Weight)
    ew_weights = np.ones(num_assets) / num_assets

    current_start = 0
    while current_start + train_window < total_len:
        train_end = current_start + train_window
        test_end = min(train_end + test_window, total_len)

        # 1. In-Sample Data (Train)
        train_data = port_returns.iloc[current_start:train_end]
        
        # MVO Math - Train
        mean_returns = train_data.mean() * 252
        cov_matrix_np = LedoitWolf().fit(train_data).covariance_
        cov_matrix = cov_matrix_np * 252
        
        # Variance Drag
        variances = np.diag(cov_matrix)
        expected_returns = mean_returns.values - (variances / 2)

        # Max Sharpe Optimization
        def negative_sharpe(w):
            w = np.array(w)
            port_r = np.sum(expected_returns * w)
            port_v = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
            # Sharpe: Giả định Risk Free = 3%
            return -((port_r - 0.03) / port_v)

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0.05, 0.40) for _ in range(num_assets))
        init_guess = ew_weights
        
        optimized_result = minimize(negative_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        ms_weights = optimized_result.x
        
        # 2. Out-of-Sample Data (Test)
        test_data = port_returns.iloc[train_end:test_end]
        test_mkt = market_returns.iloc[train_end:test_end]
        
        # Lợi nhuận danh mục MVO trong test_window
        daily_oos_mvo = test_data.dot(ms_weights)
        # Lợi nhuận danh mục Equal Weight trong test_window
        daily_oos_ew = test_data.dot(ew_weights)
        
        oos_portfolio_returns.extend(daily_oos_mvo.tolist())
        oos_ew_returns.extend(daily_oos_ew.tolist())
        oos_market_returns.extend(test_mkt.tolist())
        oos_dates.extend(test_data.index.tolist())

        # Cuộn cửa sổ
        current_start += test_window

    # Chuyển đổi Log Returns lũy kế (Tác Vụ 2.1)
    # Vì log returns có tính cộng dồn, ta dùng cumulative sum sau đó exp - 1
    # Tuy nhiên, nếu là simple list, ta làm như sau:
    mvo_series = pd.Series(oos_portfolio_returns, index=oos_dates)
    ew_series = pd.Series(oos_ew_returns, index=oos_dates)
    mkt_series = pd.Series(oos_market_returns, index=oos_dates)
    
    cum_mvo = np.exp(mvo_series.cumsum()) - 1
    cum_ew = np.exp(ew_series.cumsum()) - 1
    cum_mkt = np.exp(mkt_series.cumsum()) - 1

    dates_str = [d.strftime("%Y-%m-%d") for d in mvo_series.index]

    return {
        'dates': dates_str,
        'portfolio_cum_returns': cum_mvo.fillna(0).tolist(),
        'equal_weight_cum_returns': cum_ew.fillna(0).tolist(),
        'market_cum_returns': cum_mkt.fillna(0).tolist()
    }

def fallback_backtest(port_returns: pd.DataFrame, market_returns: pd.Series) -> dict:
    """Xử lý trường hợp dữ liệu quá ít (Chỉ báo Equal Weight)"""
    num_assets = len(port_returns.columns)
    if num_assets == 0:
        return {'dates': [], 'portfolio_cum_returns': [], 'equal_weight_cum_returns': [], 'market_cum_returns': []}
        
    ew_weights = np.ones(num_assets) / num_assets
    daily_ew = port_returns.dot(ew_weights)
    
    cum_ew = np.exp(daily_ew.cumsum()) - 1
    cum_mkt = np.exp(market_returns.cumsum()) - 1
    
    # Đồng bộ index
    cum_mkt = cum_mkt.reindex(cum_ew.index).ffill().fillna(0)
    dates_str = [d.strftime("%Y-%m-%d") for d in cum_ew.index]
    
    return {
        'dates': dates_str,
        'portfolio_cum_returns': cum_ew.fillna(0).tolist(), # Fallback MVO thành EW
        'equal_weight_cum_returns': cum_ew.fillna(0).tolist(),
        'market_cum_returns': cum_mkt.tolist()
    }
