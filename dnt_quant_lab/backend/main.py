from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import plotly.graph_objects as go
import json

from core.data_engine import prepare_portfolio_data, fetch_current_prices
from core.portfolio_opt import run_monte_carlo, calculate_stress_test, evaluate_custom_portfolio

app = FastAPI(title="DNT Quant Lab API")

# Setup CORS for frontend to communicate without policy errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    capital: float
    target_return: float
    tickers: list[str]

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
        hovertemplate="Return: %{y:.2%}<br>Vol: %{x:.2%}<br>Sharpe: " + f"{ms['sharpe']:.2f}"
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(title="Biến động (Rủi ro)", showgrid=False, zeroline=False),
        yaxis=dict(title="Lợi nhuận Kì vọng", showgrid=True, gridcolor='rgba(255,255,255,0.1)', zeroline=False),
        font=dict(color='#94A3B8')
    )
    
    chart_json = json.loads(fig.to_json())
    
    return {
        "chart": chart_json,
        "monte_carlo": mc_results,
        "stress_test": stress_test_results
    }

class EvaluationRequest(BaseModel):
    holdings: dict[str, float]  # e.g., {"SHB": 100, "VIC": 50, "GAS": 20}
    days: int                   # e.g., 63 for 3 months

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
    
    return {
        "chart": json.loads(fig.to_json()),
        "monte_carlo": eval_results,  # Ta mượn cấu trúc trả giống nhau để Frontend dễ xài
        "stress_test": stress_test_results
    }
