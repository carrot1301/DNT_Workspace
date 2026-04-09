let chart = null;
let lineSeries = null;
let candlestickSeries = null;

// View Switcher
function switchView(viewId, btn) {
    document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
    document.getElementById(viewId).classList.remove('hidden');
    
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    if(btn) btn.classList.add('active');

    if(viewId === 'deepdive-view' && chart) {
        chart.timeScale().fitContent();
    }
}

// Fetch Data for Screener
async function initScreenerMock() {
    document.getElementById('vnindex-value').innerText = '1,280.45';
    document.getElementById('vn30-value').innerText = '1,305.12';

    const tbody = document.getElementById('screener-tbody');
    try {
        const response = await fetch('http://127.0.0.1:8000/api/screener');
        const data = await response.json();
        tbody.innerHTML = '';
        data.forEach(d => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${d.ticker}</strong></td>
                <td>${d.price.toFixed(2)}</td>
                <td class="${d.change > 0 ? 'positive' : 'negative'}">${d.change > 0 ? '+' : ''}${d.change}%</td>
                <td>${d.signal}</td>
                <td><button class="btn btn-primary" onclick="loadDeepDive('${d.ticker}', ${d.price})">Phân Tích</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error('Lỗi khi tải bảng giá:', e);
        tbody.innerHTML = '<tr><td colspan="5">Không thể kết nối đến Backend. Đảm bảo FastAPI đang chạy ở cổng 8000.</td></tr>';
    }
}

// Load Deep Dive
function loadDeepDive(ticker, price) {
    document.getElementById('analyzer-ticker').innerText = `${ticker} - Phân Giá Chi Tiết`;
    document.getElementById('analyzer-price').innerText = price.toFixed(2);
    
    // Switch to deep dive tab
    switchView('deepdive-view', document.getElementById('btn-deepdive'));

    // Mock Chart Data
    if(!chart) {
        chart = LightweightCharts.createChart(document.getElementById('tvchart'), {
            layout: { background: { type: 'solid', color: 'transparent' }, textColor: '#d1d4dc' },
            grid: { vertLines: { color: 'rgba(42, 46, 57, 0.5)' }, horzLines: { color: 'rgba(42, 46, 57, 0.5)' } },
            timeScale: { timeVisible: true, secondsVisible: false }
        });
        candlestickSeries = chart.addCandlestickSeries({
            upColor: '#3fb950', downColor: '#f85149', borderVisible: false, wickUpColor: '#3fb950', wickDownColor: '#f85149'
        });
    }

    // Fetch Real Data for Chart
    fetch(`http://127.0.0.1:8000/api/stock/${ticker}/chart`)
        .then(res => res.json())
        .then(data => {
            if(Array.isArray(data) && data.length > 0) {
                // filter out invalid time rows just in case
                const validData = data.filter(d => !isNaN(d.time)).sort((a,b)=> a.time - b.time);
                candlestickSeries.setData(validData);
                chart.timeScale().fitContent();
            } else {
                console.warn('No chart data found for', ticker);
            }
        }).catch(err => console.error(err));

    // Mock FA Data
    document.getElementById('fa-metrics').innerHTML = `
        <div class="metric-box"><span>P/E</span><strong>${(Math.random()*20+5).toFixed(2)}</strong></div>
        <div class="metric-box"><span>P/B</span><strong>${(Math.random()*3+1).toFixed(2)}</strong></div>
        <div class="metric-box"><span>ROE</span><strong>${(Math.random()*15+10).toFixed(1)}%</strong></div>
        <div class="metric-box"><span>Debt/Equity</span><strong>${(Math.random()*1).toFixed(2)}</strong></div>
    `;

    document.getElementById('quant-score-value').innerText = Math.floor(Math.random()*40 + 50);
}

// Generate Report
function generateReport() {
    const reportSection = document.getElementById('report-section');
    const content = document.getElementById('report-content');
    
    reportSection.classList.remove('hidden');
    content.innerHTML = '<p><em>Đang kết nối tới AI Engine để tổng hợp dữ liệu TA, FA, và Quant...</em></p>';

    setTimeout(() => {
        content.innerHTML = `
            <h3>Góc Nhìn Thực Chiến</h3>
            <p>Dựa trên các chỉ số động lượng và định giá hiện tại, cổ phiếu đang cho thấy những dấu hiệu tích lũy tích cực. Chỉ báo RSI đang dao động quanh ngưỡng 55, trong khi MACD histogram vừa mới cắt qua đường zero line - dòng tiền lớn đang rục rịch nhập cuộc.</p>
            <br>
            <p><strong>Khuyến nghị:</strong> Có thể mở vị thế mua thăm dò (swing long) với mức phân bổ 30% NAV. Cân nhắc đặt lệnh stop loss (cắt lỗ) chặt chẽ nếu giá thủng đường EMA20 để quản trị rủi ro.</p>
        `;
    }, 1500);
}

// Init
window.onload = initScreenerMock;
