# BÁO CÁO CẬP NHẬT DNT QUANT LAB
**Ngày cập nhật: 13/04/2026**

## Nội dung cập nhật chính
Bản cập nhật tập trung vào việc nâng cấp thuật toán định lượng (Quant Engine) để xử lý và định giá tự động lộ trình nâng hạng thị trường của FTSE Russell từ Frontier Market lên Emerging Market (Chia làm 4 đợt từ T9/2026 đến T9/2027). Việc chỉ sử dụng Portfolio Optimization theo Markowitz tĩnh đã được thay thế bằng mô hình Black-Litterman hướng sự kiện.

### 1. Nâng cấp cốt lõi (Backend Core - `portfolio_opt.py`)
- **Tích hợp thuật toán Black-Litterman (Bayersian Model)**: Hoàn thiện phương trình tái phân bổ tỷ trọng từ Lợi nhuận cơ sở (Implied Returns) và Góc nhìn vĩ mô (Macro Views). 
- **Tạo hàm Views tự sinh `generate_ftse_views`**: Gán cứng danh sách 25 cổ phiếu được hưởng lợi tốt nhất từ đợt nâng hạng (bao gồm *VIC, VHM, HPG, FPT, SSI, MSN, VCB, VNM, VJC, VIX, STB, VRE, SHB, GEX, VCI, KDH, KBC, BID, NVL, DGC, EIB, PDR, DXG, DIG, DPM*).
- **Phân bổ tỷ suất Alpha theo Thời hạn dự phóng (Timeframe)**:
  - Dưới 6 tháng: +5% Lợi nhuận siêu ngạch.
  - Từ 6 - 12 tháng: +8% Lợi nhuận siêu ngạch.
  - Trên 12 tháng (kéo qua nhiều pha nâng hạng): +12% Lợi nhuận siêu ngạch.
- **Mở rộng API Payload**: Hàm `run_monte_carlo` nay trả về trực tiếp Ma trận *P* (Pick Matrix) và *Q* (View Vector) dưới node JSON `black_litterman_event` để Frontend có thể trực quan hóa sự thiên lệch về dòng tiền đối với các mã trụ này.

### 2. Nâng cấp Trợ lý AI (AI Advisor - `ai_advisor.py`)
- **Tích hợp cờ tín hiệu (Flagging)**: Bắt tín hiệu cờ `is_bl_active` từ kết quả thuật toán Black-Litterman.
- **Điều chỉnh System Prompt thông minh**: Bổ sung Context cho AI để nó tự nhận thức được việc các tỷ trọng (weights) vừa được hệ thống Quant tái tính toán dựa trên câu chuyện hút tiền ngoại thông qua FTSE. Từ đó AI sẽ trình bày rõ ràng hơn cho khách hàng, tránh việc lý giải tỷ trọng thuần túy theo Volatility/Alpha truyền thống.

## Kế hoạch cho bước tiếp theo
- Triển khai cập nhật Frontend (React/HTMLJS) để đọc trường `black_litterman_event` và vẽ biểu đồ 2D Scatter Plot hoặc Bar Chart thể hiện "Lợi nhuận được định giá lại" ngay trên giao diện cho người dùng so sánh.

--- 
*Báo cáo được khởi tạo tự động bởi hệ thống Quản lý DNT Quant Lab.*
