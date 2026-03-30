# VN30 Quant Analyzer - Chuyện phía sau Data Pipeline 🚀

Chào mọi người! Dưới đây là chút chia sẻ của em về cách ứng dụng này tự động thu thập và xử lý dữ liệu chứng khoán ở hậu đài. Khi mới bắt tay vào code chiếc dashboard định lượng này, em đã gặp không ít bài toán "đau đầu" về Data Pipeline. Và đây là cách em đã từng bước giải quyết chúng!

## 1. Tự động hóa 100% - Tạm biệt việc tải file thủ công
Thú thật là thời gian đầu, để lấy dữ liệu OHLCV (Mở/Cao/Thấp/Đóng/Khối lượng) của rổ VN30, ngày nào em cũng phải lóc cóc lên các trang chuyên dữ liệu để tải file Excel về. Sau đó lại mất công viết code làm sạch rồi lưu thành file CSV cho Pandas đọc. Cách làm thủ công này thực sự tốn thời gian và khó có thể duy trì lâu dài.

Em từng định chuyển sang dùng các thư viện Python tiện lợi như `yfinance` hay `vnstock`. Nhưng thực tế lại phát sinh vấn đề: `yfinance` lấy data chứng khoán Việt Nam đôi khi bị thiếu ngày hoặc sai giá; còn `vnstock` (bản v3) lại yêu cầu Token và có giới hạn số lượng request đối với tài khoản miễn phí.

**Cách giải quyết của em:** Tự build một **Custom API Fetcher**! 
Bộ fetcher nhỏ gọn này được viết bằng `requests`, gọi trực tiếp tới API đồ thị public của chứng khoán DNSE (Entrade). Nhờ vậy, ứng dụng lấy được data từ nguồn chuẩn với những ưu điểm:
* **Hoàn toàn miễn phí và ẩn danh:** Không cần tạo tài khoản hay phải nhúng API Key vào code.
* **Tự động hóa hoàn toàn:** Code sẽ tự động cập nhật dữ liệu lịch sử giá mới nhất mỗi ngày.

## 2. Tối ưu hiệu suất và tránh "Block IP" bằng Smart Caching
Khi tự động gọi API, rủi ro lớn nhất là vướng phải **Rate Limit**. Giả sử ứng dụng có 1.000 user truy cập cùng lúc, mỗi người lại kích hoạt một luồng gọi API đến DNSE, IP Server của em chắc chắn sẽ bị đưa vào "danh sách đen" (Blacklist) ngay lập tức.

Để xử lý bài toán này, em đã thiết kế một lớp bộ nhớ đệm (cache) bằng decorator `@st.cache_data(ttl=86400)` rất hiệu quả của Streamlit. 

**Cách thức hoạt động:** Khi người dùng đầu tiên truy cập vào web trong ngày, ứng dụng sẽ kéo toàn bộ lịch sử 3 năm của từng cổ phiếu về, nhưng chỉ thực hiện **đúng 1 lần duy nhất**. Dữ liệu sau khi xử lý thành DataFrame sẽ được lưu ngay vào RAM của máy chủ và giữ nguyên trong suốt 24 giờ. 
Với 999 người dùng truy cập sau đó, tốc độ tải trang chỉ tính bằng mili-giây vì dữ liệu được đọc trực tiếp từ RAM, không gửi thêm bất kỳ request nào lên server của nhà cung cấp API nữa. Nhờ vậy, ứng dụng hoạt động vừa mượt mà, vừa an toàn.

## 3. Xử lý độ lệch thời gian và chuẩn hóa dữ liệu
Trong phân tích định lượng (Quant), để chạy mô hình tính toán các chỉ số quan trọng như Beta và Alpha, em cần ghép nối (Inner Join) biến động giá của một cổ phiếu với biến động của thị trường chung (VNINDEX) trên cùng một trục thời gian.

Tuy nhiên thực tế, dữ liệu API trả về thỉnh thoảng có mốc thời gian (Unix Timestamp) của VNINDEX lệch với giờ đóng cửa của cổ phiếu (ví dụ lệch nhau vài phút do thời điểm khớp lệnh ATC khác nhau). Khi đó, Pandas sẽ từ chối Join dữ liệu vì nhận diện đây là 2 thời điểm khác biệt, dẫn đến lỗi hiển thị trên đồ thị.

Để khắc phục, em áp dụng hàm `.dt.normalize()` ngay trước khi nạp data vào bộ nhớ. Hàm này có nhiệm vụ ép tất cả mốc thời gian của các luồng API về chung mức `00:00:00` của ngày giao dịch đó, loại bỏ hoàn toàn các sai số thời gian lẻ tẻ trong ngày. Kết quả là hai biểu đồ được ghép nối với nhau một cách hoàn hảo.

---
Hy vọng những chia sẻ nhỏ này sẽ giúp mọi người hình dung rõ hơn về quá trình xây dựng **Data Pipeline** ở phía Back-end, đằng sau lớp UI của ứng dụng. Cảm ơn anh/chị và mọi người đã dành thời gian đọc bài! Em rất mong nhận được những góp ý và trao đổi từ mọi người! ✌️