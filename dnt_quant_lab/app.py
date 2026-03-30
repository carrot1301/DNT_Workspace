import streamlit as st
import os
import json
import plotly.graph_objects as go
import pandas as pd
from core.data_engine import fetch_stock_data

# --- Setup Page ---
st.set_page_config(page_title="DNT Quant Lab", layout="wide", page_icon="🧪")

# Thêm tuỳ chỉnh CSS màu sắc, UX như cũ
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    h1, h2, h3 { color: #E0E0E0; }
    [data-testid="stSidebar"] {
        background: rgba(11, 15, 25, 0.4) !important;
        backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(0, 255, 170, 0.2) !important;
    }
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.3) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 255, 170, 0.15) !important;
        padding: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("🧪 DNT Quant Lab")
st.sidebar.markdown("Hệ thống Cố vấn Đầu tư Thông minh")

# Navigation Menu
menu = ["📊 Quản lý Danh mục (Monte Carlo)", "⏳ Backtest Chiến lược", "📝 Cố vấn AI (Gemini)"]
choice = st.sidebar.radio("Điều hướng / Navigation", menu)
st.sidebar.markdown("---")

# Tải danh sách Tickers
@st.cache_data
def load_tickers():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data', 'all_tickers.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

ALL_TICKERS = load_tickers()

# Giao diện chính tuỳ theo Menu
if choice == menu[0]:
    st.title("Phân tích Rủi ro & Tối ưu hóa Danh mục")
    st.write("Mô phỏng 10,000 kịch bản bằng thuật toán Monte Carlo.")
    
    selected_tickers = st.multiselect("Vui lòng chọn 3-5 mã cổ phiếu để lập Danh mục (Portfolio):", ALL_TICKERS)
    
    if len(selected_tickers) > 0:
        if st.button("🚀 Bắt đầu mô phỏng (Run Monte Carlo)"):
            st.info("Module portfolio_opt.py đang được xây dựng... Sẽ kết nối véc-tơ hóa Numpy sớm!")

elif choice == menu[1]:
    st.title("Kiểm định Lịch sử (Backtesting)")
    st.write("Thử nghiệm các chiến thuật Giao cắt đường trung bình, RSI, v.v.")
    
elif choice == menu[2]:
    st.title("🤖 Cố vấn AI Đầu tư (BETA)")
    st.write("Phóng dữ liệu kỹ thuật qua Gemini LLM để nhận Báo cáo tự động dễ hiểu cho Nhà đầu tư mới (F0).")
    
    # Input API Key an toàn
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""
        
    api_input = st.text_input("Vui lòng nhập Google Gemini API Key của bạn (Sẽ không được lưu trữ):", type="password")
    if api_input:
        st.session_state["api_key"] = api_input
        st.success("API Key đã được thêm tạm thời!")

st.sidebar.markdown("<br><br><br><br>", unsafe_allow_html=True)
st.sidebar.caption("⚡ **Phát triển bởi Doan Nguyen Tri**")
