def generate_insights(ticker, beta, alpha, sharpe, stock_vol, max_dd, total_stock_ret, total_market_ret):
    """
    Generate automated insights based on quantitative metrics.
    Written in a sophisticated, institutional financial reporting style.
    """
    insights = []
    
    # 1. Systematic Risk (Beta)
    if beta > 1.3:
        beta_desc = "is classified as **High Beta / Aggressive**. This asset is highly sensitive to market swings and will likely amplify VNINDEX movements significantly."
    elif beta > 0.8:
        beta_desc = "exhibits **Market-aligned** volatility, effectively tracking the broader benchmark's trajectory with moderate systemic exposure."
    elif beta > 0.3:
        beta_desc = "is a **Defensive** asset, demonstrating low sensitivity to systemic shocks and acting as a potential stabilizer during market turbulence."
    else:
        beta_desc = "shows **Uncorrelated / Inverse** movement relative to the market, providing unique diversification benefits."
    
    insights.append(f"**Systematic Risk (Beta):** With a Beta of {beta:.2f}, {ticker} {beta_desc}")

    # 2. Risk-Reward Efficiency (Sharpe Ratio) - NEW
    if sharpe > 1.5:
        sharpe_desc = "is **Excellent**. The asset provides high excess returns relative to the volatility incurred."
    elif sharpe > 1.0:
        sharpe_desc = "is **Strong**. It maintains a healthy balance between capital appreciation and risk exposure."
    elif sharpe > 0:
        sharpe_desc = "is **Adequate**, though it may be prone to periods of high volatility without proportional compensation in returns."
    else:
        sharpe_desc = "is **Suboptimal (Negative)**, indicating that the risk taken does not justify the returns over the risk-free rate."

    insights.append(f"**Risk-Reward Efficiency (Sharpe):** The Sharpe Ratio of {sharpe:.2f} {sharpe_desc}")

    # 3. Jensen's Alpha (The Edge)
    if alpha > 0.05:
        alpha_desc = f"generated a **significant alpha (+{alpha:.2%})**. This suggests strong security selection or idiosyncratic growth factors."
    elif alpha > 0:
        alpha_desc = f"yielded a **marginal positive alpha (+{alpha:.2%})**, slightly outperforming CAPM expectations."
    else:
        alpha_desc = f"yielded a **negative alpha ({alpha:.2%})**, failing to compensate for the systematic risk taken compared to the market benchmark."
        
    insights.append(f"**Alpha Generation:** {ticker} {alpha_desc}")

    # 4. Downside Risk (Max Drawdown)
    if max_dd < -0.4:
        dd_desc = f"is **Severe ({max_dd:.2%})**. High-conviction investors only; requires extreme risk tolerance due to historical capital erosion."
    elif max_dd < -0.2:
        dd_desc = f"is **Moderate ({max_dd:.2%})**, which is typical for Vietnamese equity fluctuations during correction phases."
    else:
        dd_desc = f"is **Exceptional ({max_dd:.2%})**, highlighting superior capital preservation and resilience during market downturns."
        
    insights.append(f"**Risk Profile (Max Drawdown):** Historical maximum drawdown {dd_desc}")

    # 5. Algorithmic Verdict (Summary)
    # A quick logic to categorize the stock
    if alpha > 0 and sharpe > 1.0 and max_dd > -0.2:
        verdict = "**Verdict:** This asset qualifies as a **'Quality Growth'** play with superior risk-adjusted performance."
    elif beta < 0.8 and max_dd > -0.15:
        verdict = "**Verdict:** This asset acts as a **'Defensive Anchor'**, ideal for capital preservation."
    elif beta > 1.2 and alpha > 0.05:
        verdict = "**Verdict:** This is a **'High-Beta Alpha'** play, suitable for aggressive momentum strategies."
    else:
        verdict = "**Verdict:** Performance is **'Market-Standard'**; careful monitoring of sector-specific catalysts is advised."
    
    insights.append(verdict)

    return insights