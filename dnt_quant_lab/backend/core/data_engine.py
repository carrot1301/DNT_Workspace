import pandas as pd
import requests
import datetime
from functools import lru_cache

@lru_cache(maxsize=128)
def fetch_stock_data(ticker: str, days_back: int = 1000) -> pd.DataFrame:
    """Tải dữ liệu OHLCV lịch sử từ API (không cần Key)."""
    to_ts = int(datetime.datetime.now().timestamp())
    from_ts = int((datetime.datetime.now() - datetime.timedelta(days=days_back)).timestamp())
    
    # VN-Index uses 'VNINDEX' in entrade symbols
    symbol = ticker
    
    url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?symbol={symbol}&resolution=1D&from={from_ts}&to={to_ts}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        if 't' not in data or not data['t']:
            return pd.DataFrame()
            
        df = pd.DataFrame({
            'date': pd.to_datetime(data['t'], unit='s', utc=True).dt.tz_convert('Asia/Ho_Chi_Minh').dt.tz_localize(None).dt.normalize(),
            'open': data['o'],
            'high': data['h'],
            'low': data['l'],
            'close': data['c'],
            'volume': data['v']
        })
        df = df.groupby('date').last().reset_index()
        df.set_index('date', inplace=True)
        return df
    except Exception as e:
        print(f"Lỗi tải dữ liệu cho {ticker}: {e}")
        return pd.DataFrame()

def prepare_portfolio_data(tickers: list, days_back: int = 1000):
    """
    Tải và tính toán Daily Returns cho toàn bộ Tickers trong danh mục và VNINDEX.
    Trả về (Returns_DF, VNINDEX_Returns_Series)
    """
    price_data = {}
    for t in tickers:
        df = fetch_stock_data(t, days_back)
        if not df.empty:
            price_data[t] = df['close']
            
    # Lấy thêm VN-Index làm Market Benchmark
    vnindex_df = fetch_stock_data('VNINDEX', days_back)
    market_returns = pd.Series(dtype=float)
    if not vnindex_df.empty:
        market_returns = vnindex_df['close'].pct_change().dropna()
        
    portfolio_prices = pd.DataFrame(price_data)
    portfolio_returns = portfolio_prices.pct_change().dropna()
    
    # Align dates between portfolio and market
    aligned_data = pd.concat([portfolio_returns, market_returns.rename('VNINDEX')], axis=1).dropna()
    
    port_ret = aligned_data[tickers]
    mkt_ret = aligned_data['VNINDEX']
    
    return port_ret, mkt_ret

def fetch_current_prices(tickers: list) -> dict:
    """
    Truy vấn nhanh Giá Đóng cửa mới nhất của danh sách mã Cổ phiếu.
    Trọng tâm dành cho Lõi Tính Toán Đánh Giá Vốn Đang Ngâm (Evaluator).
    """
    prices = {}
    for t in tickers:
        df = fetch_stock_data(t, days_back=10) # 10 ngày để bù đắp nghỉ Lễ
        if not df.empty:
            prices[t] = df['close'].iloc[-1]
    return prices

