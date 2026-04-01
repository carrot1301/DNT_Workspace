# HƯỚNG DẪN TÁC VỤ: NÂNG CẤP MÔ HÌNH QUANT VÀ TỐI ƯU GIAO DIỆN NGƯỜI DÙNG

## 1. Bối cảnh & Mục tiêu
Chúng ta cần nâng cấp logic tối ưu hóa cốt lõi và tinh chỉnh giao diện cho dự án **dnt_quant_lab**
Mô hình hiện tại đang gặp hiện tượng Quá khớp (Overfitting) khi tối ưu hóa danh mục, AI phân tích bỏ qua rủi ro sụt giảm cực đoan, và giao diện UI đang có một số "hạt sạn" về dịch thuật đa ngôn ngữ cũng như thiếu thông tin cập nhật dữ liệu.

**Mục tiêu:** Tái cấu trúc backend Python để quản trị rủi ro thực tế hơn, nâng cấp prompt của Gemini API, sửa lỗi localization (Anh-Việt) và bổ sung timestamp cho bảng giá.

## 2. Yêu cầu Kỹ thuật Chi tiết

### Tác vụ 2.1: Áp dụng Ràng buộc Tỷ trọng (Weight Constraints)
Cập nhật hàm `scipy.optimize.minimize` để ngăn chặn rủi ro tập trung quá mức.
* **Hành động:** Thêm tham số `bounds` vào hàm tối ưu hóa. Tỷ trọng tối thiểu = 5% (0.05), Tỷ trọng tối đa = 40% (0.40) cho mỗi tài sản.

### Tác vụ 2.2: Hiệu chỉnh Ma trận Hiệp phương sai (Covariance Shrinkage)
* **Hành động:** Thay thế hàm `.cov()` cơ bản của Pandas bằng phương pháp Ledoit-Wolf shrinkage từ thư viện `scikit-learn` để làm mượt các điểm nhiễu trong dữ liệu lịch sử 3 năm của HOSE.

### Tác vụ 2.3: Nâng cấp Template Prompt cho Gemini AI (Tập trung Quản trị Rủi ro)
* **Hành động:** Bổ sung chỉ thị sau vào system prompt: > "Trong vai trò là một Giám đốc Quản trị Rủi ro Định lượng khắt khe, bạn BẮT BUỘC phải đánh giá trực tiếp chỉ số 'Max Drawdown' (Mức sụt giảm tối đa). Hãy so sánh trực tiếp Max Drawdown này với Kỳ vọng lợi nhuận. Nếu Max Drawdown > 20%, phải cảnh báo người dùng về rủi ro tâm lý khi nắm giữ. Phân tích bài toán Đánh đổi: Liệu lợi nhuận kỳ vọng có xứng đáng với nguy cơ chia tài khoản từ đỉnh hay không?"

### Tác vụ 2.4: Chuẩn bị kiến trúc cho Black-Litterman
* **Hành động:** Thêm comment và cấu trúc code tại vị trí tính toán Expected Returns (CAPM) để sẵn sàng chèn "Góc nhìn người dùng" (Views) vào sau này, phục vụ việc chuyển đổi sang mô hình Black-Litterman.

### Tác vụ 2.5: Tối ưu hóa Dịch thuật UI (Anh - Việt)
Hệ thống hiện tại có lỗi dịch thuật: một số từ ngữ thông thường trên UI không được dịch từ tiếng Việt sang tiếng Anh khi người dùng chuyển đổi ngôn ngữ.
* **Hành động:** Rà soát lại logic i18n hoặc bộ từ điển (dictionary/mapping) của giao diện Streamlit. 
* **Yêu cầu:** Đảm bảo toàn bộ text (label, thông báo, text phụ trợ) được ánh xạ đầy đủ 2 ngôn ngữ. Giữ nguyên thuật ngữ chuyên ngành Quant bằng tiếng Anh nếu cần, nhưng các từ ngữ thông thường phải được dịch chuẩn xác theo state ngôn ngữ người dùng đang chọn.

### Tác vụ 2.6: Thêm Timestamp vào "Bảng Giá Đóng cửa"
Người dùng cần biết dữ liệu đang hiển thị thuộc phiên giao dịch nào.
* **Hành động:** Trích xuất ngày giao dịch gần nhất (latest trading date) từ DataFrame lịch sử giá.
* **Hiển thị:** Bổ sung một dòng text nhỏ phía trên hoặc bên dưới component "Bảng Giá Đóng cửa" với định dạng hiển thị là `Ngày - Tháng - Năm`.
* *Mã giả tham khảo:* `last_updated_str = df.index.max().strftime('%d-%m-%Y')` -> H `st.caption(f"Cập nhật lần cuối: {last_updated_str}")`

## 3. Quy tắc Đầu ra (Output Rules) dành cho AI
1. Đọc kỹ các file Python hiện tại (logic Quant và logic UI Streamlit).
2. Cung cấp code Python cập nhật cho Tác vụ 2.1, 2.2 và 2.6.
3. Cung cấp prompt template mới cho Tác vụ 2.3.
4. Sửa lại logic dictionary/translation cho Tác vụ 2.5.
5. Đảm bảo code chạy mượt mà, không làm vỡ layout của biểu đồ Efficient Frontier hay các component hiện tại.