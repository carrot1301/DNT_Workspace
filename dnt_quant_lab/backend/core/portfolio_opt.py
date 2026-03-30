import numpy as np
import pandas as pd

def run_monte_carlo(returns_df: pd.DataFrame, num_portfolios: int = 10000) -> dict:
    """
    Sinh Monte Carlo: Tối ưu hoá Danh mục đầu tư.
    Tính toán Efficient Frontier và Sharpe Ratio tối ưu.
    """
    # Khởi tạo ma trận rỗng
    num_assets = len(returns_df.columns)
    points = np.zeros((num_portfolios, 3)) # Return, Volatility, Sharpe
    weights_record = np.zeros((num_portfolios, num_assets))
    
    mean_returns = returns_df.mean() * 252
    cov_matrix = returns_df.cov() * 252
    
    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        
        # Vectorized calculations for speed
        port_return = np.sum(mean_returns * weights)
        port_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        port_volatility = np.sqrt(port_variance)
        
        # Risk-free rate assumed ~3%
        sharpe = (port_return - 0.03) / port_volatility
        
        points[i, 0] = port_return
        points[i, 1] = port_volatility
        points[i, 2] = sharpe
        weights_record[i, :] = weights
        
    # Tìm Max Sharpe
    max_sharpe_idx = np.argmax(points[:, 2])
    max_sharpe_weights = weights_record[max_sharpe_idx, :]
    
    # Tìm Min Volatility
    min_vol_idx = np.argmin(points[:, 1])
    min_vol_weights = weights_record[min_vol_idx, :]
    
    return {
        'max_sharpe': {
            'return': points[max_sharpe_idx, 0],
            'volatility': points[max_sharpe_idx, 1],
            'sharpe': points[max_sharpe_idx, 2],
            'weights': dict(zip(returns_df.columns, max_sharpe_weights))
        },
        'min_volatility': {
            'return': points[min_vol_idx, 0],
            'volatility': points[min_vol_idx, 1],
            'sharpe': points[min_vol_idx, 2],
            'weights': dict(zip(returns_df.columns, min_vol_weights))
        },
        'frontier_points': points # Dùng để vẽ đồ thị Scatter
    }
