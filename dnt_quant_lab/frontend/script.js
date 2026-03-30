const I18N = {
    'en': {
        'subtitle': 'AI Investment Advisor',
        'nav_opt': 'Portfolio Optimizer',
        'nav_backtest': 'Backtesting',
        'nav_ai': 'AI Advisor',
        'params_title': 'Investment Parameters',
        'label_capital': 'Initial Capital (VND)',
        'ph_capital': 'e.g. 1,000,000,000',
        'btn_run': 'Run Simulation',
        'main_title': 'Portfolio Status',
        'status_connected': 'Server Connected',
        'chart_title': 'Efficient Frontier (Demo)',
        'chart_desc': 'High-performance charts rendered natively via Python API.',
        'metric_proj': 'Projected Value',
        'metric_risk': 'Max Risk (VaR)',
        'err_conn': 'Server Connection Failed',
        'err_wait': 'Waiting for Python Backend (FastAPI).<br>Run: uvicorn main:app --reload',
        'err_input': 'Alert: Please input both numbers correctly!'
    },
    'vi': {
        'subtitle': 'Cố vấn Đầu tư AI',
        'nav_opt': 'Tối ưu Danh mục',
        'nav_backtest': 'Kiểm định Lịch sử',
        'nav_ai': 'Tiên tri AI (Gemini)',
        'params_title': 'Tham số Đầu tư',
        'label_capital': 'Tiền vốn ban đầu (VNĐ)',
        'ph_capital': 'Ví dụ: 1,000,000,000',
        'btn_run': 'Chạy Mô phỏng 🚀',
        'main_title': 'Tổng quan Danh mục',
        'status_connected': 'Đã kết nối Máy chủ',
        'chart_title': 'Biên Hiệu Quả (Bản Demo)',
        'chart_desc': 'Biểu đồ kết xuất tốc độ cao siêu nhẹ từ Backend Python.',
        'metric_proj': 'Vốn Dự phóng',
        'metric_risk': 'Rủi ro Tối đa (VaR)',
        'err_conn': 'Chưa kết nối Server',
        'err_wait': 'Đang đợi đánh thức Backend Python.<br>Chạy lệnh: uvicorn main:app --reload',
        'err_input': 'Lưu ý (F0): Hệ thống báo bạn Nhập số chưa đúng định dạng!'
    }
};

document.addEventListener("DOMContentLoaded", () => {
    
    // --- Ngôn ngữ (i18n) ---
    const langSelector = document.getElementById("lang-selector");
    let currentLang = 'en';

    function updateLanguage() {
        currentLang = langSelector.value;
        const dict = I18N[currentLang];
        
        // Cập nhật text content
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            if (dict[key]) el.textContent = dict[key];
        });
        
        // Cập nhật placeholder
        document.querySelectorAll("[data-i18n-ph]").forEach(el => {
            const key = el.getAttribute("data-i18n-ph");
            if (dict[key]) el.setAttribute("placeholder", dict[key]);
        });
        
        // Cập nhật hard-coded JS strings if possible...
    }
    
    langSelector.addEventListener("change", updateLanguage);
    updateLanguage(); // Chạy ngay lần đầu

    
    const apiStatus = document.getElementById("api-status");
    const statusDot = document.querySelector(".status-dot");
    const runBtn = document.getElementById("run-btn");
    
    // --- Lấy dữ liệu biểu đồ từ FastAPI Backend ---
    function fetchAndRenderChart() {
        // Địa chỉ mặc định của FastAPI chạy ở Localhost cổng 8000
        fetch('http://127.0.0.1:8000/api/demo-chart')
            .then(response => {
                if (!response.ok) throw new Error("Chưa kết nối Server");
                return response.json();
            })
            .then(figData => {
                // Plotly.js nhận Data và Layout từ JSON Python tạo ra
                Plotly.newPlot('chart-container', figData.data, figData.layout, { responsive: true, displayModeBar: false });
                
                apiStatus.textContent = I18N[currentLang]['status_connected'] + " (100%)";
                statusDot.style.background = "var(--neon-green)";
                statusDot.style.boxShadow = "0 0 8px var(--neon-green)";
            })
            .catch(error => {
                console.error("API Error: ", error);
                apiStatus.textContent = I18N[currentLang]['err_conn'];
                statusDot.style.background = "var(--neon-alert)";
                statusDot.style.boxShadow = "0 0 8px var(--neon-alert)";
                document.getElementById('chart-container').innerHTML = 
                    `<p style="color: var(--neon-alert); text-align: center; margin-top: 50px;">
                        ${I18N[currentLang]['err_wait']}
                    </p>`;
            });
    }

    // --- Tính toán nhanh (Interactivity ngay trên Browser) ---
    runBtn.addEventListener("click", () => {
        const capInput = document.getElementById("capital-input").value;
        const retInput = document.getElementById("target-return").value;
        
        let cap = parseFloat(capInput.replace(/,/g, ''));
        let ret = parseFloat(retInput) / 100;

        if (isNaN(cap) || isNaN(ret)) {
            alert(I18N[currentLang]['err_input']);
            return;
        }

        const expectedRtn = cap * (1 + ret);
        
        // Thêm hiệu ứng Update tức thời (Gen-Z Style)
        const displayCap = document.getElementById("display-capital");
        displayCap.style.transform = "scale(1.2)";
        displayCap.textContent = expectedRtn.toLocaleString('vi-VN') + '₫';
        
        setTimeout(() => {
            displayCap.style.transform = "scale(1)";
        }, 200);
        
        // Gọi API vẽ biểu đồ
        fetchAndRenderChart();
    });

    // Initial Load attempt
    fetchAndRenderChart();
});
