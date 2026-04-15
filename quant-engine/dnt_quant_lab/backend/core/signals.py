import pandas as pd
from core.data_engine import fetch_stock_data
from core.ta_engine import compute_full_ta

def compute_signals(tickers: list, weights: dict, capital: float) -> dict:
    """
    Phân tích Technical Analysis.
    Tính toán tín hiệu (Action) và khối lượng (Volume) khuyến nghị.
    """
    signals = {}
    
    for ticker in tickers:
        df = fetch_stock_data(ticker, days_back=365)
        
        target_weight = weights.get(ticker, 0)
        target_allocation = capital * target_weight
        
        if df.empty or len(df) < 50:
            signals[ticker] = {
                "action": "HOLD",
                "detail": "Đợi Dữ Liệu",
                "price": 0,
                "volume": 0,
                "broker_url": "https://smartoneweb.vps.com.vn/",
                "ta_analysis": None
            }
            continue
            
        ta_data = compute_full_ta(df, ticker)
        current_price = ta_data.get("current_price", 0)
        
        # Lấy overall signal từ TA engine
        if "summary" in ta_data:
            action = ta_data["summary"]["overall_signal"]
            score = ta_data["summary"]["score"]
            detail = f"Điểm TA: {score:.2f} | B:{ta_data['summary']['buy_count']} S:{ta_data['summary']['sell_count']} N:{ta_data['summary']['neutral_count']}"
        else:
            action = "HOLD"
            detail = "Lỗi xử lý TA"
            
        # Tính toán khối lượng lô 100
        if current_price > 0:
            raw_volume = target_allocation / current_price
            volume = int(raw_volume // 100) * 100
        else:
            volume = 0
            
        signals[ticker] = {
            "action": action,
            "detail": detail,
            "price": current_price,
            "volume": volume,
            "broker_url": "https://smartoneweb.vps.com.vn/",
            "ta_analysis": ta_data
        }
        
    return signals
