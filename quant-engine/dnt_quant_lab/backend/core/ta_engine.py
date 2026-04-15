import pandas as pd
import pandas_ta_classic as ta
import numpy as np

def compute_full_ta(df: pd.DataFrame, ticker: str = "") -> dict:
    """
    Computes comprehensive technical analysis indicators matching Fireant's detailed TA screen.
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
    
    try:
        # Moving Averages
        for length in [5, 10, 20, 50, 100, 200]:
            df.ta.sma(length=length, append=True)
            df.ta.ema(length=length, append=True)
        
        # Technical Indicators
        df.ta.rsi(length=14, append=True)
        df.ta.stoch(append=True) # STOCHk_14_3_3, STOCHd
        df.ta.stochrsi(length=14, append=True) # STOCHRSI
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.willr(length=14, append=True)
        df.ta.cci(length=14, append=True)
        df.ta.ao(fast=5, slow=34, append=True)
        df.ta.roc(length=14, append=True)
        df.ta.mfi(length=14, append=True)
    except Exception as e:
        return {"ticker": ticker, "error": f"TA computation failed: {str(e)}"}

    latest = df.iloc[-1].to_dict()
    prev1 = df.iloc[-2].to_dict() if len(df) > 1 else latest
    
    current_price = latest.get('close', 0.0)
    
    def sf(val):
        if pd.isna(val) or np.isinf(val): return 0.0
        return float(val)

    def get_col(prefix):
        for k, v in latest.items():
            if k.startswith(prefix):
                return sf(v)
        return 0.0

    # 1. Moving Averages
    ma_buy = 0
    ma_sell = 0
    ma_list = []
    
    for length in [5, 10, 20, 50, 100, 200]:
        sma_val = get_col(f'SMA_{length}')
        ema_val = get_col(f'EMA_{length}')
        
        sma_action = "Mua" if current_price > sma_val else "Bán"
        ema_action = "Mua" if current_price > ema_val else "Bán"
        
        if sma_action == "Mua": ma_buy += 1
        else: ma_sell += 1
        
        if ema_action == "Mua": ma_buy += 1
        else: ma_sell += 1
        
        ma_list.append({
            "name": f"MA{length}",
            "sma_val": sma_val * 1000 if sma_val > 0 else 0,
            "sma_action": sma_action if sma_val > 0 else "--",
            "ema_val": ema_val * 1000 if ema_val > 0 else 0,
            "ema_action": ema_action if ema_val > 0 else "--"
        })
        
    ma_summary = "MUA MẠNH" if ma_buy >= 10 else "MUA" if ma_buy > ma_sell else "BÁN MẠNH" if ma_sell >= 10 else "BÁN"
    if ma_buy == ma_sell: ma_summary = "TRUNG TÍNH"

    # 2. Oscillators / Technical Indicators
    ind_buy = 0
    ind_sell = 0
    ind_neutral = 0
    indicators_list = []
    
    # RSI
    rsi = get_col('RSI')
    rsi_action = "Mua" if 30 < rsi < 70 else "Quá bán" if rsi <= 30 else "Quá mua"
    if rsi_action in ["Mua", "Quá bán"]: ind_buy += 1
    else: ind_sell += 1
    indicators_list.append({"name": "RSI(14)", "value": rsi, "action": rsi_action})
    
    # Stochastic
    stoch = get_col('STOCHk')
    stoch_action = "Mua" if 20 < stoch < 80 else "Quá bán" if stoch <= 20 else "Quá mua"
    if stoch_action in ["Mua", "Quá bán"]: ind_buy += 1
    else: ind_sell += 1
    indicators_list.append({"name": "Stochastic(14, 3)", "value": stoch, "action": stoch_action})
    
    # Stochastic RSI
    stochrsi = get_col('STOCHRSIk')
    stochrsi_action = "Mua" if 20 < stochrsi < 80 else "Quá bán" if stochrsi <= 20 else "Quá mua"
    if stochrsi_action in ["Mua", "Quá bán"]: ind_buy += 1
    else: ind_sell += 1
    indicators_list.append({"name": "Stochastic RSI(14)", "value": stochrsi, "action": stochrsi_action})
    
    # MACD
    macd = get_col('MACD_')
    macd_sig = get_col('MACDs_')
    macd_action = "Mua" if macd > macd_sig else "Bán"
    if macd_action == "Mua": ind_buy += 1
    else: ind_sell += 1
    indicators_list.append({"name": "MACD(12, 26)", "value": macd, "action": macd_action})
    
    # William %R
    willr = get_col('WILLR')
    willr_action = "Mua" if -80 < willr < -20 else "Quá bán" if willr <= -80 else "Quá mua"
    if willr_action in ["Mua", "Quá bán"]: ind_buy += 1
    else: ind_sell += 1
    indicators_list.append({"name": "WilliamR(14)", "value": willr, "action": willr_action})
    
    # CCI
    cci = get_col('CCI')
    cci_action = "Mua" if cci < -100 else "Bán" if cci > 100 else "Trung tính"
    if cci_action == "Mua": ind_buy += 1
    elif cci_action == "Bán": ind_sell += 1
    else: ind_neutral += 1
    indicators_list.append({"name": "CCI(14)", "value": cci, "action": cci_action})
    
    # Awesome Oscillator
    ao = get_col('AO')
    ao_action = "Mua" if ao > 0 else "Bán"
    if ao_action == "Mua": ind_buy += 1
    else: ind_sell += 1
    indicators_list.append({"name": "Awesome Oscillator(5, 34)", "value": ao, "action": ao_action})
    
    # ROC
    roc = get_col('ROC')
    roc_action = "Mua" if roc > 0 else "Bán"
    if roc_action == "Mua": ind_buy += 1
    else: ind_sell += 1
    indicators_list.append({"name": "ROC(14)", "value": roc, "action": roc_action})
    
    # MFI
    mfi = get_col('MFI')
    mfi_action = "Mua" if 20 < mfi < 80 else "Quá bán" if mfi <= 20 else "Quá mua"
    if mfi_action in ["Mua", "Quá bán"]: ind_buy += 1
    else: ind_sell += 1
    indicators_list.append({"name": "MFI(14)", "value": mfi, "action": mfi_action})
    
    ind_summary = "MUA MẠNH" if ind_buy >= 6 else "MUA" if ind_buy > ind_sell else "BÁN MẠNH" if ind_sell >= 6 else "BÁN"
    if ind_buy == ind_sell: ind_summary = "TRUNG TÍNH"
    
    # Overall summary logic mapping to EN for backend compatibility
    total_buy = ma_buy + ind_buy
    total_sell = ma_sell + ind_sell
    total_neutral = ind_neutral
    
    overall_signal = "STRONG BUY" if total_buy >= 14 else "BUY" if total_buy > total_sell else "STRONG SELL" if total_sell >= 14 else "SELL"
    if total_buy == total_sell: overall_signal = "NEUTRAL"
    score = (total_buy - total_sell) / (total_buy + total_sell + total_neutral) if (total_buy + total_sell + total_neutral) > 0 else 0
    overall_vi = "MUA MẠNH" if total_buy >= 14 else "MUA" if total_buy > total_sell else "BÁN MẠNH" if total_sell >= 14 else "BÁN"
    if total_buy == total_sell: overall_vi = "TRUNG TÍNH"

    # 3. Pivot Points
    high = prev1.get('high', 0.0)
    low = prev1.get('low', 0.0)
    close = prev1.get('close', 0.0)
    open_p = prev1.get('open', 0.0)
    
    H = sf(high) * 1000
    L = sf(low) * 1000
    C = sf(close) * 1000
    O = sf(open_p) * 1000
    
    pivot_points = []
    
    # Classic
    PP = (H + L + C) / 3
    pivot_points.append({
        "name": "Classic",
        "S3": PP - 2 * (H - L),
        "S2": PP - (H - L),
        "S1": (PP * 2) - H,
        "Points": PP,
        "R1": (PP * 2) - L,
        "R2": PP + (H - L),
        "R3": PP + 2 * (H - L)
    })
    
    # Fibonacci
    pivot_points.append({
        "name": "Fibonacci",
        "S3": PP - 1.000 * (H - L),
        "S2": PP - 0.618 * (H - L),
        "S1": PP - 0.382 * (H - L),
        "Points": PP,
        "R1": PP + 0.382 * (H - L),
        "R2": PP + 0.618 * (H - L),
        "R3": PP + 1.000 * (H - L)
    })
    
    # Camarilla
    pivot_points.append({
        "name": "Camarilla",
        "S3": C - (H - L) * 1.1 / 4,
        "S2": C - (H - L) * 1.1 / 6,
        "S1": C - (H - L) * 1.1 / 12,
        "Points": C,
        "R1": C + (H - L) * 1.1 / 12,
        "R2": C + (H - L) * 1.1 / 6,
        "R3": C + (H - L) * 1.1 / 4
    })
    
    # Woodie
    PP_wood = (H + L + 2 * C) / 4
    pivot_points.append({
        "name": "Woodie",
        "S3": L - 2 * (H - PP_wood),
        "S2": PP_wood - (H - L),
        "S1": (PP_wood * 2) - H,
        "Points": PP_wood,
        "R1": (PP_wood * 2) - L,
        "R2": PP_wood + (H - L),
        "R3": H + 2 * (PP_wood - L)
    })
    
    # DeMark
    if C < O: X = H + 2 * L + C
    elif C > O: X = 2 * H + L + C
    else: X = H + L + 2 * C
    PP_demark = X / 4
    pivot_points.append({
        "name": "DeMark",
        "S3": 0,
        "S2": 0,
        "S1": X / 2 - H,
        "Points": PP_demark,
        "R1": X / 2 - L,
        "R2": 0,
        "R3": 0
    })

    return {
        "ticker": ticker,
        "current_price": current_price * 1000,
        "summary": {
            "overall_signal": overall_signal, 
            "overall_vi": overall_vi, # UI display string 
            "overall_buy": total_buy,
            "overall_sell": total_sell,
            "ma_signal": ma_summary,
            "ma_buy": ma_buy,
            "ma_sell": ma_sell,
            "ind_signal": ind_summary,
            "ind_buy": ind_buy,
            "ind_sell": ind_sell,
            "ind_neutral": ind_neutral,
            "score": sf(score)
        },
        "moving_averages": ma_list,
        "technical_indicators": indicators_list,
        "pivot_points": pivot_points
    }
