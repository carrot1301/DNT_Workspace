"""
Multi-Factor Model cho thị trường Việt Nam
==========================================
Sử dụng 100% dữ liệu giá (Entrade OHLCV) — không phụ thuộc TCBS API.

3 Factor:
1. Momentum (6-month return, skip last 1 month) — Weight: 40%
2. Low-Volatility (inverse of annualized vol) — Weight: 30%  
3. Trend (Price vs SMA200 distance) — Weight: 30%

Output: Dict {ticker: factor_score} dùng làm Views cho Black-Litterman
hoặc adjust expected returns trong MVO.
"""

import numpy as np
import pandas as pd
from core.data_engine import fetch_stock_data


# ═══════════════════════════════════════════════════
# FACTOR WEIGHTS (có thể tune)
# ═══════════════════════════════════════════════════
FACTOR_WEIGHTS = {
    'momentum': 0.40,
    'low_volatility': 0.30,
    'trend': 0.30
}

# Scale factor: composite score sẽ được nhân với hệ số này
# để chuyển thành expected return adjustment (alpha)
# VD: score = 1.0 (top) → alpha = +3%, score = -1.0 (bottom) → alpha = -3%
# Expert consensus: 0.02-0.05 cho thị trường VN (emerging market).
# Giá trị quá lớn → BL override equilibrium, quá nhỏ → views bị bỏ qua.
ALPHA_SCALE = 0.03


def compute_momentum_score(prices: pd.Series) -> float:
    """
    Momentum Factor: Lợi nhuận 6 tháng gần nhất, bỏ qua 1 tháng cuối.
    
    Công thức: R_{t-126, t-21} = P(t-21) / P(t-126) - 1
    
    Bỏ tháng cuối cùng vì hiệu ứng Short-Term Reversal (Jegadeesh & Titman, 1993).
    """
    if len(prices) < 130:
        return 0.0
    
    # 126 trading days ≈ 6 months, 21 trading days ≈ 1 month
    price_6m_ago = prices.iloc[-126]
    price_1m_ago = prices.iloc[-21]
    
    if price_6m_ago <= 0:
        return 0.0
    
    return (price_1m_ago / price_6m_ago) - 1.0


def compute_volatility_score(log_returns: pd.Series) -> float:
    """
    Low-Volatility Factor: Inverse of annualized volatility.
    
    Công thức: σ_annual = σ_daily × √252
    Score = -σ_annual (âm vì volatility thấp = tốt)
    
    Low-volatility anomaly: cổ phiếu ít biến động thường có risk-adjusted return
    tốt hơn cổ phiếu biến động cao (Baker, Bradley & Wurgler, 2011).
    """
    if len(log_returns) < 60:
        return 0.0
    
    # Dùng 63 ngày gần nhất (3 tháng) cho volatility estimate gần nhất
    recent_returns = log_returns.tail(63)
    daily_vol = recent_returns.std()
    annual_vol = daily_vol * np.sqrt(252)
    
    # Trả về âm vì vol thấp = điểm cao
    return -annual_vol


def compute_trend_score(prices: pd.Series) -> float:
    """
    Trend Factor: Khoảng cách tương đối giữa giá hiện tại và SMA200.
    
    Công thức: Trend = (P_current - SMA200) / SMA200
    
    Dương = uptrend, Âm = downtrend.
    Trend following dựa trên lý thuyết momentum dài hạn
    (Moskowitz, Ooi & Pedersen, 2012).
    """
    if len(prices) < 200:
        return 0.0
    
    current_price = prices.iloc[-1]
    sma200 = prices.tail(200).mean()
    
    if sma200 <= 0:
        return 0.0
    
    return (current_price - sma200) / sma200


def zscore_normalize(scores: dict) -> dict:
    """
    Z-score normalization: chuyển raw scores về phân phối chuẩn (mean=0, std=1).
    
    Công thức: z_i = (x_i - μ) / σ
    
    Clip tại ±3σ để giảm outlier impact.
    """
    if not scores or len(scores) < 2:
        return {k: 0.0 for k in scores}
    
    values = np.array(list(scores.values()))
    mean = np.mean(values)
    std = np.std(values)
    
    if std < 1e-10:
        return {k: 0.0 for k in scores}
    
    return {k: np.clip((v - mean) / std, -3.0, 3.0) for k, v in scores.items()}


def compute_factor_scores(tickers: list, returns_df: pd.DataFrame = None) -> dict:
    """
    Tính Composite Factor Score cho từng ticker.
    
    Pipeline:
    1. Fetch price data cho mỗi mã
    2. Tính raw score cho 3 factor
    3. Z-score normalize mỗi factor
    4. Composite = weighted sum of z-scores
    
    Parameters:
        tickers: List mã cổ phiếu
        returns_df: DataFrame log returns (optional, dùng lại nếu đã fetch)
    
    Returns:
        Dict {ticker: composite_score} — score ∈ [-3, 3]
    """
    if len(tickers) < 2:
        return {t: 0.0 for t in tickers}
    
    raw_momentum = {}
    raw_volatility = {}
    raw_trend = {}
    
    for ticker in tickers:
        df = fetch_stock_data(ticker, days_back=300)
        if df.empty or len(df) < 60:
            raw_momentum[ticker] = 0.0
            raw_volatility[ticker] = 0.0
            raw_trend[ticker] = 0.0
            continue
        
        prices = df['close']
        log_ret = np.log(prices / prices.shift(1)).dropna()
        
        raw_momentum[ticker] = compute_momentum_score(prices)
        raw_volatility[ticker] = compute_volatility_score(log_ret)
        raw_trend[ticker] = compute_trend_score(prices)
    
    # Z-score normalize từng factor riêng
    z_momentum = zscore_normalize(raw_momentum)
    z_volatility = zscore_normalize(raw_volatility)
    z_trend = zscore_normalize(raw_trend)
    
    # Composite score = weighted sum
    composite = {}
    for t in tickers:
        score = (
            FACTOR_WEIGHTS['momentum'] * z_momentum.get(t, 0) +
            FACTOR_WEIGHTS['low_volatility'] * z_volatility.get(t, 0) +
            FACTOR_WEIGHTS['trend'] * z_trend.get(t, 0)
        )
        composite[t] = score
    
    return composite


def factor_scores_to_alpha(composite_scores: dict) -> dict:
    """
    Chuyển composite scores thành alpha adjustments cho expected returns.
    
    Công thức: α_i = score_i × ALPHA_SCALE
    
    VD: ALPHA_SCALE = 0.06
    - Score = +1.5 → α = +9% (tăng expected return 9%)
    - Score = -1.0 → α = -6% (giảm expected return 6%)
    """
    return {t: score * ALPHA_SCALE for t, score in composite_scores.items()}


def build_factor_views(tickers: list, alpha_dict: dict):
    """
    Chuyển alpha adjustments thành P, Q matrices cho Black-Litterman.
    
    P matrix: Identity matrix (absolute views cho từng asset)
    Q vector: Alpha values
    
    Chỉ tạo views cho các mã có alpha đáng kể (|α| > 0.5%).
    """
    views = {t: alpha_dict[t] for t in tickers if t in alpha_dict and abs(alpha_dict[t]) > 0.005}
    
    if not views:
        return None, None
    
    num_assets = len(tickers)
    num_views = len(views)
    P = np.zeros((num_views, num_assets))
    Q = np.zeros(num_views)
    
    for i, (ticker, alpha) in enumerate(views.items()):
        if ticker in tickers:
            asset_idx = tickers.index(ticker)
            P[i, asset_idx] = 1.0
            Q[i] = alpha
    
    return P, Q


def compute_dynamic_bounds(tickers: list, user_min: float = 0.05, user_max: float = 0.40) -> dict:
    """
    Dynamic Bounds: Tính ràng buộc trọng số TRƯỚC KHI đưa vào optimizer.
    
    [Expert Fix] Thay vì overlay SAU optimization (phá solution tối ưu),
    đưa trend constraint VÀO optimizer thông qua dynamic bounds.
    
    Logic:
    - Uptrend (Price > SMA50 > SMA200): max = user_max (giữ nguyên)
    - Mild downtrend (SMA200 ≤ Price < SMA50): max = min(user_max, 0.25)
    - Strong downtrend (Price < SMA200): max = min(user_max, 0.10)
    
    Kết quả: Optimizer giải bài toán với constraint chính xác → solution vẫn tối ưu.
    
    Dựa trên: "Time Series Momentum" (Moskowitz, Ooi & Pedersen, AQR, 2012)
    
    Returns:
        Dict {ticker: (min_bound, max_bound)}
    """
    bounds = {}
    
    for ticker in tickers:
        df = fetch_stock_data(ticker, days_back=250)
        if df.empty or len(df) < 200:
            bounds[ticker] = (user_min, user_max)
            continue
        
        prices = df['close']
        current = prices.iloc[-1]
        sma50 = prices.tail(50).mean()
        sma200 = prices.tail(200).mean()
        
        if current < sma200:
            # Strong downtrend: cap tại 10%
            effective_max = min(user_max, 0.10)
        elif current < sma50:
            # Mild downtrend: cap tại 25%
            effective_max = min(user_max, 0.25)
        else:
            # Uptrend: giữ nguyên user setting
            effective_max = user_max
        
        # Đảm bảo min <= max
        effective_min = min(user_min, effective_max)
        bounds[ticker] = (effective_min, effective_max)
    
    return bounds
