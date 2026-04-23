document.addEventListener("DOMContentLoaded", () => {
    // Demo Modal Popup for inner pages
    const showGuide = sessionStorage.getItem('fintopGuideShown');
    
    if(!showGuide && window.location.pathname.includes('fintop-data')) {
        createGuidePopup();
        sessionStorage.setItem('fintopGuideShown', 'true');
    }
});

function createGuidePopup() {
    const overlay = document.createElement('div');
    overlay.className = 'guide-overlay';
    overlay.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.5); backdrop-filter: blur(4px);
        display: flex; align-items: center; justify-content: center; z-index: 10000;
        opacity: 0; transition: opacity 0.3s;
    `;
    
    const modal = document.createElement('div');
    modal.style.cssText = `
        background: #fff; padding: 2rem; border-radius: 12px; max-width: 500px;
        color: #1E1B4B; box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        transform: translateY(20px); transition: all 0.3s;
    `;
    
    modal.innerHTML = `
        <h3 style="margin-bottom: 1rem; color: #7C3AED;">HƯỚNG DẪN SỬ DỤNG</h3>
        <p style="margin-bottom: 1.5rem; color: #475569; font-size: 0.95rem;">Bảng tổng hợp danh mục cổ phiếu theo Trạng thái và Kết quả thuật toán của Mô hình (Model). Vui lòng sử dụng kết hợp với các chỉ báo kỹ thuật khác.</p>
        <hr style="border:none; border-top: 1px solid #E5E7F0; margin-bottom: 1.5rem;">
        <div style="font-size: 0.8rem; color: #94A3B8; margin-bottom: 1.5rem;">
            <strong>MIỄN TRỪ TRÁCH NHIỆM:</strong> Dữ liệu chỉ mang tính chất tham khảo, không phải khuyến nghị đầu tư. Người dùng chịu hoàn toàn trách nhiệm trước các quyết định đầu tư của mình.
        </div>
        <button id="closeGuide" style="width: 100%; background: #7C3AED; color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold;">Đã hiểu, tiếp tục</button>
    `;
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    // Animate in
    setTimeout(() => {
        overlay.style.opacity = '1';
        modal.style.transform = 'translateY(0)';
    }, 100);
    
    // Event listener
    document.getElementById('closeGuide').addEventListener('click', () => {
        overlay.style.opacity = '0';
        modal.style.transform = 'translateY(20px)';
        setTimeout(() => overlay.remove(), 300);
    });
}
