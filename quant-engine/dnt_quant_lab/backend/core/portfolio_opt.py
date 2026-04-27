import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf
from core.factor_model import compute_factor_scores, factor_scores_to_alpha, build_factor_views, compute_trend_overlay

class BlackLittermanOptimizer:
    """
    [Tác Vụ Mô Hình Hóa] Black-Litterman Model
    Mô hình tích hợp kỳ vọng chủ quan (Views) vào Implied Equilibrium Returns.
    """
    def __init__(self, risk_aversion: float = 2.5, tau: float = 0.05):
        self.risk_aversion = risk_aversion
        self.tau = tau
        
    def implied_returns(self, cov_matrix: pd.DataFrame, weights: np.ndarray) -> pd.Series:
        """Tính Prior: Implied Equilibrium Returns (Equally Weighted nếu không có Market Cap)"""
        return pd.Series(self.risk_aversion * np.dot(cov_matrix.values, weights), index=cov_matrix.columns)
        
    def optimize(self, cov_matrix: pd.DataFrame, implied_returns: pd.Series, 
                 P: np.ndarray = None, Q: np.ndarray = None, omega: np.ndarray = None):
        """Toán học Black-Litterman Bayersian Equation"""
        if P is None or Q is None or len(P) == 0:
            return implied_returns
            
        Sigma = cov_matrix.values
        Pi = implied_returns.values
        
        # Rủi ro views (omega), mặc định nội suy từ P và Sigma nếu chưa truyền
        if omega is None:
            omega = np.diag(np.diag(np.dot(np.dot(P, self.tau * Sigma), P.T)))
        elif len(omega.shape) == 1:
            omega = np.diag(omega)
                
        try:
            tau_sigma_inv = np.linalg.inv(self.tau * Sigma)
            omega_inv = np.linalg.inv(omega)
            
            # [ (tau*Sigma)^-1 + P^T * Omega^-1 * P ]^-1
            part1 = np.linalg.inv(tau_sigma_inv + np.dot(np.dot(P.T, omega_inv), P))
            # [ (tau*Sigma)^-1 * Pi + P^T * Omega^-1 * Q ]
            part2 = np.dot(tau_sigma_inv, Pi) + np.dot(np.dot(P.T, omega_inv), Q)
            
            posterior_expected_returns = np.dot(part1, part2)
            return pd.Series(posterior_expected_returns, index=cov_matrix.columns)
        except np.linalg.LinAlgError:
            return implied_returns

def generate_ftse_views(tickers: list, timeframe_days: int) -> dict:
    """Sinh Ma trận Views cho sự kiện nâng hạng FTSE (T9/2026 tới T9/2027)"""
    # Xử lý list thụ hưởng user nhập:
    FTSE_BENEFICIARIES = ['VIC', 'VHM', 'HPG', 'FPT', 'SSI', 'MSN', 'VCB', 'VNM', 'VJC', 'VIX', 'STB', 'VRE', 'SHB', 'GEX', 'VCI', 'KDH', 'KBC', 'BID', 'NVL', 'DGC', 'EIB', 'PDR', 'DXG', 'DIG', 'DPM']
    
    # Sốc Alpha Kỳ vọng — giảm xuống để BL không bias quá mạnh
    alpha_bump = 0.02
    if timeframe_days >= 126:
        alpha_bump = 0.03
    if timeframe_days >= 252:
        alpha_bump = 0.05

    views = {}
    for t in tickers:
        if t in FTSE_BENEFICIARIES:
            views[t] = alpha_bump
    return views

def build_views_matrices(tickers: list, views_dict: dict):
    if not dict or len(views_dict) == 0:
        return None, None
    num_assets = len(tickers)
    num_views = len(views_dict)
    P = np.zeros((num_views, num_assets))
    Q = np.zeros(num_views)
    for i, (ticker, excess_return) in enumerate(views_dict.items()):
        if ticker in tickers:
            asset_idx = tickers.index(ticker)
            P[i, asset_idx] = 1.0 # View tuyệt đối
            Q[i] = excess_return
    return P, Q
def run_monte_carlo(returns_df: pd.DataFrame, num_portfolios: int = 10000, initial_capital: float = 1000000, trading_days: int = 252, apply_ftse_event: bool = True, min_weight: float = 0.05, max_weight: float = 0.40) -> dict:
    """
    Sinh Monte Carlo: Tối ưu hoá Danh mục đầu tư.
    Tích hợp mô hình Black-Litterman và Rà soát sự kiện Nâng hạng FTSE.
    """
    num_assets = len(returns_df.columns)
    points = np.zeros((num_portfolios, 3)) # Return, Volatility, Sharpe
    weights_record = np.zeros((num_portfolios, num_assets))
    
    # Scale returns and covariance to the specific timeframe (e.g. 63 days for 3 months)
    mean_returns = returns_df.mean() * trading_days
    
    # [Tác Vụ 2.2] Covariance Shrinkage với Ledoit-Wolf
    cov_matrix_daily = LedoitWolf().fit(returns_df).covariance_
    cov_matrix = pd.DataFrame(cov_matrix_daily, index=returns_df.columns, columns=returns_df.columns) * trading_days
    daily_variances = np.diag(cov_matrix_daily)  # Giữ daily variance cho variance drag
    
    # -----------------------------------------------------------------
    # Nâng cấp thuật toán Hướng sự kiện: BLACK-LITTERMAN (Mô hình BL)
    # -----------------------------------------------------------------
    bl_p_matrix_out = []
    bl_q_vector_out = []
    is_bl_active = False
    
    if apply_ftse_event:
        tickers_list = list(returns_df.columns)
        eq_weights = np.ones(len(tickers_list)) / len(tickers_list)
        bl_optimizer = BlackLittermanOptimizer()
        implied_ret = bl_optimizer.implied_returns(cov_matrix, eq_weights)
        
        # 1. Multi-Factor Views
        composite_scores = compute_factor_scores(tickers_list)
        alpha_dict = factor_scores_to_alpha(composite_scores)
        
        # 2. FTSE Event Views (Optional overlay)
        ftse_views = generate_ftse_views(tickers_list, trading_days)
        if ftse_views:
            for t, alpha in ftse_views.items():
                alpha_dict[t] = alpha_dict.get(t, 0) + alpha
                
        if alpha_dict:
            P, Q = build_factor_views(tickers_list, alpha_dict)
            if P is not None and Q is not None:
                bl_p_matrix_out = P.tolist()
                bl_q_vector_out = Q.tolist()
                post_ret = bl_optimizer.optimize(cov_matrix, implied_ret, P, Q)
                
                # [FIX] Variance Drag: dùng daily variance * trading_days / 2
                # thay vì annualized variance / 2 (gây penalty quá lớn 4-8%)
                expected_returns = post_ret.values - (daily_variances * trading_days / 2)
                is_bl_active = True
                
    # Fallback to Markowitz Lịch sử nếu không kích hoạt hoặc rỗng View
    if not is_bl_active:
        expected_returns = mean_returns - (daily_variances * trading_days / 2)
    
    # Scale risk-free rate based on the timeframe (assume 3% annually)
    risk_free_rate = 0.03 * (trading_days / 252)
    
    # Sinh trọng số ngẫu nhiên
    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        
        port_return = np.sum(expected_returns * weights)
        port_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        port_volatility = np.sqrt(port_variance)
        
        sharpe = (port_return - risk_free_rate) / port_volatility 
        
        points[i, :] = [port_return, port_volatility, sharpe]
        weights_record[i, :] = weights
        
    # [Tác Vụ 2.1] Sử dụng scipy.optimize.minimize để tìm Max Sharpe với Ràng buộc (Bounds)
    def negative_sharpe(weights):
        port_return = np.sum(expected_returns * weights)
        port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (port_return - risk_free_rate) / port_volatility
        return -sharpe_ratio

    # Ràng buộc: Tổng tỉ trọng = 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    # Ràng buộc: Theo thông số từ UI
    bounds = tuple((min_weight, max_weight) for _ in range(num_assets))
    
    # Khởi tạo điểm bắt đầu (equal weights)
    init_guess = np.array(num_assets * [1. / num_assets])
    
    optimized_result = minimize(negative_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    ms_weights = optimized_result.x
    
    # -----------------------------------------------------------------
    # TREND FOLLOWING OVERLAY
    # -----------------------------------------------------------------
    raw_weights_dict = dict(zip(returns_df.columns, ms_weights))
    adjusted_weights_dict = compute_trend_overlay(list(returns_df.columns), raw_weights_dict)
    ms_weights = np.array([adjusted_weights_dict[t] for t in returns_df.columns])
    
    ms_return = np.sum(expected_returns * ms_weights)
    ms_volatil = np.sqrt(np.dot(ms_weights.T, np.dot(cov_matrix, ms_weights)))
    ms_sharpe = (ms_return - risk_free_rate) / ms_volatil
    
    # -- TÍNH KHOẢNG XÁC SUẤT 95% (CONFIDENCE INTERVAL) --
    # Khảo sát Return theo danh mục Max Sharpe với phân phối chuẩn
    # [BẢN SỬA LỖI] Sử dụng Arithmetic Standard Deviation cho CI
    lower_bound_return = ms_return - (1.96 * ms_volatil)
    upper_bound_return = ms_return + (1.96 * ms_volatil)
    
    # 5% sụt giảm tồi tệ nhất (Value at Risk - VaR 95%) 
    # [BẢN SỬA LỖI] VaR nên được tính là mức sụt giảm tệ nhất theo độ lệch chuẩn
    # (Nếu Expected Return dương lớn, VaR có thể vẫn dương, nhưng chúng ta 
    # muốn thể hiện phần rủi ro thực sự mất mát)
    var_95_percent = ms_return - (1.645 * ms_volatil)
    
    # Tính ra số tiền thực tế
    lower_bound_val = initial_capital * (1 + lower_bound_return)
    upper_bound_val = initial_capital * (1 + upper_bound_return)
    expected_val = initial_capital * (1 + ms_return)
    
    # [BẢN SỬA LỖI] VaR: Thể hiện số tiền rủi ro có thể mất (Relative Loss)
    # Chúng ta lấy mức tổn thất so với giá trị kỳ vọng HOẶC vốn gốc. 
    # Ở Việt Nam thường so với Vốn gốc. Nếu tệ nhất vẫn lời thì VaR VND = 0 (Rủi ro mất tiền là 0)
    var_95_worst_value = initial_capital * (1 + var_95_percent)
    var_95_value = min(0, var_95_worst_value - initial_capital)
    
    return {
        'max_sharpe': {
            'expected_return': ms_return,
            'volatility': ms_volatil,
            'sharpe': ms_sharpe,
            'weights': dict(zip(returns_df.columns, ms_weights)),
            'ci_95_lower': lower_bound_return,
            'ci_95_upper': upper_bound_return,
            'var_95_percent': var_95_percent,
        },
        'monetary_values': {
            'initial_capital': initial_capital,
            'expected_value': expected_val,
            'ci_lower_value': lower_bound_val,
            'ci_upper_value': upper_bound_val,
            'var_value_loss': var_95_value
        },
        'timeframe_days': trading_days,
        'frontier_points_x': points[:, 1].tolist(),
        'frontier_points_y': points[:, 0].tolist(),
        'frontier_points_c': points[:, 2].tolist(),
        'black_litterman_event': {
            'is_active': is_bl_active,
            'P_matrix': bl_p_matrix_out,
            'Q_vector': bl_q_vector_out
        }
    }

def calculate_stress_test(port_returns: pd.DataFrame, market_returns: pd.Series, weights_dict: dict, initial_capital: float, crash_percent: float = -0.05) -> dict:
    """
    Tính năng Stress Test: VN-Index sập mạnh, tài khoản bốc hơi bao nhiêu?
    Sử dụng Beta để ước tính mức độ sụt giảm so với thị trường.
    """
    tickers = list(weights_dict.keys())
    port_ret_selected = port_returns[tickers]
    weights = np.array([weights_dict[t] for t in tickers])
    
    portfolio_beta = 0
    betas = {}
    
    # Tính Beta cho từng cổ phiếu
    if len(market_returns) > 0:
        cov_matrix_with_market = port_ret_selected.apply(lambda x: x.cov(market_returns))
        market_var = market_returns.var()
        if market_var > 0:
            betas = (cov_matrix_with_market / market_var).to_dict()
        else:
            betas = {t: 1.0 for t in tickers}
    else:
        # Giả định Beta = 1 nếu không có dữ liệu Market
        betas = {t: 1.0 for t in tickers}
        
    # Tính Beta tổng của danh mục
    for t in tickers:
        portfolio_beta += betas[t] * weights_dict[t]
        
    # Mô phỏng thiệt hại trong kịch bản sập
    estimated_drop_percent = portfolio_beta * crash_percent
    estimated_loss_value = initial_capital * estimated_drop_percent
    final_capital = initial_capital + estimated_loss_value
    
    return {
        'portfolio_beta': portfolio_beta,
        'simulated_market_crash': crash_percent,
        'estimated_portfolio_drop': estimated_drop_percent,
        'estimated_loss_vnd': estimated_loss_value,
        'capital_after_crash': final_capital
    }

def evaluate_custom_portfolio(returns_df: pd.DataFrame, weights_dict: dict, initial_capital: float, trading_days: int = 63) -> dict:
    """
    Tính năng Đánh Giá Danh Mục Cá Nhân (Evaluator).
    Tính dải mức lợi nhuận và Rủi ro cho một mốc thời gian cố định ở tương lai.
    (Ví dụ 3 tháng = ~63 ngày giao dịch).
    """
    tickers = list(weights_dict.keys())
    port_ret_selected = returns_df[tickers]
    weights = np.array([weights_dict[t] for t in tickers])
    
    # Tính lợi nhuận và Biến động theo NGÀY
    daily_mean_returns = port_ret_selected.mean()
    # Sử dụng LedoitWolf Shrinkage cho Evaluator (Tác vụ 2.2)
    daily_cov_matrix_np = LedoitWolf().fit(port_ret_selected).covariance_
    daily_cov_matrix = pd.DataFrame(daily_cov_matrix_np, index=port_ret_selected.columns, columns=port_ret_selected.columns)
    
    # [Tác Vụ 2.1] Điều chỉnh lực cản biến động (Variance Drag)
    daily_variances = np.diag(daily_cov_matrix)
    daily_expected_returns = daily_mean_returns - (daily_variances / 2)
    
    port_daily_return = np.sum(daily_expected_returns * weights)
    port_daily_variance = np.dot(weights.T, np.dot(daily_cov_matrix, weights))
    
    # Scale mốc thời gian NGÀY lên THỜI HẠN (trading_days)
    period_return = port_daily_return * trading_days
    period_variance = port_daily_variance * trading_days
    period_volatility = np.sqrt(period_variance)
    
    # Tính Khoảng Xác Suất 95% (Distribution Boundaries)
    lower_bound_return = period_return - (1.96 * period_volatility)
    upper_bound_return = period_return + (1.96 * period_volatility)
    var_95_percent = period_return - (1.645 * period_volatility)
    
    # Tính mốc Suy ra Số Tiền VNĐ
    expected_val = initial_capital * (1 + period_return)
    lower_bound_val = initial_capital * (1 + lower_bound_return)
    upper_bound_val = initial_capital * (1 + upper_bound_return)
    # [BẢN SỬA LỖI] VaR: Thể hiện số tiền rủi ro có thể mất (Relative Loss)
    # Lấy phân vị thứ 5 của phân phối. Nếu kết quả dương (vẫn có lời ở 5%), VaR = 0 (Không mất vốn).
    var_95_worst_value = initial_capital * (1 + var_95_percent)
    var_95_value = min(0, var_95_worst_value - initial_capital)
    
    return {
        'timeframe_days': trading_days,
        'expected_return': period_return,
        'volatility': period_volatility,
        'ci_95_lower': lower_bound_return,
        'ci_95_upper': upper_bound_return,
        'var_95_percent': var_95_percent,
        'monetary_values': {
            'initial_capital': initial_capital,
            'expected_value': expected_val,
            'ci_lower_value': lower_bound_val,
            'ci_upper_value': upper_bound_val,
            'var_value_loss': var_95_value
        }
    }

def calculate_backtest(port_returns: pd.DataFrame, market_returns: pd.Series, weights_dict: dict) -> dict:
    """
    Tính toán Backtest Lịch sử (Khoảng thời gian trong tập dữ liệu).
    Trọng số danh mục được cố định từ đầu kỳ.
    Trả về Dict chứa Chuỗi ngày, Lợi nhuận tích lũy của Danh mục và Thị trường.
    """
    # Lấy các Tickers phù hợp
    tickers = [t for t in weights_dict.keys() if t in port_returns.columns]
    if len(tickers) == 0:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}

    weights = np.array([weights_dict[t] for t in tickers])
    
    # Chuẩn hoá trọng số về 100% trong trường hợp thiếu mã
    if np.sum(weights) == 0:
        return {'dates': [], 'portfolio_cum_returns': [], 'market_cum_returns': []}
    weights = weights / np.sum(weights)
    
    # Tính Lợi nhuận hằng ngày của Danh mục
    port_ret_selected = port_returns[tickers]
    daily_port_returns = port_ret_selected.dot(weights)
    
    # Tính Cumulative Returns (Log Returns → exp(cumsum))
    cum_port = np.exp(daily_port_returns.cumsum()) - 1
    cum_market = np.exp(market_returns.cumsum()) - 1
    
    # Đồng bộ index
    cum_market = cum_market.reindex(cum_port.index).ffill().fillna(0)
    
    # Format lại ngày tháng dạng string để JSON Parse dễ
    dates = [d.strftime("%Y-%m-%d") for d in cum_port.index]
    
    return {
        'dates': dates,
        'portfolio_cum_returns': cum_port.fillna(0).tolist(),
        'market_cum_returns': cum_market.tolist()
    }

# --- ADVANCED QUANT METRICS ---
TRADING_DAYS = 252
RISK_FREE_RATE = 0.03

def compute_max_drawdown(cum_returns: pd.Series):
    running_max = cum_returns.cummax()
    drawdown = (cum_returns - running_max) / running_max
    return drawdown.min(), drawdown

def calculate_advanced_metrics(daily_port_returns: pd.Series, market_returns: pd.Series) -> dict:
    """
    Tính Toán Các Chỉ Số Quant Nâng Cao.
    Đầu vào: Series lợi nhuận hàng ngày của MỘT danh mục (đã gộp tỉ trọng).
    """
    if len(daily_port_returns) == 0:
        return {}
        
    # [BẢN SỬA LỖI] Arithmetic Annualization là chuẩn cho MPT
    # Đã chuyển sang Log Returns trong Data Engine nên sum(mean) * 252 là chuẩn
    ann_return = daily_port_returns.mean() * TRADING_DAYS
    ann_vol = daily_port_returns.std() * np.sqrt(TRADING_DAYS)
    
    # 1. Sortino Ratio
    negative_returns = daily_port_returns[daily_port_returns < 0]
    downside_dev = np.sqrt(np.mean(negative_returns**2)) * np.sqrt(TRADING_DAYS)
    sortino = (ann_return - RISK_FREE_RATE) / downside_dev if downside_dev > 0 else 0.0
    
    # 2. Beta & Treynor Ratio
    beta = 1.0
    r_squared = 0.0
    if len(market_returns) > 0 and market_returns.var() > 0:
        cov_matrix = np.cov(daily_port_returns, market_returns)
        beta = cov_matrix[0, 1] / cov_matrix[1, 1]
        
        corr_matrix = np.corrcoef(daily_port_returns, market_returns)
        if not np.isnan(corr_matrix[0, 1]):
            r_squared = corr_matrix[0, 1] ** 2
            
    treynor = (ann_return - RISK_FREE_RATE) / beta if beta != 0 else 0.0
    
    # 3. Maximum Drawdown & Calmar (Log Returns → exp(cumsum))
    cum_returns = np.exp(daily_port_returns.cumsum())
    max_dd, _ = compute_max_drawdown(cum_returns)
    calmar = ann_return / abs(max_dd) if abs(max_dd) > 0 else 0.0
    
    # 4. VaR 95% (Historical Daily)
    var_95_daily = np.percentile(daily_port_returns, 5)
    
    return {
        "annualized_return": ann_return,
        "annualized_volatility": ann_vol,
        "sortino": sortino,
        "treynor": treynor,
        "r_squared": r_squared,
        "max_drawdown": max_dd,
        "calmar": calmar,
        "var_95_daily": var_95_daily,
        "beta": beta
    }

def calculate_backtest_performance(out_sample_returns: pd.DataFrame, mkt_out_sample: pd.Series, weights: list) -> dict:
    """
    Calculate forward-test performance using static weights.
    Returns cumulative returns for the portfolio and the market (VN-INDEX).
    """
    if len(out_sample_returns) == 0:
        return {}
        
    w = np.array(weights)
    # Calculate daily portfolio returns
    port_daily_ret = out_sample_returns.dot(w)
    
    # Cumulative Returns
    port_cum_ret = (1 + port_daily_ret).cumprod()
    mkt_cum_ret = (1 + mkt_out_sample).cumprod()
    
    # Convert dates to string format
    dates = out_sample_returns.index.strftime('%Y-%m-%d').tolist()
    
    return {
        "dates": dates,
        "portfolio": port_cum_ret.tolist(),
        "market": mkt_cum_ret.tolist()
    }

