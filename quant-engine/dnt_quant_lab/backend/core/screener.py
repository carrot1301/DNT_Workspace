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

def _compute_ta_score(ticker: str) -> dict | None:
    """Tính điểm TA cho một mã. Trả về dict hoặc None nếu lỗi."""
    try:
        df = fetch_stock_data(ticker, days_back=250)
        if df.empty or len(df) < 50:
            return None
            
        close_prices = df['close']
        current_price = close_prices.iloc[-1]
        sma20 = close_prices.rolling(window=20).mean().iloc[-1]
        sma50 = close_prices.rolling(window=50).mean().iloc[-1]
        
        # Tính SMA200 nếu đủ data, nếu không thì dùng SMA100
        if len(df) >= 200:
            sma_long = close_prices.rolling(window=200).mean().iloc[-1]
        elif len(df) >= 100:
            sma_long = close_prices.rolling(window=100).mean().iloc[-1]
        else:
            sma_long = sma50 * 0.95  # Ước lượng
        
        # Score system: điểm cộng dồn thay vì chỉ filter binary
        score = 0.0
        
        # Giá trên SMA20 (+0.2)
        if current_price > sma20:
            score += 0.2
        
        # Giá trên SMA50 (+0.3)
        if current_price > sma50:
            score += 0.3
            
        # SMA50 trên SMA_long (Golden Cross signal) (+0.3)
        if sma50 > sma_long:
            score += 0.3
            
        # Momentum: khoảng cách giá vs SMA_long (+0.0 đến +0.2)
        if sma_long > 0:
            momentum = (current_price - sma_long) / sma_long
            score += min(max(momentum, 0), 0.2)  # Cap tại 0.2
        
        if score > 0.1:  # Chỉ cần có ít nhất 1 tín hiệu tích cực
            return {
                "ticker": ticker,
                "score": round(float(score), 3),
                "price": float(current_price * 1000)
            }
        return None
    except Exception as e:
        print(f"TA Error for {ticker}: {e}")
        return None

def run_daily_radar():
    """
    Quét VN30 bằng màng lọc CƠ BẢN (FA) và KỸ THUẬT (TA).
    Trả về Top 5 mã có điểm tích cực nhất.
    Cải thiện: Bộ lọc FA mềm hơn, TA scoring linh hoạt hơn, không bị lặp.
    """
    # Chia thành 2 nhóm: qua FA tốt và qua FA trung bình
    passed_fa_strong = []
    passed_fa_moderate = []
    
    # 1. BỘ LỌC CƠ BẢN (FA) — 2 tầng
    for ticker in VN30_TICKERS:
        try:
            data = fetch_screener_financials(ticker)
            if not data:
                continue
                
            market_cap = data.get("marketcap", 0) or 0
            pe = data.get("pe", 0) or 0
            roe = data.get("roe", 0) or 0
            
            # Tầng 1 (Mạnh): Vốn hoá > 10k tỷ, P/E 0-25, ROE >= 12%
            if market_cap > 10000 and 0 < pe < 25 and roe >= 0.12:
                passed_fa_strong.append(ticker)
            # Tầng 2 (Trung bình): Vốn hoá > 5k tỷ, P/E 0-30, ROE >= 8%
            elif market_cap > 5000 and 0 < pe < 30 and roe >= 0.08:
                passed_fa_moderate.append(ticker)
        except Exception as e:
            print(f"FA Error for {ticker}: {e}")
            continue
    
    # Kết hợp: ưu tiên strong, bổ sung moderate
    candidates = passed_fa_strong + [t for t in passed_fa_moderate if t not in passed_fa_strong]
    
    if not candidates:
        # Fallback: dùng top blue-chips VN30 nhưng xáo trộn để không lặp
        import random
        fallback_pool = ["FPT", "HPG", "MBB", "MWG", "TCB", "VCB", "ACB", "VPB", "CTG", "SSI"]
        random.shuffle(fallback_pool)
        candidates = fallback_pool[:8]

    # 2. BỘ LỌC KỸ THUẬT (TA - Scoring System)
    scored_tickers = []
    for ticker in candidates:
        result = _compute_ta_score(ticker)
        if result:
            scored_tickers.append(result)

    # Nếu không có mã nào qua TA, chạy TA cho top blue-chips làm fallback
    if not scored_tickers:
        import random
        fallback_ta = ["FPT", "VCB", "MBB", "ACB", "TCB", "HPG", "MWG", "VPB"]
        random.shuffle(fallback_ta)
        for ticker in fallback_ta[:6]:
            result = _compute_ta_score(ticker)
            if result:
                # Giảm score vì đây là fallback
                result["score"] = round(result["score"] * 0.7, 3)
                scored_tickers.append(result)
        
        # Nếu vẫn rỗng, trả về data tĩnh với giá thực
        if not scored_tickers:
            for ticker in ["FPT", "MBB", "TCB", "ACB", "HPG"]:
                try:
                    df = fetch_stock_data(ticker, days_back=10)
                    price = float(df['close'].iloc[-1]) * 1000 if not df.empty else 0
                    scored_tickers.append({"ticker": ticker, "score": 0.1, "price": price})
                except Exception:
                    scored_tickers.append({"ticker": ticker, "score": 0.1, "price": 0})
        
    # Sort top theo trend mạnh nhất
    scored_tickers.sort(key=lambda x: x['score'], reverse=True)
    return scored_tickers[:5]
