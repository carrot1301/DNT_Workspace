import numpy as np
import pandas as pd

# --- Quantitative Constants (Vietnam Market Context 2026) ---
TRADING_DAYS = 252 
# Risk-free rate based on 10-year Vietnam Government Bond yields (~3%)
RISK_FREE_RATE = 0.03 

def compute_returns(prices: pd.Series) -> pd.Series:
    """Calculate Daily Percentage Returns."""
    return prices.pct_change().dropna()

def compute_cumulative_returns(returns: pd.Series) -> pd.Series:
    """Calculate the growth of an initial 1 VND investment."""
    return (1 + returns).cumprod() - 1

def compute_beta(stock_returns: pd.Series, market_returns: pd.Series) -> float:
    """
    Calculate Beta: Measures systematic risk relative to VNINDEX.
    Beta > 1: Aggressive (More volatile)
    Beta < 1: Defensive (Less volatile)
    """
    cov_matrix = np.cov(stock_returns, market_returns)
    covariance = cov_matrix[0, 1]
    market_variance = cov_matrix[1, 1]
    
    # Avoid division by zero for extremely stable markets
    return covariance / market_variance if market_variance != 0 else 0.0

def compute_volatility(returns: pd.Series) -> float:
    """Calculate Annualized Volatility (Standard Deviation of returns)."""
    return returns.std() * np.sqrt(TRADING_DAYS)

def compute_sharpe_ratio(returns: pd.Series) -> float:
    """
    Calculate the Sharpe Ratio (Risk-Adjusted Return).
    Measures excess return per unit of total risk.
    """
    ann_return = (1 + returns.mean()) ** TRADING_DAYS - 1
    ann_vol = compute_volatility(returns)
    
    return (ann_return - RISK_FREE_RATE) / ann_vol if ann_vol != 0 else 0.0

def compute_max_drawdown(returns: pd.Series):
    """
    Calculate the Maximum Drawdown (MDD) and the full Drawdown Series.
    Essential for understanding worst-case loss scenarios.
    """
    cum_returns = (1 + returns).cumprod()
    running_max = cum_returns.cummax()
    drawdown = (cum_returns - running_max) / running_max
    max_drawdown = drawdown.min()
    
    return max_drawdown, drawdown

def compute_alpha(stock_returns: pd.Series, market_returns: pd.Series, beta: float) -> float:
    """
    Calculate Jensen's Alpha using the Capital Asset Pricing Model (CAPM).
    Alpha represents the performance 'edge' added by the manager/strategy.
    """
    # Calculate Geometric Annualized Returns for more accuracy
    ann_stock_ret = (1 + stock_returns.mean()) ** TRADING_DAYS - 1
    ann_market_ret = (1 + market_returns.mean()) ** TRADING_DAYS - 1
    
    # CAPM Formula: E(R) = Rf + Beta * [E(Rm) - Rf]
    expected_return = RISK_FREE_RATE + beta * (ann_market_ret - RISK_FREE_RATE)
    
    # Alpha = Actual Performance - Benchmark-adjusted Performance
    alpha = ann_stock_ret - expected_return
    return alpha