from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import plotly.graph_objects as go
import json
import math
import os
import numpy as np
import requests
from datetime import datetime


def sanitize_floats(obj):
    """Đệ quy làm sạch nan/inf trong dict/list/float trước khi trả về JSON."""
    if isinstance(obj, dict):
        return {k: sanitize_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_floats(v) for v in obj]
    elif isinstance(obj, float) or isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    return obj

from core.data_engine import prepare_portfolio_data, fetch_current_prices, fetch_recent_news
from core.portfolio_opt import run_monte_carlo, calculate_stress_test, evaluate_custom_portfolio, calculate_backtest, calculate_advanced_metrics
from core.ai_advisor import stream_ai_advice
from core.backtester import run_backtrader_strategy
from core.signals import compute_signals
from core.screener import run_daily_radar

app = FastAPI(title="DNT Quant Lab API")

# Database (RAM) để lưu trạng thái thanh toán
# Format: {"SESSION_ID": True}
payments_db = {}

# Đệm cho radar F0
radar_cache = {"date": None, "data": []}

# Setup CORS for frontend to communicate without policy errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend tĩnh tại /
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

class SimulationRequest(BaseModel):
    capital: float
    target_return: float
    tickers: list[str]
    lang: str = "vi"
    timeframe_days: int = 252

@app.post("/api/run-simulation")
def get_simulation_data(req: SimulationRequest):
    if len(req.tickers) < 2:
        return {"error": "Cần ít nhất 2 mã cổ phiếu để chạy tối ưu hóa danh mục."}
        
    # 1. Tải và Xử lý dữ liệu
    port_ret, mkt_ret = prepare_portfolio_data(req.tickers, days_back=1000)
    
    # 2. Chạy thuật toán Monte Carlo
    num_ports = 10000
    mc_results = run_monte_carlo(port_ret, num_ports, req.capital, req.timeframe_days)
    
    # 3. Chạy Stress Test dựa trên rổ cổ phiếu Max Sharpe
    stress_test_results = calculate_stress_test(
        port_ret, mkt_ret, mc_results['max_sharpe']['weights'], req.capital, crash_percent=-0.05
    )
    
    # 4. Vẽ biểu đồ Plotly (Bắn Json về Web)
    fig = go.Figure()
    
    # Tất cả các kịch bản phụ
    fig.add_trace(go.Scatter(
        x=mc_results['frontier_points_x'], 
        y=mc_results['frontier_points_y'], 
        mode='markers', 
        name='Random Portfolios',
        marker=dict(
            color=mc_results['frontier_points_c'], 
            colorscale='Viridis', 
            size=4,
            opacity=0.5,
            showscale=True,
            colorbar=dict(title="Sharpe Ratio")
        ),
        hoverinfo='skip'
    ))
    
    # Điểm Max Sharpe
    ms = mc_results['max_sharpe']
    fig.add_trace(go.Scatter(
        x=[ms['volatility']], 
        y=[ms['expected_return']], 
        mode='markers+text', 
        name='Max Sharpe',
        text=['Optimal'],
        textposition='top center',
        marker=dict(color='#00FFAA', size=15, symbol='star', line=dict(color='white', width=2)),
        hovertemplate="Lợi nhuận: %{y:.2%}<br>Rủi ro: %{x:.2%}<br>Sharpe: " + f"{ms['sharpe']:.2f}"
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(title="Độ biến động (Rủi ro)", showgrid=False, zeroline=False),
        yaxis=dict(title="Lợi nhuận kỳ vọng", showgrid=True, gridcolor='rgba(255,255,255,0.1)', zeroline=False),
        font=dict(color='#94A3B8'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    chart_json = json.loads(fig.to_json())
    
    # Pie chart for Optimized Portfolio (Max Sharpe)
    ms_weights = mc_results['max_sharpe']['weights']
    pie_fig = go.Figure(data=[go.Pie(
        labels=list(ms_weights.keys()), 
        values=list(ms_weights.values()),
        hole=.5,
        marker=dict(colors=['#00FFAA', '#00B8FF', '#FF5555', '#F59E0B', '#8B5CF6'])
    )])
    pie_fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0), font=dict(color='#94A3B8')
    )
    
    # Backtest logic (Backtrader Validation)
    bt_data = run_backtrader_strategy(req.tickers, ms_weights, req.capital)
    bt_fig = go.Figure()
    if bt_data['dates']:
        bt_fig.add_trace(go.Scatter(x=bt_data['dates'], y=bt_data['portfolio_cum_returns'], mode='lines', name='MVO Strategy (BT)', line=dict(color='#00FFAA', width=2)))
        bt_fig.add_trace(go.Scatter(x=bt_data['dates'], y=bt_data['market_cum_returns'], mode='lines', name='VNINDEX', line=dict(color='#94A3B8', width=1, dash='dot')))
        bt_fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'))
    
    bt_chart_json = json.loads(bt_fig.to_json()) if bt_data['dates'] else None
    
    # Real-time Signals
    signals_data = compute_signals(req.tickers, ms_weights, req.capital)
    
    # Advanced Metrics & Raw Prices
    port_ret_selected = port_ret[list(ms_weights.keys())]
    daily_port_returns = port_ret_selected.dot(np.array(list(ms_weights.values())))
    adv_metrics = calculate_advanced_metrics(daily_port_returns, mkt_ret)
    cur_prices = fetch_current_prices(req.tickers)
    
    # Fetch Fundamental data for all tickers to assist AI
    fundamentals_data = {}
    for t in req.tickers:
        fund_res = fetch_financials_internal(t)
        if "error" not in fund_res:
            fundamentals_data[t] = fund_res

    res = {
        "monte_carlo": mc_results,
        "stress_test": stress_test_results,
        "advanced_metrics": adv_metrics,
        "raw_prices": cur_prices,
        "fundamentals": fundamentals_data,
        "last_updated_date": datetime.now().strftime("%d-%m-%Y"),
        "chart": chart_json,
        "pie_chart": json.loads(pie_fig.to_json()),
        "backtest_chart": bt_chart_json,
        "trading_signals": signals_data
    }
    return sanitize_floats(res)

# ── BCTC Manual Check ─────────────────────────────────────────
@app.get("/api/check-manual-bctc")
def check_manual_bctc(tickers: str):
    """
    Kiểm tra xem các mã truyền vào đã có BCTC thủ công (RAG) chưa.
    """
    registry_path = os.path.join(os.path.dirname(__file__), "data", "bctc_registry.json")
    if not os.path.exists(registry_path):
        return {}
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception:
        return {}
        
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    matches = {}
    for t in ticker_list:
        if t in registry:
            matches[t] = registry[t]
            
    return matches

# ── Live News (vnstock) ───────────────────────────────────────
@app.get("/api/news")
def get_live_news(tickers: str):
    """
    Lấy điểm tin (Headlines & Summaries) từ vnstock.
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    news = fetch_recent_news(ticker_list, limit=3)
    return news

# ── AI Auto Radar (F0) ───────────────────────────────────────
@app.get("/api/ai-radar")
def get_ai_radar():
    """
    Trả về top 5 mã cổ phiếu có điểm FA (Cơ bản) và TA (Kỹ thuật) tốt nhất hiện tại.
    Có Cache trên RAM theo ngày để tối ưu performance.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if radar_cache["date"] == today_str and radar_cache["data"]:
        return radar_cache["data"]
        
    try:
        top_picks = sanitize_floats(run_daily_radar())
        radar_cache["date"] = today_str
        radar_cache["data"] = top_picks
        return top_picks
    except Exception as e:
        print(f"Lỗi AI Radar: {e}")
        return []



# ── Gemini AI Advice ──────────────────────────────────────────
class AIAdviceRequest(BaseModel):
    monte_carlo: dict
    stress_test: dict
    advanced_metrics: dict = {}
    manual_bctc_tickers: list[str] = []
    news_data: dict = {}
    lang: str = "vi"

@app.post("/api/ai-advice")
def get_ai_advice(req: AIAdviceRequest):
    """
    Stream lời khuyên đầu tư từ Gemini AI dựa trên kết quả Monte Carlo.
    Sử dụng Server-Sent streaming để frontend nhận text từng chunk.
    """
    data = {
        "monte_carlo": req.monte_carlo,
        "stress_test": req.stress_test,
        "advanced_metrics": req.advanced_metrics,
        "manual_bctc_tickers": req.manual_bctc_tickers,
        "news_data": req.news_data
    }

    def generate():
        for chunk in stream_ai_advice(data, req.lang):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={"X-Content-Type-Options": "nosniff"}
    )


class EvaluationRequest(BaseModel):
    holdings: dict[str, float]  # e.g., {"SHB": 100, "VIC": 50, "GAS": 20}
    days: int                   # e.g., 63 for 3 months
    lang: str = "vi"

@app.post("/api/evaluate-portfolio")
def evaluate_custom(req: EvaluationRequest):
    tickers = list(req.holdings.keys())
    if len(tickers) == 0:
        return {"error": "Cần ít nhất 1 mã để định giá."}

    # 1. Truy vấn mốc giá hiện tại để qui ra Tiền
    current_prices = fetch_current_prices(tickers)
    
    # 2. Định giá Vốn & Tỉ trọng hiện tại
    total_capital = 0.0
    values = {}
    for t in tickers:
        p = current_prices.get(t, 0)
        v = p * req.holdings[t]
        values[t] = v
        total_capital += v
        
    if total_capital == 0:
        return {"error": "Không thể định giá danh mục (Dữ liệu rỗng)."}
        
    weights = {t: values[t]/total_capital for t in tickers}
    
    # 3. Kéo dữ liệu quá khứ cho tập tickers để trích Covariance Matrix
    port_ret, mkt_ret = prepare_portfolio_data(tickers, days_back=1000)
    
    # 4. Giả lập Dải xác suất tương lai
    eval_results = evaluate_custom_portfolio(port_ret, weights, total_capital, req.days)
    
    # 5. Stress test nếu ngày mai mất điện rơi 5%
    stress_test_results = calculate_stress_test(port_ret, mkt_ret, weights, total_capital, crash_percent=-0.05)
    
    # Vẽ Biểu đồ Asset Allocation (Trực quan hóa Phân bổ Tỉ trọng)
    fig = go.Figure(data=[go.Pie(
        labels=tickers, 
        values=[weights[t] for t in tickers],
        hole=.5,
        marker=dict(colors=['#00FFAA', '#00B8FF', '#FF5555', '#F59E0B', '#8B5CF6'])
    )])
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(color='#94A3B8')
    )
    
    # Backtest logic (Backtrader Evaluation)
    bt_data = run_backtrader_strategy(tickers, weights, total_capital)
    bt_fig = go.Figure()
    if bt_data['dates']:
        bt_fig.add_trace(go.Scatter(x=bt_data['dates'], y=bt_data['portfolio_cum_returns'], mode='lines', name='Custom Strategy (BT)', line=dict(color='#00FFAA', width=2)))
        bt_fig.add_trace(go.Scatter(x=bt_data['dates'], y=bt_data['market_cum_returns'], mode='lines', name='VNINDEX', line=dict(color='#94A3B8', width=1, dash='dot')))
    bt_fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0), font=dict(color='#94A3B8'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Lấy Advanced Metrics
    port_ret_selected = port_ret[tickers]
    daily_port_returns = port_ret_selected.dot(np.array([weights[t] for t in tickers]))
    adv_metrics = calculate_advanced_metrics(daily_port_returns, mkt_ret)
    last_updated_date = port_ret.index.max().strftime('%d-%m-%Y') if not port_ret.index.empty else ""
    
    return sanitize_floats({
        "chart": None, # Disable the main scatter chart for evaluate since it's just pie + line
        "pie_chart": json.loads(fig.to_json()),
        "backtest_chart": json.loads(bt_fig.to_json()),
        "monte_carlo": eval_results,  # Ta mượn cấu trúc trả giống nhau để Frontend dễ xài
        "stress_test": stress_test_results,
        "advanced_metrics": adv_metrics,
        "raw_prices": current_prices,
        "last_updated_date": last_updated_date,
        "trading_signals": compute_signals(tickers, weights, total_capital)
    })

@app.get("/api/current-prices")
def get_current_prices(tickers: str):
    """
    Trả về giá cổ phiếu hiện thời theo list. Định dạng: FPT,MWG,VIC
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not ticker_list:
        return {}
    prices = fetch_current_prices(ticker_list)
    return sanitize_floats(prices)


# ── SePay & Báo Cáo Tài Chính (TCBS Integration) ──────────────────
from fastapi import Request
import requests

@app.post("/hooks/sepay-payment")
async def sepay_webhook(req: Request):
    """
    Webhook nhận thông báo khi có giao dịch mới (SePay -> VPBank).
    - Lấy nội dung chuyển khoản (Ví dụ: DNTLAB 123456)
    - So khớp với hóa đơn ảo tạm thời trên hệ thống
    """
    try:
        data = await req.json()
        content = str(data.get("content", "")).upper()
        amount = int(data.get("transferAmount", 0))
        
        # Nếu nhận >= 5000đ và có chữ DNTLAB trong nội dung CK
        if amount >= 5000 and "DNTLAB" in content:
            parts = content.split("DNTLAB")
            if len(parts) > 1:
                session_id = parts[1].strip().split()[0]
                payments_db[session_id] = True
                
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/payment-status")
def get_payment_status(session_id: str):
    """Client polling API này để xem trạng thái hóa đơn"""
    is_paid = payments_db.get(session_id, False)
    return {"paid": is_paid}

def fetch_financials_internal(ticker: str):
    ticker = ticker.upper()
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{ticker}/overview"
        res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()
        data = res.json()
    except Exception as api_err:
        import random
        # Fallback Mock Data for demo purposes if external API is dead
        data = {
            "industry": "Công nghệ / Tài chính (Mock)",
            "marketcap": random.randint(10000, 200000),
            "pe": round(random.uniform(8, 25), 2),
            "pb": round(random.uniform(1.0, 5.0), 2),
            "roe": round(random.uniform(0.05, 0.30), 4),
            "roa": round(random.uniform(0.01, 0.15), 4),
            "debtOnEquity": round(random.uniform(0.1, 3.0), 2),
            "revenueGrowth": round(random.uniform(-0.1, 0.5), 4),
            "profitGrowth": round(random.uniform(-0.2, 0.6), 4)
        }
        
    try:    
        # Format metrics
        financials = {
            "ticker": ticker,
            "industry": data.get("industry", ""),
            "marketCap": data.get("marketcap", 0),
            "pe": data.get("pe", 0),
            "pb": data.get("pb", 0),
            "roe": data.get("roe", 0) * 100 if data.get("roe") else 0,
            "roa": data.get("roa", 0) * 100 if data.get("roa") else 0,
            "debt_on_equity": data.get("debtOnEquity", 0),
            "revenue_growth": data.get("revenueGrowth", 0) * 100 if data.get("revenueGrowth") else 0,
            "profit_growth": data.get("profitGrowth", 0) * 100 if data.get("profitGrowth") else 0,
        }
        return financials
    except Exception as e:
        return {"error": f"Lỗi parse dữ liệu TCBS: {str(e)}"}

@app.get("/api/financials/{ticker}")
def get_financial_reports(ticker: str, session_id: str = None):
    """
    Kéo API miễn phí từ TCBS v1/ticker/overview
    Cơ chế Paywall đã được thay bằng quyên góp tự nguyện.
    Trả về toàn bộ dữ liệu chỉ số cơ bản.
    """
    financière_data = fetch_financials_internal(ticker)
    if "error" in financière_data:
        return financière_data
        
    financials = financière_data.copy()
    return sanitize_floats(financials)


# Mount toàn bộ folder frontend làm static files (đặt cuối cùng sau tất cả API routes)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
