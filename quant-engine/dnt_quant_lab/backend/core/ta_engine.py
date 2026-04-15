import pandas as pd
import pandas_ta as ta
import numpy as np

def compute_full_ta(df: pd.DataFrame, ticker: str = "") -> dict:
    """
    Computes comprehensive technical analysis indicators using pandas_ta.
    """
    if df is None or df.empty or len(df) < 200:
        return {
            "ticker": ticker,
            "error": "Insufficient data for TA (need >= 200 days)"
        }

    # Ensure index is datetime and sorted
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    
    # Calculate indicators
    try:
        # Trend
        df.ta.sma(length=10, append=True)
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.sma(length=200, append=True)
        df.ta.ema(length=10, append=True)
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.ema(length=200, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.adx(length=14, append=True)
        
        # Oscillators
        df.ta.rsi(length=14, append=True)
        df.ta.stoch(append=True) # STOCHk_14_3_3, STOCHd_14_3_3
        df.ta.cci(length=14, append=True)
        df.ta.willr(length=14, append=True)
        
        # Volatility
        df.ta.bbands(length=20, append=True) # BBL_20_2.0, BBM_20_2.0, BBU_20_2.0
        
        # Volume
        df.ta.obv(append=True)
        df.ta.mfi(length=14, append=True)
        
    except Exception as e:
        return {"ticker": ticker, "error": f"TA computation failed: {str(e)}"}

    # Extract latest values
    latest = df.iloc[-1].to_dict()
    prev = df.iloc[-2].to_dict() if len(df) > 1 else latest
    
    current_price = latest.get('close', 0)
    
    # helper for safe float conversion
    def sf(val):
        if pd.isna(val) or np.isinf(val): return 0.0
        return float(val)

    # Signal Evaluation Logic
    signals = []
    
    # 1. SMAs
    sma20 = sf(latest.get('SMA_20'))
    sma50 = sf(latest.get('SMA_50'))
    sma200 = sf(latest.get('SMA_200'))
    
    sma_sig = "NEUTRAL"
    if current_price > sma20 and sma20 > sma50:
        sma_sig = "BUY"
    elif current_price < sma20 and sma20 < sma50:
        sma_sig = "SELL"
    signals.append(sma_sig)
    
    # 2. MACD
    macd_line = sf(latest.get('MACD_12_26_9'))
    macd_sig = sf(latest.get('MACDs_12_26_9'))
    macd_hist = sf(latest.get('MACDh_12_26_9'))
    prev_macd_hist = sf(prev.get('MACDh_12_26_9'))
    
    macd_decision = "NEUTRAL"
    if macd_line > macd_sig and macd_hist > prev_macd_hist:
        macd_decision = "BUY"
    elif macd_line < macd_sig and macd_hist < prev_macd_hist:
        macd_decision = "SELL"
    signals.append(macd_decision)
    
    # 3. RSI
    rsi_val = sf(latest.get('RSI_14'))
    rsi_sig = "NEUTRAL"
    if rsi_val > 70:
        rsi_sig = "SELL" # Overbought
    elif rsi_val < 30:
        rsi_sig = "BUY"  # Oversold
    elif rsi_val > 50:
        rsi_sig = "BUY" # Bullish territory
    else:
        rsi_sig = "SELL" # Bearish territory
    signals.append(rsi_sig)
    
    # 4. Bollinger Bands
    bbu = sf(latest.get('BBU_20_2.0'))
    bbl = sf(latest.get('BBL_20_2.0'))
    bb_sig = "NEUTRAL"
    if current_price > bbu:
        bb_sig = "SELL" # Overbought
    elif current_price < bbl:
        bb_sig = "BUY"  # Oversold
    signals.append(bb_sig)
    
    # 5. Stochastic
    stoch_k = sf(latest.get('STOCHk_14_3_3'))
    stoch_d = sf(latest.get('STOCHd_14_3_3'))
    stoch_sig = "NEUTRAL"
    if stoch_k < 20 and stoch_d < 20 and stoch_k > stoch_d:
        stoch_sig = "BUY"
    elif stoch_k > 80 and stoch_d > 80 and stoch_k < stoch_d:
        stoch_sig = "SELL"
    signals.append(stoch_sig)

    # 6. ADX
    adx_val = sf(latest.get('ADX_14'))
    dmp = sf(latest.get('DMP_14'))
    dmn = sf(latest.get('DMN_14'))
    adx_sig = "NEUTRAL"
    if adx_val > 25:
        if dmp > dmn: adx_sig = "BUY"
        else: adx_sig = "SELL"
    signals.append(adx_sig)

    # 7. CCI
    cci_val = sf(latest.get('CCI_14_0.015'))
    cci_sig = "NEUTRAL"
    if cci_val < -100: cci_sig = "BUY"
    elif cci_val > 100: cci_sig = "SELL"
    signals.append(cci_sig)
    
    # 8. MFI
    mfi_val = sf(latest.get('MFI_14'))
    mfi_sig = "NEUTRAL"
    if mfi_val < 20: mfi_sig = "BUY"
    elif mfi_val > 80: mfi_sig = "SELL"
    signals.append(mfi_sig)
    
    # Calculate Summary Score
    buy_count = signals.count("BUY")
    sell_count = signals.count("SELL")
    neutral_count = signals.count("NEUTRAL")
    total_signals = len(signals)
    
    score = (buy_count - sell_count) / total_signals if total_signals > 0 else 0
    overall_signal = "NEUTRAL"
    if score > 0.3: overall_signal = "STRONG BUY"
    elif score > 0.1: overall_signal = "BUY"
    elif score < -0.3: overall_signal = "STRONG SELL"
    elif score < -0.1: overall_signal = "SELL"

    return {
        "ticker": ticker,
        "current_price": current_price * 1000,
        "summary": {
            "overall_signal": overall_signal,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "neutral_count": neutral_count,
            "score": sf(score)
        },
        "trend": {
            "SMA20": sf(sma20 * 1000),
            "SMA50": sf(sma50 * 1000),
            "SMA200": sf(sma200 * 1000),
            "EMA20": sf(latest.get('EMA_20', 0) * 1000),
            "MACD": {"line": sf(macd_line), "signal": sf(macd_sig), "hist": sf(macd_hist)},
            "ADX": sf(adx_val)
        },
        "oscillators": {
            "RSI": sf(rsi_val),
            "Stochastic": {"k": sf(stoch_k), "d": sf(stoch_d)},
            "CCI": sf(cci_val),
            "WilliamsR": sf(latest.get('WILLR_14', 0))
        },
        "volatility": {
            "BollingerBands": {"upper": sf(bbu * 1000), "middle": sf(latest.get('BBM_20_2.0', 0) * 1000), "lower": sf(bbl * 1000)}
        },
        "volume": {
            "OBV": sf(latest.get('OBV', 0)),
            "MFI": sf(mfi_val)
        }
    }

