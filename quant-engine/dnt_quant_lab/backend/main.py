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

from core.data_engine import prepare_portfolio_data, fetch_current_prices
from core.portfolio_opt import run_monte_carlo, calculate_stress_test, evaluate_custom_portfolio, calculate_backtest, calculate_advanced_metrics
from core.ai_advisor import stream_ai_advice
from core.backtester import walk_forward_backtest

app = FastAPI(title="DNT Quant Lab API")

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

@app.post("/api/run-simulation")
def get_simulation_data(req: SimulationRequest):
    if len(req.tickers) < 2:
        return {"error": "Cần ít nhất 2 mã cổ phiếu để chạy tối ưu hóa danh mục."}
        
    # 1. Tải và Xử lý dữ liệu
    port_ret, mkt_ret = prepare_portfolio_data(req.tickers, days_back=1000)
    
    # 2. Chạy thuật toán Monte Carlo
    num_ports = 10000
    mc_results = run_monte_carlo(port_ret, num_ports, req.capital)
    
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
    
    # Backtest logic (Walk-Forward Validation)
    bt_data = walk_forward_backtest(port_ret, mkt_ret)
    bt_fig = go.Figure()
    if bt_data['dates']:
        bt_fig.add_trace(go.Scatter(x=bt_data['dates'], y=bt_data['portfolio_cum_returns'], mode='lines', name='MVO (OOS)', line=dict(color='#00FFAA', width=2)))
        bt_fig.add_trace(go.Scatter(x=bt_data['dates'], y=bt_data['equal_weight_cum_returns'], mode='lines', name='Equal Weight', line=dict(color='#FCD34D', width=2)))
        bt_fig.add_trace(go.Scatter(x=bt_data['dates'], y=bt_data['market_cum_returns'], mode='lines', name='VNINDEX', line=dict(color='#94A3B8', width=1, dash='dot')))
    bt_fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0), font=dict(color='#94A3B8'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Advanced Metrics & Raw Prices
    port_ret_selected = port_ret[list(ms_weights.keys())]
    daily_port_returns = port_ret_selected.dot(np.array(list(ms_weights.values())))
    adv_metrics = calculate_advanced_metrics(daily_port_returns, mkt_ret)
    raw_prices = fetch_current_prices(req.tickers)
    last_updated_date = port_ret.index.max().strftime('%d-%m-%Y') if not port_ret.index.empty else ""
    
    return sanitize_floats({
        "chart": chart_json,
        "pie_chart": json.loads(pie_fig.to_json()),
        "backtest_chart": json.loads(bt_fig.to_json()),
        "monte_carlo": mc_results,
        "stress_test": stress_test_results,
        "advanced_metrics": adv_metrics,
        "raw_prices": raw_prices,
        "last_updated_date": last_updated_date
    })

# ── Gemini AI Advice ──────────────────────────────────────────
class AIAdviceRequest(BaseModel):
    monte_carlo: dict
    stress_test: dict
    advanced_metrics: dict = {}
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
        "advanced_metrics": req.advanced_metrics
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
    
    # Backtest logic
    bt_data = calculate_backtest(port_ret, mkt_ret, weights)
    bt_fig = go.Figure()
    if bt_data['dates']:
        bt_fig.add_trace(go.Scatter(x=bt_data['dates'], y=bt_data['portfolio_cum_returns'], mode='lines', name='Custom Portfolio', line=dict(color='#00FFAA', width=2)))
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
        "last_updated_date": last_updated_date
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

# Mount toàn bộ folder frontend làm static files (đặt cuối cùng sau tất cả API routes)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
