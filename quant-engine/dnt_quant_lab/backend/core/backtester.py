import pandas as pd

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
