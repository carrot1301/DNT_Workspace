import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import os
from data_loader import get_aligned_data, load_stock
from metrics import (
    compute_returns, compute_cumulative_returns, compute_beta,
    compute_volatility, compute_max_drawdown, compute_alpha,
    compute_sharpe_ratio  # <--- Đã thêm import này
)
from utils import generate_insights
st.set_page_config(page_title="VN30 Quant Analyzer", layout="wide")
# --- Page Config & Styling ---
st.set_page_config(page_title="VN30 Quant Analyzer", layout="wide", page_icon="📈")
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    h1, h2, h3 { color: #E0E0E0; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; } /* Chỉnh nhỏ lại một chút để vừa 6 cột */
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("⚙️ VN30 Analyzer")
st.sidebar.markdown("Quantitative Research Dashboard")

try:
    ticker_files = os.listdir("vn30_quant_app/data/stocks")
    VN30_TICKERS = sorted([file.replace(".csv", "") for file in ticker_files if file.endswith(".csv")])
except FileNotFoundError:
    VN30_TICKERS = []

if not VN30_TICKERS:
    st.sidebar.error("No data available. Please check data/stocks/ directory.")
    ticker = None
else:
    ticker = st.sidebar.selectbox("Select Stock Ticker", VN30_TICKERS)

st.sidebar.markdown("---")
st.sidebar.write("### Benchmark: VNINDEX")
st.sidebar.write("**VNINDEX** (Market Portfolio)")

# --- Main Logic ---
st.title(f"📊 Quantitative Analysis: {ticker} vs VNINDEX")

df = get_aligned_data(ticker)
stock_raw = load_stock(ticker) 

if df is not None and stock_raw is not None:
    # 1. Calculations
    df['stock_ret'] = compute_returns(df['stock_close'])
    df['market_ret'] = compute_returns(df['market_close'])
    df.dropna(inplace=True)

    stock_cum_ret = compute_cumulative_returns(df['stock_ret'])
    market_cum_ret = compute_cumulative_returns(df['market_ret'])
    
    total_stock_ret = stock_cum_ret.iloc[-1]
    total_market_ret = market_cum_ret.iloc[-1]
    
    beta = compute_beta(df['stock_ret'], df['market_ret'])
    alpha = compute_alpha(df['stock_ret'], df['market_ret'], beta)
    sharpe = compute_sharpe_ratio(df['stock_ret']) # <--- Tính Sharpe
    stock_vol = compute_volatility(df['stock_ret'])
    market_vol = compute_volatility(df['market_ret'])
    max_dd_stock, dd_series_stock = compute_max_drawdown(df['stock_ret'])

    # --- Top Metric Dashboard (Updated to 6 Columns) ---
    m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)
    
    m_col1.metric("Cumulative Return", f"{total_stock_ret:.2%}", f"vs Market: {(total_stock_ret - total_market_ret):.2%}")
    m_col2.metric("Sharpe Ratio", f"{sharpe:.2f}", "Risk-Adj. Perf")
    m_col3.metric("Beta", f"{beta:.2f}", "VNINDEX = 1.0", delta_color="off")
    m_col4.metric("Jensen's Alpha", f"{alpha:.2%}", "Excess Return")
    m_col5.metric("Volatility (Ann.)", f"{stock_vol:.2%}", f"Mkt: {market_vol:.2%}", delta_color="inverse")
    m_col6.metric("Max Drawdown", f"{max_dd_stock:.2%}", "Hist. Peak", delta_color="inverse")

    st.markdown("---")

    # --- Visualizations ---
    st.subheader("📈 Visual Analytics")
    tab1, tab2, tab3, tab4 = st.tabs(["Price Action", "Cumulative Returns", "Drawdown Profile", "Beta Regression"])

    with tab1:
        fig_candle = go.Figure(data=[go.Candlestick(
            x=stock_raw.index, open=stock_raw['open'], high=stock_raw['high'],
            low=stock_raw['low'], close=stock_raw['stock_close'], name=ticker,
            increasing_line_color='#00FFAA', decreasing_line_color='#FF5555'
        )])
        fig_candle.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_candle, use_container_width=True)

    with tab2:
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(x=stock_cum_ret.index, y=stock_cum_ret, mode='lines', name=ticker, line=dict(color='#00FFAA')))
        fig_cum.add_trace(go.Scatter(x=market_cum_ret.index, y=market_cum_ret, mode='lines', name="VNINDEX", line=dict(color='#FF5555', dash='dash')))
        fig_cum.update_layout(hovermode="x unified", template="plotly_dark", margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_cum, use_container_width=True)

    with tab3:
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(x=dd_series_stock.index, y=dd_series_stock, fill='tozeroy', name="Drawdown", fillcolor='rgba(255, 85, 85, 0.3)'))
        fig_dd.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_dd, use_container_width=True)

    with tab4:
        fig_scatter = px.scatter(df, x='market_ret', y='stock_ret', opacity=0.4, trendline="ols", trendline_color_override="#00FFAA")
        fig_scatter.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    
    # --- Raw Data Explorer ---
    st.subheader("🗄️ Raw Data Explorer")
    with st.expander("View historical OHLCV data"):
        st.caption("ℹ️ All prices in VND.")
        display_df = stock_raw.sort_index(ascending=False).copy()
        st.dataframe(display_df.rename(columns={'stock_close': 'Close'}), use_container_width=True, height=250)
        
    # --- Automated Insights ---
    st.subheader("🧠 Algorithmic Insights")
    # Cập nhật thứ tự tham số khớp với utils.py mới
    insights = generate_insights(ticker, beta, alpha, sharpe, stock_vol, max_dd_stock, total_stock_ret, total_market_ret)
    
    for insight in insights:
        st.markdown(f"- {insight}")

else:
    st.warning("Data alignment failed. Please verify CSV structures.")