import pandas as pd
import requests
import requests_cache
import os
import datetime

cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache_db')
os.makedirs(cache_dir, exist_ok=True)
requests_cache.install_cache(os.path.join(cache_dir, 'dnt_market_cache'), backend='sqlite', expire_after=86400)

def fetch_index_data(symbol: str = 'VNINDEX', days_back: int = 1000) -> pd.DataFrame:
    """Tải dữ liệu lịch sử Index (VNINDEX, VN30) qua endpoint /index."""
    now = datetime.datetime.now()
    # Làm tròn timestamp đến giờ (hoặc ngày) để requests_cache hoạt động, tránh tạo URL mới liên tục mỗi giây
    now_rounded = now.replace(minute=0, second=0, microsecond=0)
    to_ts = int(now_rounded.timestamp())
    from_ts = int((now_rounded - datetime.timedelta(days=days_back)).timestamp())
    url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/index?symbol={symbol}&resolution=1D&from={from_ts}&to={to_ts}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        if 't' not in data or not data['t']:
            return pd.DataFrame()
        dates = pd.to_datetime(data['t'], unit='s', utc=True)
        dates = dates.tz_convert('Asia/Ho_Chi_Minh').tz_localize(None).normalize()
        df = pd.DataFrame({'date': dates, 'close': data['c']})
        df = df.groupby('date').last().reset_index()
        df.set_index('date', inplace=True)
        return df
    except Exception as e:
        print(f"Index Fetch Error for {symbol}: {e}")
        return pd.DataFrame()


def fetch_stock_data(ticker: str, days_back: int = 1000) -> pd.DataFrame:
    """Tải dữ liệu OHLCV lịch sử từ API (không cần Key)."""
    now = datetime.datetime.now()
    # Làm tròn timestamp đến giờ để cache hoạt động
    now_rounded = now.replace(minute=0, second=0, microsecond=0)
    to_ts = int(now_rounded.timestamp())
    from_ts = int((now_rounded - datetime.timedelta(days=days_back)).timestamp())
    
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
            
        dates = pd.to_datetime(data['t'], unit='s', utc=True)
        dates = dates.tz_convert('Asia/Ho_Chi_Minh').tz_localize(None).normalize()
        df = pd.DataFrame({
            'date': dates,
            'open': data['o'],
            'high': data['h'],
            'low': data['l'],
            'close': data['c'],
            'volume': data['v']
        })
        if df.empty:
            return pd.DataFrame()
        df = df.groupby('date').last().reset_index()
        df.set_index('date', inplace=True)
        return df
    except Exception as e:
        print(f"Data Fetch Error for {ticker}: {e}")
        return pd.DataFrame()

def prepare_portfolio_data(tickers: list, days_back: int = 1000):
    """
    Tải và tính toán Daily Returns cho toàn bộ Tickers trong danh mục và VNINDEX.
    Trả về (Returns_DF, VNINDEX_Returns_Series)
    """
    price_data = {}
    for t in tickers:
        df = fetch_stock_data(t, days_back)
        if not df.empty and 'close' in df.columns:
            price_data[t] = df['close']
            
    # Lấy thêm VN30 làm Market Benchmark (VNINDEX không hỗ trợ qua stock endpoint)
    vnindex_df = fetch_index_data('VN30', days_back)
    market_returns = pd.Series(dtype=float)
    if not vnindex_df.empty and 'close' in vnindex_df.columns:
        # [BẢN SỬA LỖI] Đồng nhất với Log Returns
        import numpy as np
        market_returns = np.log(vnindex_df['close'] / vnindex_df['close'].shift(1)).dropna()
        
    if not price_data:
        return pd.DataFrame(), pd.Series(dtype=float)

    portfolio_prices = pd.DataFrame(price_data)
    # [BẢN SỬA LỖI] Chuyển đổi sang Log Returns để ổn định ma trận hiệp phương sai
    import numpy as np
    portfolio_returns = np.log(portfolio_prices / portfolio_prices.shift(1))
    
    # [FIX] Clip per-column thay vì mask cả dòng — giữ lại data hợp lệ của các cổ phiếu khác
    # khi 1 mã có spike do chia tách hoặc lỗi API
    for col in portfolio_returns.columns:
        portfolio_returns[col] = portfolio_returns[col].clip(-0.15, 0.15)
    portfolio_returns = portfolio_returns.dropna()
    
    # Align dates between portfolio and market
    if market_returns.empty:
        return portfolio_returns, pd.Series(0, index=portfolio_returns.index)

    aligned_data = pd.concat([portfolio_returns, market_returns.rename('VNINDEX')], axis=1).dropna()
    
    # Ensure all original tickers are present in the final data
    available_tickers = [t for t in tickers if t in aligned_data.columns]
    if not available_tickers:
        return pd.DataFrame(), pd.Series(dtype=float)

    port_ret = aligned_data[available_tickers]
    mkt_ret = aligned_data['VNINDEX']
    
    return port_ret, mkt_ret

def fetch_current_prices(tickers: list) -> dict:
    """
    Truy vấn nhanh Giá Đóng cửa mới nhất của danh sách mã Cổ phiếu.
    Nhân với 1000 để chuyển đổi hệ số của API Entrade về đơn vị VND thực tế (VD: 74.0 -> 74000).
    """
    prices = {}
    for t in tickers:
        df = fetch_stock_data(t, days_back=10) # 10 ngày để bù đắp nghỉ Lễ
        if not df.empty:
            prices[t] = float(df['close'].iloc[-1]) * 1000
    return prices

# Cache nhẹ cho Ticker Tape (5 phút)
_tape_cache = {"ts": 0, "data": {}}

def _fetch_stock_uncached(ticker: str, days_back: int = 10) -> pd.DataFrame:
    """Lấy dữ liệu giá KHÔNG qua requests_cache để luôn fresh."""
    import requests as raw_requests
    now = datetime.datetime.now()
    now_rounded = now.replace(minute=0, second=0, microsecond=0)
    to_ts = int(now_rounded.timestamp())
    from_ts = int((now_rounded - datetime.timedelta(days=days_back)).timestamp())
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?symbol={ticker}&resolution=1D&from={from_ts}&to={to_ts}"
        with raw_requests.Session() as s:
            res = s.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        if 't' not in data or not data['t']:
            return pd.DataFrame()
        dates = pd.to_datetime(data['t'], unit='s', utc=True)
        dates = dates.tz_convert('Asia/Ho_Chi_Minh').tz_localize(None).normalize()
        df = pd.DataFrame({'date': dates, 'close': data['c']})
        df = df.groupby('date').last().reset_index()
        df.set_index('date', inplace=True)
        return df
    except Exception as e:
        print(f"Tape Fetch Error for {ticker}: {e}")
        return pd.DataFrame()

def _fetch_index_uncached(symbol: str = 'VN30', days_back: int = 10) -> pd.DataFrame:
    """Lấy dữ liệu index KHÔNG qua requests_cache."""
    import requests as raw_requests
    now = datetime.datetime.now()
    now_rounded = now.replace(minute=0, second=0, microsecond=0)
    to_ts = int(now_rounded.timestamp())
    from_ts = int((now_rounded - datetime.timedelta(days=days_back)).timestamp())
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/index?symbol={symbol}&resolution=1D&from={from_ts}&to={to_ts}"
        with raw_requests.Session() as s:
            res = s.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        if 't' not in data or not data['t']:
            return pd.DataFrame()
        dates = pd.to_datetime(data['t'], unit='s', utc=True)
        dates = dates.tz_convert('Asia/Ho_Chi_Minh').tz_localize(None).normalize()
        df = pd.DataFrame({'date': dates, 'close': data['c']})
        df = df.groupby('date').last().reset_index()
        df.set_index('date', inplace=True)
        return df
    except Exception as e:
        print(f"Tape Index Fetch Error for {symbol}: {e}")
        return pd.DataFrame()

def fetch_ticker_tape_data() -> dict:
    """Fetch prices and 1-day % change for Ticker Tape. Cache 5 phút trong RAM."""
    import time
    now = time.time()
    if _tape_cache["data"] and (now - _tape_cache["ts"]) < 300:  # 5 phút
        return _tape_cache["data"]
    
    tickers = ['VN30', 'FPT', 'MWG', 'VCB', 'HPG', 'TCB', 'SSI']
    tape_data = {}
    for t in tickers:
        if t == 'VN30':
            df = _fetch_index_uncached('VN30', days_back=10)
        else:
            df = _fetch_stock_uncached(t, days_back=10)
            
        if not df.empty and len(df) >= 2:
            current_price = float(df['close'].iloc[-1])
            prev_price = float(df['close'].iloc[-2])
            change_pct = ((current_price - prev_price) / prev_price) * 100
            
            if t != 'VN30':
                current_price *= 1000
                
            tape_data[t] = {
                "price": current_price,
                "change_pct": round(change_pct, 2)
            }
        elif not df.empty and len(df) == 1:
            current_price = float(df['close'].iloc[-1])
            if t != 'VN30': current_price *= 1000
            tape_data[t] = {"price": current_price, "change_pct": 0}
        else:
            tape_data[t] = {"price": 0, "change_pct": 0}
    
    _tape_cache["data"] = tape_data
    _tape_cache["ts"] = now
    return tape_data

def fetch_recent_news(tickers: list, limit: int = 3) -> dict:
    """
    Sử dụng thư viện vnstock3 để kéo tin tức công ty mới nhất.
    Nếu vnstock3 fail hoặc không có tin → fallback sang RSS (VnExpress, Tuổi Trẻ).
    Trả về dict: { "FPT": [ {"title": "...", "summary": "...", "publishDate": "..."} ] }
    """
    news_data = {}
    vnstock_failed = False
    
    try:
        from vnstock3 import Vnstock
        for t in tickers:
            try:
                stock = Vnstock().stock(symbol=t, source='TCBS')
                df = stock.company.news()
                if df is not None and not df.empty:
                    tops = df.head(limit)
                    t_news = []
                    for _, row in tops.iterrows():
                        t_news.append({
                            "publishDate": str(row.get('publishDate', '')),
                            "title": str(row.get('title', '')),
                            "summary": str(row.get('summary', ''))
                        })
                    news_data[t] = t_news
                else:
                    news_data[t] = []
            except Exception as e:
                print(f"Error fetching news for {t}: {e}")
                news_data[t] = []
    except ImportError:
        print("vnstock3 library is not available. Falling back to RSS.")
        vnstock_failed = True
    
    # Fallback: dùng RSS cho các ticker không có tin vnstock3
    tickers_need_rss = [t for t in tickers if not news_data.get(t)]
    if tickers_need_rss or vnstock_failed:
        try:
            from core.rss_engine import search_news_by_tickers
            rss_results = search_news_by_tickers(
                tickers_need_rss if tickers_need_rss else tickers,
                limit=limit
            )
            for t, articles in rss_results.items():
                if not news_data.get(t) and articles:
                    # Convert RSS format to vnstock format
                    news_data[t] = [{
                        "publishDate": art.get("pubDate", ""),
                        "title": art.get("title", ""),
                        "summary": art.get("summary", "")
                    } for art in articles[:limit]]
        except Exception as e:
            print(f"RSS Fallback Error: {e}")
    
    return news_data

