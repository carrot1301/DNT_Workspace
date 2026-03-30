import numpy as np
import pandas as pd

def run_monte_carlo(returns_df: pd.DataFrame, num_portfolios: int = 10000, initial_capital: float = 1000000) -> dict:
    """
    Sinh Monte Carlo: Tối ưu hoá Danh mục đầu tư.
    Tính toán Efficient Frontier, điểm Sharpe tối ưu và Khoảng tin cậy (Confidence Interval).
    """
    num_assets = len(returns_df.columns)
    points = np.zeros((num_portfolios, 3)) # Return, Volatility, Sharpe
    weights_record = np.zeros((num_portfolios, num_assets))
    
    mean_returns = returns_df.mean() * 252
    cov_matrix = returns_df.cov() * 252
    
    # Sinh trọng số ngẫu nhiên
    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        
        port_return = np.sum(mean_returns * weights)
        port_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        port_volatility = np.sqrt(port_variance)
        
        sharpe = (port_return - 0.03) / port_volatility # Giả định risk-free rate 3%
        
        points[i, :] = [port_return, port_volatility, sharpe]
        weights_record[i, :] = weights
        
    # Lấy danh mục có Max Sharpe
    max_sharpe_idx = np.argmax(points[:, 2])
    ms_return = points[max_sharpe_idx, 0]
    ms_volatil = points[max_sharpe_idx, 1]
    ms_weights = weights_record[max_sharpe_idx, :]
    
    # -- TÍNH KHOẢNG XÁC SUẤT 95% (CONFIDENCE INTERVAL) --
    # Khảo sát Return theo danh mục Max Sharpe với phân phối chuẩn
    # 95% CI (1.96 standard deviations từ mean)
    lower_bound_return = ms_return - (1.96 * ms_volatil)
    upper_bound_return = ms_return + (1.96 * ms_volatil)
    
    # 5% sụt giảm tồi tệ nhất (Value at Risk - VaR 95%)
    # = Mức return tệ nhất ở ngưỡng 95% tự tin
    var_95_percent = ms_return - (1.645 * ms_volatil)
    
    # Tính ra số tiền thực tế
    lower_bound_val = initial_capital * (1 + lower_bound_return)
    upper_bound_val = initial_capital * (1 + upper_bound_return)
    expected_val = initial_capital * (1 + ms_return)
    
    # Tính VaR: Phần tổn thất so với VỐN GỐC (luôn âm hoặc bằng 0)
    # var_95_worst_value = giá trị danh mục ở kịch bản xấu nhất 5%
    var_95_worst_value = initial_capital * (1 + var_95_percent)
    # var_value_loss = mức lỗ/lãi so với ban đầu (< 0 là mất tiền, > 0 là vẫn lời dù ít)
    var_95_value = var_95_worst_value - initial_capital
    
    return {
        'max_sharpe': {
            'expected_return': ms_return,
            'volatility': ms_volatil,
            'sharpe': points[max_sharpe_idx, 2],
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
        'frontier_points_x': points[:, 1].tolist(),
        'frontier_points_y': points[:, 0].tolist(),
        'frontier_points_c': points[:, 2].tolist()
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
    daily_cov_matrix = port_ret_selected.cov()
    
    port_daily_return = np.sum(daily_mean_returns * weights)
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
    # Tính VaR: Phần tổn thất so với VỐN GỐC (luôn âm hoặc bằng 0)
    var_95_worst_value = initial_capital * (1 + var_95_percent)
    var_95_value = var_95_worst_value - initial_capital
    
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
    
    # Tính Cumulative Returns
    cum_port = (1 + daily_port_returns).cumprod() - 1
    cum_market = (1 + market_returns).cumprod() - 1
    
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
        
    ann_return = (1 + daily_port_returns.mean()) ** TRADING_DAYS - 1
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
    
    # 3. Maximum Drawdown & Calmar
    cum_returns = (1 + daily_port_returns).cumprod()
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
