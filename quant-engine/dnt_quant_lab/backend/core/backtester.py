import pandas as pd
import numpy as np
from core.data_engine import fetch_stock_data, fetch_index_data


def run_backtrader_strategy(tickers: list, weights: dict, initial_capital: float, days_back: int = 252) -> dict:
    """
    Backtest Buy-and-Hold với trọng số MVO tối ưu.
    Tính lợi nhuận tích lũy (Cumulative Returns) của danh mục so với VN30 Benchmark.
    
    Phương pháp:
    - Dùng Log Returns hàng ngày cho từng mã cổ phiếu.
    - Tính Daily Portfolio Return = Σ(weight_i × return_i).
    - Cumulative Return = exp(cumsum(daily_returns)) - 1.
    
    Trả về:
    - dates: list ngày tháng ("YYYY-MM-DD")
    - portfolio_cum_returns: list % lợi nhuận tích lũy của danh mục MVO.
    - market_cum_returns: list % lợi nhuận tích lũy VN30 làm Benchmark.
    """
    if not tickers or not weights:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}

    # 1. Fetch dữ liệu giá đóng cửa cho tất cả tickers
    price_data = {}
    for ticker in tickers:
        df = fetch_stock_data(ticker, days_back=days_back + 30)  # Thêm buffer cho ngày nghỉ
        if not df.empty and 'close' in df.columns:
            price_data[ticker] = df['close']

    if not price_data:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}

    # 2. Tạo DataFrame giá và tính Log Returns
    prices_df = pd.DataFrame(price_data)
    prices_df = prices_df.dropna()

    if len(prices_df) < 2:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}

    log_returns = np.log(prices_df / prices_df.shift(1)).dropna()

    # Lọc spike (Biên độ sàn UPCOM tối đa 15%)
    log_returns = log_returns[(log_returns < 0.15) & (log_returns > -0.15)].dropna()

    # Cắt lấy đúng days_back ngày gần nhất
    if len(log_returns) > days_back:
        log_returns = log_returns.tail(days_back)

    # 3. Chuẩn hóa trọng số cho các mã có sẵn dữ liệu
    available_tickers = [t for t in tickers if t in log_returns.columns]
    if not available_tickers:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}

    w_sum = sum(weights.get(t, 0) for t in available_tickers)
    if w_sum <= 0:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}

    norm_weights = np.array([weights.get(t, 0) / w_sum for t in available_tickers])

    # 4. Tính Daily Portfolio Returns (weighted sum)
    portfolio_daily_returns = log_returns[available_tickers].dot(norm_weights)

    # 5. Tính Cumulative Returns (Log Returns → exp(cumsum) - 1)
    portfolio_cum_returns = np.exp(portfolio_daily_returns.cumsum()) - 1.0

    # 6. Fetch VN30 Benchmark
    mkt_df = fetch_index_data('VN30', days_back=days_back + 30)
    market_cum_returns = []

    if not mkt_df.empty and 'close' in mkt_df.columns:
        mkt_df.index = pd.to_datetime(mkt_df.index)
        mkt_log_returns = np.log(mkt_df['close'] / mkt_df['close'].shift(1)).dropna()

        # Align market với portfolio dates
        aligned_mkt = mkt_log_returns.reindex(portfolio_cum_returns.index)
        
        # Fill forward nếu thiếu ngày, drop NaN còn lại
        aligned_mkt = aligned_mkt.ffill().bfill().fillna(0)

        market_cum_returns = (np.exp(aligned_mkt.cumsum()) - 1.0).tolist()
    else:
        market_cum_returns = [0.0] * len(portfolio_cum_returns)

    # 7. Chuẩn bị output
    dates_str = [d.strftime("%Y-%m-%d") for d in portfolio_cum_returns.index]

    return {
        'dates': dates_str,
        'portfolio_cum_returns': portfolio_cum_returns.tolist(),
        'market_cum_returns': market_cum_returns
    }
