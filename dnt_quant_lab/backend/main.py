from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import plotly.graph_objects as go
import json

app = FastAPI(title="DNT Quant Lab API")

# Setup CORS for frontend to communicate without policy errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to DNT Quant Lab API"}

@app.get("/api/demo-chart")
def get_demo_chart():
    """
    Tạo một biểu đồ bằng Plotly Python siêu đẹp, và xuất ra JSON.
    Frontend sẽ nhận cục JSON này và vẽ lại y hệt với tốc độ cao.
    """
    # Demo Mock data cho biểu đồ
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[10, 15, 13, 17], 
                             mode='lines+markers', name='VNINDEX',
                             line=dict(color='#00FFAA', width=3)))
    
    # Cấu hình phong cách siêu Neon/Dark
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',  # Kính mờ (Trong suốt)
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', zeroline=False),
        font=dict(color='#94A3B8')
    )
    
    # Ép kiểu ra định dạng JSON tương thích với Plotly.js Frontend
    chart_json = fig.to_json()
    return json.loads(chart_json)
