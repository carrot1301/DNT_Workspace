import pandas as pd
import requests
import datetime
import streamlit as st

@st.cache_data(ttl=86400)
def fetch_stock_data(ticker: str, days_back: int = 1000) -> pd.DataFrame:
    """Tải dữ liệu OHLCV lịch sử từ API (không cần Key)."""
    to_ts = int(datetime.datetime.now().timestamp())
    from_ts = int((datetime.datetime.now() - datetime.timedelta(days=days_back)).timestamp())
    
    url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?symbol={ticker}&resolution=1D&from={from_ts}&to={to_ts}"
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
