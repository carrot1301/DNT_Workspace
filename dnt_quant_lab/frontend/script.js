const I18N = {
    'en': {
        'subtitle': 'AI Investment Advisor',
        'nav_opt': 'Portfolio Optimizer',
        'nav_backtest': 'Backtesting',
        'nav_ai': 'AI Advisor',
        'params_title': 'Investment Parameters',
        'label_tickers': 'Stock Tickers (comma separated)',
        'ph_tickers': 'e.g. FPT, VCB',
        'label_capital': 'Initial Capital (VND)',
        'ph_capital': 'e.g. 1,000,000,000',
        'label_return': 'Target Return (%)',
        'btn_run': 'Run Simulation',
        'btn_stress': '🔥 Stress Test',
        'main_title': 'Portfolio Status',
        'status_connected': 'Server Connected',
        'chart_title': 'Efficient Frontier & MC Simulation',
        'chart_desc': 'High-performance API: 10,000 Monte Carlo scenarios evaluated via Python Numpy matrices.',
        'metric_proj': 'Projected Expected Value',
        'metric_risk': 'Max Risk (VaR 95%)',
        'err_conn': 'Server Connection Failed',
        'err_wait': 'Waiting for Python Backend (FastAPI).<br>Run: uvicorn main:app --reload',
        'err_input': 'Alert: Please input both numbers correctly!',
        'disclaimer_title': '⚠️ Disclaimer:',
        'ai_disclaimer': 'AI analysis is strictly based on historical data and the latest financial reports. It cannot forecast sudden or unprecedented future events. Past performance is no guarantee of future results.',
        'ci_text': '95% Prob. Range:',
        'stress_drop': 'Crash -5% VN-Index: ',
        'loading_api': 'Computing Matrix...'
    },
    'vi': {
        'subtitle': 'Cố vấn Đầu tư AI',
        'nav_opt': 'Tối ưu Danh mục',
        'nav_backtest': 'Kiểm định Lịch sử',
        'nav_ai': 'Tiên tri AI (Gemini)',
        'params_title': 'Tham số Đầu tư',
        'label_tickers': 'Mã Cổ phiếu (Cách nhau dấu phẩy)',
        'ph_tickers': 'Ví dụ: FPT, MWG',
        'label_capital': 'Tiền vốn ban đầu (VNĐ)',
        'ph_capital': 'Ví dụ: 1,000,000,000',
        'label_return': 'Kỳ vọng Lợi nhuận (%)',
        'btn_run': 'Chạy Mô phỏng 🚀',
        'btn_stress': '🔥 Tắt Mù',
        'main_title': 'Tổng quan Danh mục',
        'status_connected': 'Đã kết nối Máy chủ',
        'chart_title': 'Biên Hiệu Quả & Mô Phỏng Monte Carlo',
        'chart_desc': 'API Chuyên nghiệp: Đưa 10,000 kịch bản ngẫu nhiên qua ma trận Numpy Python.',
        'metric_proj': 'Vốn Kỳ Vọng',
        'metric_risk': 'Rủi ro Tối đa (VaR 95%)',
        'err_conn': 'Chưa kết nối Server',
        'err_wait': 'Đang đợi đánh thức Backend Python.<br>Chạy lệnh: uvicorn main:app --reload',
        'err_input': 'Lưu ý (F0): Hệ thống báo bạn Nhập số chưa đúng định dạng!',
        'disclaimer_title': '⚠️ Lưu ý:',
        'ai_disclaimer': 'Phân tích của AI chỉ dựa trên dữ liệu lịch sử và báo cáo tài chính mới nhất. Hệ thống không thể dự báo các sự kiện biến thiên đột xuất. Hiệu suất trong quá khứ không đảm bảo cho kết quả trong tương lai.',
        'ci_text': 'Xác suất 95% biên độ:',
        'stress_drop': 'VNI Sập -5%: Bốc hơi ',
        'loading_api': 'Đang cày ma trận...'
    }
};

document.addEventListener("DOMContentLoaded", () => {
    
    // --- Ngôn ngữ (i18n) ---
    const langSelector = document.getElementById("lang-selector");
    let currentLang = 'en';

    function updateLanguage() {
        currentLang = langSelector.value;
        const dict = I18N[currentLang];
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            if (dict[key]) el.textContent = dict[key];
        });
        document.querySelectorAll("[data-i18n-ph]").forEach(el => {
            const key = el.getAttribute("data-i18n-ph");
            if (dict[key]) el.setAttribute("placeholder", dict[key]);
        });
    }
    
    langSelector.addEventListener("change", updateLanguage);
    updateLanguage(); 

    const apiStatus = document.getElementById("api-status");
    const statusDot = document.querySelector(".status-dot");
    const runBtn = document.getElementById("run-btn");
    const stressBtn = document.getElementById("stress-btn");

    let latestSimulationData = null;

    function formatVND(value) {
        return Math.floor(value).toLocaleString('vi-VN') + '₫';
    }

    function runSimulation() {
        const capInput = parseFloat(document.getElementById("capital-input").value);
        const retInput = parseFloat(document.getElementById("target-return").value) / 100;
        const tickersStr = document.getElementById("tickers-input").value;
        
        let tickersArray = tickersStr.split(',').map(s => s.trim().toUpperCase()).filter(s => s.length > 0);

        if (isNaN(capInput) || isNaN(retInput) || tickersArray.length < 2) {
            alert(I18N[currentLang]['err_input'] + " Hoặc cần ít nhất 2 mã cổ phiếu!");
            return;
        }

        runBtn.textContent = I18N[currentLang]['loading_api'];
        runBtn.disabled = true;

        const payload = {
            capital: capInput,
            target_return: retInput,
            tickers: tickersArray
        };

        fetch('http://127.0.0.1:8000/api/run-simulation', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) throw new Error("Connection failed");
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            
            latestSimulationData = data;
            
            // Vẽ biểu đồ Plotly
            Plotly.newPlot('chart-container', data.chart.data, data.chart.layout, { responsive: true, displayModeBar: false });
            
            // Xử lý Dải Xác Suất 95% (Confidence Interval)
            const mc = data.monte_carlo;
            const values = mc.monetary_values;
            
            const displayCap = document.getElementById("display-capital");
            displayCap.style.transform = "scale(1.1)";
            displayCap.textContent = formatVND(values.expected_value);
            
            const ciText = document.getElementById("ci-text");
            ciText.textContent = `${I18N[currentLang]['ci_text']} [${formatVND(values.ci_lower_value)} -> ${formatVND(values.ci_upper_value)}]`;
            
            const displayRisk = document.getElementById("display-risk");
            displayRisk.textContent = "-" + formatVND(Math.abs(values.var_value_loss));

            // Hiển thị nút Stress Test
            stressBtn.style.display = "inline-block";
            document.getElementById("stress-text").style.display = "none";
            
            // Cập nhật tín hiệu
            apiStatus.textContent = I18N[currentLang]['status_connected'] + " (100%)";
            statusDot.style.background = "var(--neon-green)";
            statusDot.style.boxShadow = "0 0 8px var(--neon-green)";

            setTimeout(() => { displayCap.style.transform = "scale(1)"; }, 200);
        })
        .catch(error => {
            console.error(error);
            apiStatus.textContent = I18N[currentLang]['err_conn'];
            statusDot.style.background = "var(--neon-alert)";
            statusDot.style.boxShadow = "0 0 8px var(--neon-alert)";
            document.getElementById('chart-container').innerHTML = `<p style="color: var(--neon-alert); text-align: center; margin-top: 50px;">${I18N[currentLang]['err_wait']}</p>`;
        })
        .finally(() => {
            runBtn.textContent = I18N[currentLang]['btn_run'];
            runBtn.disabled = false;
        });
    }

    runBtn.addEventListener("click", runSimulation);

    stressBtn.addEventListener("click", () => {
        if (!latestSimulationData) return;
        const lossVnd = latestSimulationData.stress_test.estimated_loss_vnd;
        
        const stressText = document.getElementById("stress-text");
        stressText.style.display = "block";
        stressText.style.transform = "scale(1.1)";
        stressText.textContent = `${I18N[currentLang]['stress_drop']} -${formatVND(Math.abs(lossVnd))}`;
        
        setTimeout(() => { stressText.style.transform = "scale(1)"; }, 300);
    });

    // Cố gắng render lần đầu nếu Backend đã bật (nhưng backend giờ cần payload, nên để trống cũng đc)
    // Sẽ báo dòng chữ "Đợi chạy..."
});
