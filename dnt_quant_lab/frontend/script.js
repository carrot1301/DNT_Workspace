const I18N = {
    'en': {
        'subtitle': 'AI Investment Advisor',
        'nav_opt': 'Portfolio Optimizer',
        'nav_eval': 'Portfolio Evaluator',
        'params_title': 'Investment Parameters',
        'eval_title': 'My Custom Portfolio',
        'label_tickers': 'Stock Tickers (comma separated)',
        'ph_tickers': 'e.g. FPT, VCB',
        'label_capital': 'Initial Capital (VND)',
        'ph_capital': 'e.g. 1,000,000,000',
        'label_return': 'Target Return (%)',
        'btn_run': 'Run Simulation',
        'btn_eval': 'Evaluate Portfolio 🔍',
        'btn_stress': '🔥 Stress Test',
        'btn_add_stock': '+ Add Stock',
        'label_timeframe': 'Timeframe',
        'tf_1m': '1 Month (21 Days)',
        'tf_3m': '3 Months (63 Days)',
        'tf_6m': '6 Months (126 Days)',
        'tf_1y': '1 Year (252 Days)',
        'main_title': 'Portfolio Status',
        'status_connected': 'Server Connected',
        'chart_title': 'Analysis & Projections',
        'chart_desc': 'High-performance API: Calculated natively via Python arrays.',
        'metric_proj': 'Projected Expected Value',
        'metric_risk': 'Max Risk (VaR 95%)',
        'err_conn': 'Server Connection Failed',
        'err_wait': 'Waiting for Python Backend (FastAPI).<br>Run: uvicorn main:app --reload',
        'err_input': 'Alert: Please double check your numerical inputs!',
        'disclaimer_title': '⚠️ Disclaimer:',
        'ai_disclaimer': 'AI analysis is strictly based on historical data and the latest financial reports. It cannot forecast sudden or unprecedented future events. Past performance is no guarantee of future results.',
        'ci_text': '95% Prob. Range:',
        'stress_drop': 'Crash -5% VN-Index: ',
        'loading_api': 'Computing...'
    },
    'vi': {
        'subtitle': 'Cố vấn Đầu tư AI',
        'nav_opt': 'Tối ưu Danh mục',
        'nav_eval': 'Khám Bệnh Danh Mục',
        'params_title': 'Tham số Cố định',
        'eval_title': 'Danh mục Đang kẹp',
        'label_tickers': 'Mã Cổ phiếu (Cách nhau dấu phẩy)',
        'ph_tickers': 'Ví dụ: FPT, MWG',
        'label_capital': 'Tiền vốn ban đầu (VNĐ)',
        'ph_capital': 'Ví dụ: 1,000,000,000',
        'label_return': 'Kỳ vọng Lợi nhuận (%)',
        'btn_run': 'Chạy Mô phỏng 🚀',
        'btn_eval': 'Khám Bệnh Danh Mục 🔍',
        'btn_stress': '🔥 Tắt Mù',
        'btn_add_stock': '+ Thêm Mã Phụ',
        'label_timeframe': 'Kỳ hạn (Timeframe)',
        'tf_1m': '1 Tháng (21 Ngày GD)',
        'tf_3m': '3 Tháng (63 Ngày GD)',
        'tf_6m': '6 Tháng (126 Kh GD)',
        'tf_1y': '1 Năm (252 Ngày GD)',
        'main_title': 'Tổng quan Danh mục',
        'status_connected': 'Đã kết nối Máy chủ',
        'chart_title': 'Phân tích & Dự phóng',
        'chart_desc': 'API Chuyên nghiệp: Điểm chạm máy chủ Python siêu tốc.',
        'metric_proj': 'Vốn Kỳ Vọng',
        'metric_risk': 'Rủi ro Tối đa (VaR 95%)',
        'err_conn': 'Chưa kết nối Server',
        'err_wait': 'Đang đợi đánh thức Backend Python.<br>Chạy lệnh: uvicorn main:app --reload',
        'err_input': 'Lưu ý (F0): Hệ thống báo bạn Nhập số hoặc Mã chưa đúng định dạng!',
        'disclaimer_title': '⚠️ Lưu ý:',
        'ai_disclaimer': 'Phân tích của AI chỉ dựa trên dữ liệu lịch sử và báo cáo tài chính mới nhất. Hệ thống không thể dự báo các sự kiện biến thiên đột xuất. Hiệu suất trong quá khứ không đảm bảo cho kết quả trong tương lai.',
        'ci_text': 'Xác suất 95% biên độ:',
        'stress_drop': 'VNI Sập -5%: Bốc hơi ',
        'loading_api': 'Đang tính toán...'
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

    // --- Tab Switch Logic ---
    let currentMode = 'optimizer';
    const navItems = document.querySelectorAll(".nav-menu .nav-item");
    navItems[0].addEventListener("click", () => {
        navItems[0].classList.add('active'); navItems[1].classList.remove('active');
        document.getElementById("mode-optimizer").style.display = 'block';
        document.getElementById("mode-evaluator").style.display = 'none';
        currentMode = 'optimizer';
    });
    navItems[1].addEventListener("click", () => {
        navItems[1].classList.add('active'); navItems[0].classList.remove('active');
        document.getElementById("mode-evaluator").style.display = 'block';
        document.getElementById("mode-optimizer").style.display = 'none';
        currentMode = 'evaluator';
    });

    // --- Evaluator Dynamic Rows ---
    const addRowBtn = document.getElementById("add-holding-btn");
    const holdingsList = document.getElementById("holdings-list");
    addRowBtn.addEventListener("click", () => {
        const div = document.createElement("div");
        div.className = "holding-row";
        div.style.cssText = "display: flex; gap: 5px; margin-bottom: 5px;";
        div.innerHTML = `
            <input type="text" class="glass-input t-input" placeholder="Ticker" style="width: 50%;">
            <input type="number" class="glass-input v-input" placeholder="Qty" style="width: 40%;">
            <button class="remove-btn" style="background:var(--neon-alert); color:white; border:none; border-radius:4px; width: 10%; font-weight:bold; cursor:pointer;">X</button>
        `;
        div.querySelector('.remove-btn').onclick = () => div.remove();
        holdingsList.appendChild(div);
    });

    // --- Common API Handlers ---
    const apiStatus = document.getElementById("api-status");
    const statusDot = document.querySelector(".status-dot");
    const runBtn = document.getElementById("run-btn");
    const evalBtn = document.getElementById("eval-btn");
    const stressBtn = document.getElementById("stress-btn");

    let latestSimulationData = null;

    function formatVND(value) {
        return Math.floor(value).toLocaleString('vi-VN') + '₫';
    }

    function handleApiResponse(data) {
        if (data.error) {
            alert(data.error);
            return;
        }
        
        latestSimulationData = data;
        
        Plotly.newPlot('chart-container', data.chart.data, data.chart.layout, { responsive: true, displayModeBar: false });
        
        const mc = data.monte_carlo;
        const values = mc.monetary_values;
        
        const displayCap = document.getElementById("display-capital");
        displayCap.style.transform = "scale(1.1)";
        displayCap.textContent = formatVND(values.expected_value);
        
        const ciText = document.getElementById("ci-text");
        ciText.textContent = `${I18N[currentLang]['ci_text']} [${formatVND(values.ci_lower_value)} -> ${formatVND(values.ci_upper_value)}]`;
        
        const displayRisk = document.getElementById("display-risk");
        displayRisk.textContent = "-" + formatVND(Math.abs(values.var_value_loss));

        stressBtn.style.display = "inline-block";
        document.getElementById("stress-text").style.display = "none";
        
        apiStatus.textContent = I18N[currentLang]['status_connected'] + " (100%)";
        statusDot.style.background = "var(--neon-green)";
        statusDot.style.boxShadow = "0 0 8px var(--neon-green)";

        setTimeout(() => { displayCap.style.transform = "scale(1)"; }, 200);
    }

    function handleError(error) {
        console.error(error);
        apiStatus.textContent = I18N[currentLang]['err_conn'];
        statusDot.style.background = "var(--neon-alert)";
        statusDot.style.boxShadow = "0 0 8px var(--neon-alert)";
        document.getElementById('chart-container').innerHTML = `<p style="color: var(--neon-alert); text-align: center; margin-top: 50px;">${I18N[currentLang]['err_wait']}</p>`;
    }

    // Execution Mode: Optimizer
    runBtn.addEventListener("click", () => {
        const capInput = parseFloat(document.getElementById("capital-input").value);
        const retInput = parseFloat(document.getElementById("target-return").value) / 100;
        const tickersStr = document.getElementById("tickers-input").value;
        let tickersArray = tickersStr.split(',').map(s => s.trim().toUpperCase()).filter(s => s.length > 0);

        if (isNaN(capInput) || isNaN(retInput) || tickersArray.length < 2) {
            alert(I18N[currentLang]['err_input']); return;
        }

        runBtn.textContent = I18N[currentLang]['loading_api']; runBtn.disabled = true;

        fetch('http://127.0.0.1:8000/api/run-simulation', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({capital: capInput, target_return: retInput, tickers: tickersArray})
        })
        .then(res => res.json()).then(handleApiResponse).catch(handleError)
        .finally(() => { runBtn.textContent = I18N[currentLang]['btn_run']; runBtn.disabled = false; });
    });

    // Execution Mode: Evaluator
    evalBtn.addEventListener("click", () => {
        const rows = document.querySelectorAll(".holding-row");
        let holdings = {};
        for(let row of rows) {
            let t = row.querySelector('.t-input').value.trim().toUpperCase();
            let v = parseFloat(row.querySelector('.v-input').value);
            if(t && !isNaN(v)) holdings[t] = v;
        }

        const tf = parseInt(document.getElementById("timeframe-select").value);

        if (Object.keys(holdings).length === 0) {
            alert(I18N[currentLang]['err_input']); return;
        }

        evalBtn.textContent = I18N[currentLang]['loading_api']; evalBtn.disabled = true;

        fetch('http://127.0.0.1:8000/api/evaluate-portfolio', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({holdings: holdings, days: tf})
        })
        .then(res => res.json()).then(handleApiResponse).catch(handleError)
        .finally(() => { evalBtn.textContent = I18N[currentLang]['btn_eval']; evalBtn.disabled = false; });
    });

    // Stress Test Button
    stressBtn.addEventListener("click", () => {
        if (!latestSimulationData || !latestSimulationData.stress_test) return;
        const lossVnd = latestSimulationData.stress_test.estimated_loss_vnd;
        
        const stressText = document.getElementById("stress-text");
        stressText.style.display = "block";
        stressText.style.transform = "scale(1.1)";
        stressText.textContent = `${I18N[currentLang]['stress_drop']} -${formatVND(Math.abs(lossVnd))}`;
        
        setTimeout(() => { stressText.style.transform = "scale(1)"; }, 300);
    });

});
