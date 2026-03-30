document.addEventListener("DOMContentLoaded", () => {
    
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
                
                apiStatus.textContent = "Server: Connected & Sức mạnh 100%";
                statusDot.style.background = "var(--neon-green)";
                statusDot.style.boxShadow = "0 0 8px var(--neon-green)";
            })
            .catch(error => {
                console.error("API Error: ", error);
                apiStatus.textContent = "Lỗi kết nối Python Server";
                statusDot.style.background = "var(--neon-alert)";
                statusDot.style.boxShadow = "0 0 8px var(--neon-alert)";
                document.getElementById('chart-container').innerHTML = 
                    `<p style="color: var(--neon-alert); text-align: center; margin-top: 50px;">
                        Đang đợi đánh thức Backend Python (FastAPI).<br>Hãy chạy lệnh: uvicorn main:app --reload
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
            alert("Ví dụ (F0): Hệ thống báo bạn Nhập số đi nè!");
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
