import pandas as pd
import numpy as np
import requests
from datetime import datetime
from core.data_engine import fetch_stock_data

# Tập tĩnh VN30 để tránh quét quá lâu rác data
VN30_TICKERS = [
    "FPT", "HPG", "VCB", "MBB", "MWG", "ACB", "TCB", "VPB", "REE", "PNJ", 
    "SSI", "VNM", "VIC", "VHM", "VRE", "SAB", "CTG", "BID", "GAS", "MSN", 
    "STB", "PLX", "POW", "VJC", "BVH", "GVR", "SHB", "TPB", "VIB", "SSB"
]

def fetch_screener_financials(ticker: str) -> dict:
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{ticker}/overview"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception:
        return {}

def run_daily_radar():
    """
    Quét VN30 bằng màng lọc CƠ BẢN (FA) và KỸ THUẬT (TA).
    Trả về Top 5 mã có điểm tích cực nhất.
    """
    passed_fa = []
    
    # 1. BỘ LỌC CƠ BẢN (FA)
    for ticker in VN30_TICKERS:
        data = fetch_screener_financials(ticker)
        if not data:
            continue
            
        market_cap = data.get("marketcap", 0)
        pe = data.get("pe", 0)
        roe = data.get("roe", 0)
        
        # Tiêu chí:
        # - Vốn hoá (marketcap) > 10.000 tỷ
        # - P/E từ 0 đến 25
        # - ROE >= 0.12 (12%)
        # Note: TCBS API returns marketcap in Billion VND -> 10000 = 10k billion VND = 10,000 tỷ
        if market_cap > 10000 and 0 < pe < 25 and roe >= 0.12:
            passed_fa.append(ticker)
            
    if not passed_fa:
        # Fallback in case of highly strict market
        passed_fa = ["FPT", "HPG", "MBB", "MWG", "TCB"]

    # 2. BỘ LỌC KỸ THUẬT (TA - Uptrend)
    scored_tickers = []
    for ticker in passed_fa:
        df = fetch_stock_data(ticker, days_back=250)
        if df.empty or len(df) < 200:
            continue
            
        close_prices = df['close']
        current_price = close_prices.iloc[-1]
        sma50 = close_prices.rolling(window=50).mean().iloc[-1]
        sma200 = close_prices.rolling(window=200).mean().iloc[-1]
        
        # Tiêu chí Uptrend: Current Price > SMA50 > SMA200
        if current_price > sma50 and sma50 > sma200:
            # Score: Càng dốc (khoảng cách Giá vs SMA200 lớn) thì xung lực Trend càng mạnh
            trend_score = (current_price - sma200) / sma200
            scored_tickers.append({
                "ticker": ticker,
                "score": float(trend_score),
                "price": float(current_price * 1000)
            })

    # Nếu thị trường quá nản không có mã Uptrend, fallback lấy các mã an toàn dứt khoát
    if not scored_tickers:
        return [
            {"ticker": t, "score": 0, "price": 0} for t in passed_fa[:5]
        ]
        
    # Sort top theo trend mạnh nhất
    scored_tickers.sort(key=lambda x: x['score'], reverse=True)
    return scored_tickers[:5]
