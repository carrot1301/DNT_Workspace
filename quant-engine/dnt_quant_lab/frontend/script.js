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
        'var_profitable_label': 'Still Profitable',
        'var_positive_tooltip': 'Even in the worst 5% scenario, portfolio is estimated to remain profitable – excellent portfolio quality!',
        'var_negative_tooltip': 'Maximum estimated loss at 95% confidence level.',
        'err_conn': 'Server Connection Failed',
        'err_wait': 'Waiting for Python Backend (FastAPI).<br>Run: uvicorn main:app --reload',
        'err_input': 'Alert: Please double check your numerical inputs!',
        'disclaimer_title': '⚠️ Disclaimer:',
        'ai_disclaimer': 'AI analysis is strictly based on historical data and the latest financial reports. It cannot forecast sudden or unprecedented future events. Past performance is no guarantee of future results.',
        'ci_text': '95% Prob. Range:',
        'stress_drop': 'Crash -5% VN-Index: ',
        'loading_api': 'Computing...',
        'ai_title': 'Gemini AI — Investment Insights',
        'ai_subtitle': 'Deep analysis based on 10,000 Monte Carlo scenarios',
        'ai_analyzing': 'Analyzing...',
        'ai_thinking': 'Gemini is processing data...',
        'ai_done': 'Analysis Complete',
        'backtest_title': 'Historical Performance (Backtest)',
        'backtest_desc': 'Portfolio historical cumulative returns compared to VNINDEX.',
        'allocation_title': 'Optimal Asset Allocation',
        'allocation_desc': 'Optimized capital distribution across selected stocks.',
        'raw_price_title': 'Closing Prices Table',
        'adv_metrics_title': 'Advanced Quant Metrics',
        'live_capital_label': 'Estimated Total Capital',
        'last_updated': 'Last updated: ',
        'welcome_title': 'Welcome to DNT Quant Lab',
        'welcome_desc': 'Enter your investment parameters and run the simulation to generate an AI-optimized portfolio.'
    },
    'vi': {
        'subtitle': 'Trợ lý Đầu tư AI',
        'nav_opt': 'Tối ưu hóa Danh mục',
        'nav_eval': 'Đánh giá Danh mục',
        'params_title': 'Thông số đầu vào',
        'eval_title': 'Danh mục hiện tại',
        'label_tickers': 'Mã cổ phiếu (ngăn cách bằng dấu phẩy)',
        'ph_tickers': 'Ví dụ: FPT, MWG, VCB',
        'label_capital': 'Vốn ban đầu (VNĐ)',
        'ph_capital': 'Ví dụ: 1.000.000.000',
        'label_return': 'Lợi nhuận kỳ vọng (%)',
        'btn_run': '🚀 Chạy mô phỏng',
        'btn_eval': '🔍 Đánh giá Danh mục',
        'btn_stress': '🔥 Stress Test',
        'btn_add_stock': '+ Thêm mã',
        'label_timeframe': 'Kỳ hạn',
        'tf_1m': '1 tháng (21 ngày giao dịch)',
        'tf_3m': '3 tháng (63 ngày giao dịch)',
        'tf_6m': '6 tháng (126 ngày giao dịch)',
        'tf_1y': '1 năm (252 ngày giao dịch)',
        'main_title': 'Tổng quan Danh mục',
        'status_connected': 'Đã kết nối máy chủ',
        'chart_title': 'Phân tích & Dự phóng',
        'chart_desc': 'Tính toán Monte Carlo qua Python API — 10.000 kịch bản ngẫu nhiên.',
        'metric_proj': 'Giá trị kỳ vọng',
        'metric_risk': 'Rủi ro tối đa (VaR 95%)',
        'var_profitable_label': 'Vẫn sinh lời',
        'var_positive_tooltip': 'Ở kịch bản xấu nhất 5% xác suất, danh mục ước tính vẫn có lãi – chất lượng danh mục tốt!',
        'var_negative_tooltip': 'Mức lỗ tối đa ước tính ở ngưỡng tin cậy 95%.',
        'err_conn': 'Mất kết nối với máy chủ',
        'err_wait': 'Không thể kết nối Backend Python (FastAPI).<br>Chạy lệnh: uvicorn main:app --reload',
        'err_input': 'Vui lòng kiểm tra lại dữ liệu nhập — cần ít nhất 2 mã cổ phiếu hợp lệ!',
        'disclaimer_title': '⚠️ Lưu ý quan trọng:',
        'ai_disclaimer': 'Kết quả phân tích chỉ dựa trên dữ liệu lịch sử và không phải là lời khuyên đầu tư. Hiệu suất trong quá khứ không đảm bảo cho kết quả tương lai. Nhà đầu tư tự chịu trách nhiệm về quyết định của mình.',
        'ci_text': 'Khoảng tin cậy 95%:',
        'stress_drop': 'VN-Index -5%: tổn thất ước tính ',
        'loading_api': 'Đang tính toán...',
        'ai_title': 'Gemini AI — Lời khuyên Đầu tư',
        'ai_subtitle': 'Phân tích chuyên sâu dựa trên 10.000 kịch bản Monte Carlo',
        'ai_analyzing': 'Đang phân tích...',
        'ai_thinking': 'Gemini đang xử lý dữ liệu...',
        'ai_done': 'Hoàn tất phân tích',
        'backtest_title': 'Hiệu suất Lịch sử (Backtest)',
        'backtest_desc': 'So sánh lợi nhuận tích lũy của danh mục với VN-Index.',
        'allocation_title': 'Phân bổ Tài sản Tối ưu',
        'allocation_desc': 'Tỉ trọng phân bổ vốn chi tiết cho từng mã cổ phiếu.',
        'raw_price_title': 'Bảng Giá Đóng cửa',
        'adv_metrics_title': 'Chỉ số Quant Nâng cao',
        'live_capital_label': 'Tổng Vốn Ước Tính',
        'last_updated': 'Cập nhật lần cuối: ',
        'welcome_title': 'Chào mừng đến với DNT Quant Lab',
        'welcome_desc': 'Nhập các thông số đầu tư và chạy mô phỏng để tạo danh mục được tối ưu hóa bởi AI.'
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
    const modeOpts = document.getElementById("mode-optimizer");
    const modeEval = document.getElementById("mode-evaluator");
    const modeFin = document.getElementById("mode-financial");
    
    function hideAllModes() {
        modeOpts.style.display = 'none';
        modeEval.style.display = 'none';
        if(modeFin) modeFin.style.display = 'none';
        navItems.forEach(el => el.classList.remove('active'));
    }

    navItems[0].addEventListener("click", () => {
        hideAllModes(); navItems[0].classList.add('active');
        modeOpts.style.display = 'block'; currentMode = 'optimizer';
    });
    navItems[1].addEventListener("click", () => {
        hideAllModes(); navItems[1].classList.add('active');
        modeEval.style.display = 'block'; currentMode = 'evaluator';
    });
    if(navItems[2]) {
        navItems[2].addEventListener("click", () => {
            hideAllModes(); navItems[2].classList.add('active');
            modeFin.style.display = 'block'; currentMode = 'financial';
        });
    }

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
        div.querySelector('.remove-btn').onclick = () => { div.remove(); onInputChanged(); };
        holdingsList.appendChild(div);
        attachInputListeners();
    });

    // --- Live Capital (Debounce Live Pricing) ---
    let typingTimer;
    let cachedPrices = {};
    
    function attachInputListeners() {
        const inputs = document.querySelectorAll(".holding-row input");
        inputs.forEach(input => {
            input.removeEventListener('input', onInputChanged); // prevent duplicate bindings
            input.addEventListener('input', onInputChanged);
        });
    }

    function onInputChanged() {
        clearTimeout(typingTimer);
        document.getElementById("live-capital-display").textContent = "...";
        typingTimer = setTimeout(calculateLiveCapital, 600);
    }

    async function calculateLiveCapital() {
        const rows = document.querySelectorAll(".holding-row");
        let queryTickers = [];
        let holdings = [];
        
        for(let row of rows) {
            let t = row.querySelector('.t-input').value.trim().toUpperCase();
            let v = parseFloat(row.querySelector('.v-input').value);
            if (t) {
                queryTickers.push(t);
                if (!isNaN(v)) holdings.push({t, v});
            }
        }
        
        if (queryTickers.length === 0) {
            document.getElementById("live-capital-display").textContent = "0₫";
            return;
        }
        
        let tickersQueryStr = queryTickers.join(",");
        try {
            let res = await fetch('/api/current-prices?tickers=' + tickersQueryStr);
            let prices = await res.json();
            
            Object.assign(cachedPrices, prices);
            
            let total = 0;
            for (let h of holdings) {
                if (cachedPrices[h.t]) {
                    total += cachedPrices[h.t] * h.v;
                }
            }
            document.getElementById("live-capital-display").textContent = formatVND(total);
        } catch (e) {
            console.error("Lỗi cập nhật giá realtime:", e);
        }
    }

    // --- Currency Formatting for Capital Input ---
    const capitalInput = document.getElementById("capital-input");
    if (capitalInput) {
        capitalInput.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^0-9]/g, "");
            if (value) {
                e.target.value = parseInt(value).toLocaleString("vi-VN");
            } else {
                e.target.value = "";
            }
        });
    }
    
    // Call initial listener
    attachInputListeners();

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
        
        // Hide welcome message on first result
        const welcome = document.getElementById("welcome-message");
        if (welcome) welcome.style.display = "none";

        if (data.chart) {
            Plotly.react('chart-container', data.chart.data, data.chart.layout, { responsive: true, displayModeBar: false });
            document.getElementById('main-chart-card').style.display = 'block';
        } else {
            // Hide main chart on Evaluator Mode
            const mainCard = document.getElementById('main-chart-card');
            if(mainCard) mainCard.style.display = 'none';
        }
        
        if (data.backtest_chart) {
            document.getElementById('backtest-card').style.display = 'block';
            Plotly.react('backtest-chart-container', data.backtest_chart.data, data.backtest_chart.layout, { responsive: true, displayModeBar: false });
        }
        
        if (data.pie_chart) {
            document.getElementById('pie-card').style.display = 'block';
            Plotly.react('pie-chart-container', data.pie_chart.data, data.pie_chart.layout, { responsive: true, displayModeBar: false });
        }
        
        if (data.raw_prices) {
            document.getElementById('raw-prices-card').style.display = 'block';
            if (data.last_updated_date) {
                document.getElementById('timestamp-date').textContent = data.last_updated_date;
            }
            const tbody = document.getElementById('raw-prices-tbody');
            tbody.innerHTML = '';
            for (const [ticker, price] of Object.entries(data.raw_prices)) {
                tbody.innerHTML += `<tr><td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05);">${ticker}</td><td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); color:var(--neon);">${formatVND(price)}</td></tr>`;
            }
        }

        if (data.advanced_metrics) {
            document.getElementById('advanced-metrics-card').style.display = 'block';
            document.getElementById('metric-beta').textContent = data.advanced_metrics.beta != null ? data.advanced_metrics.beta.toFixed(2) : '--';
            document.getElementById('metric-sortino').textContent = data.advanced_metrics.sortino != null ? data.advanced_metrics.sortino.toFixed(2) : '--';
            document.getElementById('metric-treynor').textContent = data.advanced_metrics.treynor != null ? data.advanced_metrics.treynor.toFixed(4) : '--';
            document.getElementById('metric-rsq').textContent = data.advanced_metrics.r_squared != null ? data.advanced_metrics.r_squared.toFixed(2) : '--';
            document.getElementById('metric-calmar').textContent = data.advanced_metrics.calmar != null ? data.advanced_metrics.calmar.toFixed(2) : '--';
            document.getElementById('metric-mdd').textContent = data.advanced_metrics.max_drawdown != null ? (data.advanced_metrics.max_drawdown * 100).toFixed(2) + '%' : '--';
        }
        
        const mc = data.monte_carlo;
        const values = mc.monetary_values;
        
        const displayCap = document.getElementById("display-capital");
        displayCap.style.transform = "scale(1.1)";
        displayCap.textContent = formatVND(values.expected_value);
        
        const ciText = document.getElementById("ci-text");
        ciText.textContent = `${I18N[currentLang]['ci_text']} [${formatVND(values.ci_lower_value)} -> ${formatVND(values.ci_upper_value)}]`;
        
        const displayRisk = document.getElementById("display-risk");
        const varLoss = values.var_value_loss;
        const varLossAbs = Math.abs(varLoss);
        if (varLoss >= 0) {
            // VaR dương: ở kịch bản xấu nhất 5%, danh mục vẫn có lãi
            displayRisk.textContent = varLossAbs < 1 ? I18N[currentLang]['var_profitable_label'] : "+" + formatVND(varLoss);
            displayRisk.style.color = "var(--neon-green)";
            displayRisk.title = I18N[currentLang]['var_positive_tooltip'];
        } else {
            // VaR âm: ở kịch bản xấu nhất 5%, danh mục bị lỗ
            const lossDisplay = varLossAbs < 1 ? "~0₫" : "-" + formatVND(varLossAbs);
            displayRisk.textContent = lossDisplay;
            displayRisk.style.color = "var(--neon-alert)";
            displayRisk.title = I18N[currentLang]['var_negative_tooltip'];
        }

        stressBtn.style.display = "inline-block";
        document.getElementById("stress-text").style.display = "none";
        
        apiStatus.textContent = I18N[currentLang]['status_connected'] + " (100%)";
        statusDot.style.background = "var(--neon-green)";
        statusDot.style.boxShadow = "0 0 8px var(--neon-green)";

        setTimeout(() => { displayCap.style.transform = "scale(1)"; }, 200);

        // --- NEW: Trigger AI Advice Automatically ---
        fetchAIAdvice(data);
    }

    async function fetchAIAdvice(data) {
        const aiCard = document.getElementById("ai-advice-card");
        const aiText = document.getElementById("ai-text");
        const aiLoading = document.getElementById("ai-loading");
        const aiBadge = document.getElementById("ai-badge");
        const aiBadgeText = document.getElementById("ai-badge-text");

        // Reset & Show Card
        aiCard.style.display = "block";
        aiText.innerHTML = "";
        aiLoading.style.display = "flex";
        aiBadge.classList.remove("done");
        aiBadgeText.textContent = I18N[currentLang]['ai_analyzing'];

        try {
            const response = await fetch('/api/ai-advice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    monte_carlo: data.monte_carlo,
                    stress_test: data.stress_test,
                    advanced_metrics: data.advanced_metrics,
                    lang: currentLang
                })
            });

            if (!response.ok) throw new Error("AI API Error");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            aiLoading.style.display = "none";
            
            // Add typing cursor
            const cursor = document.createElement("span");
            cursor.className = "ai-cursor";
            aiText.appendChild(cursor);

            let fullText = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                fullText += chunk;
                
                // Simple Markdown-ish formatting as we stream
                // Replacing **bold** and *italic* and newlines
                let formatted = fullText
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                    .replace(/\n/g, '<br>');
                
                aiText.innerHTML = formatted;
                aiText.appendChild(cursor);
                
                // Auto-scroll to bottom if needed
                aiCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }

            // Finish
            cursor.remove();
            aiBadge.classList.add("done");
            aiBadgeText.textContent = I18N[currentLang]['ai_done'];

        } catch (err) {
            console.error("AI Advice Error:", err);
            aiLoading.style.display = "none";
            aiText.innerHTML = `<span style="color: var(--neon-alert)">⚠️ Error: Không thể kết nối Gemini AI. Kiểm tra .env hoặc API Key.</span>`;
        }
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
        const rawCap = document.getElementById("capital-input").value.replace(/\./g, "");
        const capInput = parseFloat(rawCap);
        const retInput = parseFloat(document.getElementById("target-return").value) / 100;
        const tickersStr = document.getElementById("tickers-input").value;
        let tickersArray = tickersStr.split(',').map(s => s.trim().toUpperCase()).filter(s => s.length > 0);

        if (isNaN(capInput) || isNaN(retInput) || tickersArray.length < 2) {
            alert(I18N[currentLang]['err_input']); return;
        }

        runBtn.textContent = I18N[currentLang]['loading_api']; runBtn.disabled = true;

        fetch('/api/run-simulation', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({capital: capInput, target_return: retInput, tickers: tickersArray, lang: currentLang})
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

        fetch('/api/evaluate-portfolio', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({holdings: holdings, days: tf, lang: currentLang})
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

    // --- Financial Reports & SePay Paywall Logic ---
    let currentSessionId = localStorage.getItem('dnt_session_id');
    if (!currentSessionId) {
        currentSessionId = 'S' + Math.random().toString(36).substr(2, 9).toUpperCase();
        localStorage.setItem('dnt_session_id', currentSessionId);
    }
    let pollingInterval = null;

    const finBtn = document.getElementById('fin-view-btn');
    if (finBtn) {
        finBtn.addEventListener('click', async () => {
            const ticker = document.getElementById('fin-ticker-input').value.trim();
            if (!ticker) return alert("Vui lòng nhập mã cổ phiếu!");
            
            finBtn.textContent = 'Fetching...';
            try {
                const res = await fetch(`/api/financials/${ticker}?session_id=${currentSessionId}`);
                const data = await res.json();
                
                if (data.error) throw new Error(data.error);

                document.getElementById('fin-report-card').style.display = 'block';
                document.getElementById('fin-ticker').textContent = data.ticker;
                document.getElementById('fin-pepb').textContent = `${data.pe.toFixed(2)} | ${data.pb.toFixed(2)}`;
                document.getElementById('fin-industry').textContent = data.industry || '--';
                document.getElementById('fin-marketcap').textContent = data.marketCap ? (data.marketCap).toLocaleString() : '--';
                
                // Fields
                renderPaywallField('fin-roe', data.roe, data.roa, data.is_paid, '% | ', '%');
                renderPaywallField('fin-debt', data.debt_on_equity, '', data.is_paid, ' Lần', '');
                renderPaywallField('fin-profit', data.profit_growth, '', data.is_paid, '% (YoY)', '');
                
            } catch (err) {
                alert(err.message);
            } finally {
                finBtn.textContent = 'Fetch Data';
            }
        });
    }

    function renderPaywallField(id, val1, val2, isPaid, unit1='', unit2='') {
        const el = document.getElementById(id);
        const container = el.closest('.blur-box');
        const overlay = container.querySelector('.pay-overlay');
        
        if (isPaid) {
            el.style.filter = 'none';
            if(overlay) overlay.style.display = 'none';
            let txt = val1 + unit1;
            if(val2) txt += val2 + unit2;
            el.textContent = txt;
        } else {
            el.style.filter = 'blur(6px)';
            if(overlay) overlay.style.display = 'flex';
            el.textContent = "LOCKED";
        }
    }

    // Modal Handle
    const unlockBtns = document.querySelectorAll('.unlock-btn');
    const qrModal = document.getElementById('qr-modal');
    const closeQr = document.getElementById('close-qr-btn');
    const qrImg = document.getElementById('vietqr-img');

    unlockBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Generate VietQR Link
            // STK: 1001213140604, Ngân hàng VPB (VPBank), DOAN NGUYEN TRI
            const msg = `DNTLAB ${currentSessionId}`;
            const amount = 5000;
            // Dùng img.vietqr.io
            const qrUrl = `https://img.vietqr.io/image/VPB-1001213140604-compact2.jpg?amount=${amount}&addInfo=${msg}&accountName=DOAN%20NGUYEN%20TRI`;
            qrImg.src = qrUrl;
            qrModal.style.display = 'flex';
            
            // Start Polling
            startPaymentPolling();
        });
    });

    closeQr.addEventListener('click', () => {
        qrModal.style.display = 'none';
        if(pollingInterval) clearInterval(pollingInterval);
    });

    async function startPaymentPolling() {
        if(pollingInterval) clearInterval(pollingInterval);
        
        pollingInterval = setInterval(async () => {
            try {
                const res = await fetch(`/api/payment-status?session_id=${currentSessionId}`);
                const data = await res.json();
                
                if(data.paid) {
                    clearInterval(pollingInterval);
                    alert("Cảm ơn bạn! Thanh toán 5.000 VNĐ đã được SePay ghi nhận thành công.");
                    qrModal.style.display = 'none';
                    // Auto refetch data to unblur
                    if(document.getElementById('fin-ticker').textContent !== '--') {
                        document.getElementById('fin-view-btn').click(); 
                    }
                }
            } catch(e) {}
        }, 3000); // Mỗi 3 giây
    }

});
