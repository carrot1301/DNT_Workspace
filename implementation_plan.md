# Kế hoạch Tái cấu trúc Repository

Dự án hiện tại bao gồm frontend chạy trên trang cá nhân (portfolio), và hệ thống phân tích backend API/Streamlit UI rời rạc. Kế hoạch này sẽ tổ chức các mã nguồn thành cấu trúc dễ bảo trì và phân tách logic rõ ràng thành `portfolio-web` và `quant-engine`.

## User Review Required

> [!IMPORTANT]
> - Vui lòng xác nhận xem thư mục `quant-engine` sẽ tiếp tục đóng vai trò như một Multi-App Monorepo (chứa thư mục `dnt_quant_lab` và `vn_stocks_quant` bên trong nó) hay bạn muốn "trộn" (flatten) luôn nội dung của hai dự án này vào một? (Tạm thời tôi thiết lập theo hướng Monorepo với `quant-engine` làm gốc, vì các app này chạy dịch vụ riêng biệt).
> - Với thư mục `.github` hoặc tự động hoá CI/CD, việc di chuyển `Dockerfile` và mã nguồn web/app sẽ yêu cầu setup lại path deployment. Hãy đảm bảo Koyeb (hoặc VPS) của bạn sẽ được chỉnh sửa build path mới là `/quant-engine`.

## Proposed Changes

### `portfolio-web/` (Thư mục mới)
Đây sẽ là nơi lưu trữ toàn bộ nội dung frontend của website portfolio PortfolioCV.

#### Định vị các file web tĩnh hiện tại
- `index.html` → `portfolio-web/index.html`
- `style.css` → `portfolio-web/style.css` 
- `script.js` → `portfolio-web/script.js`
- `assets/` → `portfolio-web/assets/`
- `CV_Doan_Nguyen_Tri_Quant_Analyst.pdf` → `portfolio-web/CV_Doan_Nguyen_Tri_Quant_Analyst.pdf`
- `CNAME` → `portfolio-web/CNAME`

### `quant-engine/` (Thư mục mới)
Toàn bộ logic backend (API) và module Python (Streamlit/FastAPI) sẽ gom về đây.

#### Di chuyển Backend & Models
- `dnt_quant_lab/` → `quant-engine/dnt_quant_lab/`
- `vn_stocks_quant/` → `quant-engine/vn_stocks_quant/`
- `Dockerfile` (Root) → `quant-engine/Dockerfile`
- `quant_task.md` → `quant-engine/quant_task.md`

### Quét và Cập nhật Python Script & Dockerfile

#### [MODIFY] `quant-engine/Dockerfile`
- Update các layer `COPY` nếu cần (khi đưa vào `quant-engine` có thể đường dẫn Build Context sẽ thay đổi). Nếu Dockerfile nằm trong `quant-engine` và cấu trúc là `quant-engine/dnt_quant_lab/backend`, thì nội dung chạy như cũ `COPY dnt_quant_lab/backend ./backend` vẫn đúng do context build gốc chạy chung thư mục. Nhưng tôi sẽ tối ưu lại Dockerfile dựa trên việc hợp nhất thư mục này.

#### Cập nhật các câu lệnh Imports và Dữ liệu Cục bộ trong Python code
- **Quét đường dẫn Local (.js/.json):** `vn_stocks_quant/app.py` và `dnt_quant_lab/backend/core/data_engine.py` đang dùng `os.path.dirname(__file__)` để load data path, sau khi move folder cơ bản sẽ vẫn nhận diện chính xác ở level cục bộ của nó, tuy nhiên tôi sẽ tiến hành chạy test kiểm tra đảm bảo tính ổn định của các import từ `data_loader`, `metrics.py` hoặc các module dùng chung. 
- Xoá các cache rác còn sót lại của Streamlit hoặc Python (.venv) nếu nó làm hỏng reference trong quá trình đổi vị trí để tránh xung đột môi trường. (Recommend create lại venv nếu thiết lập chung môi trường sau này).

## Open Questions

> [!WARNING]
> Môi trường ảo `.venv` hiện tại đang ở Root thư mục, bạn có muốn tôi setup lại 1 file `requirements.txt` tổng hoặc duy trì từng môi trường ảo riêng biệt trong mỗi project ở `quant-engine` không?

## Verification Plan

### Automated/Manual Tests
- Kiểm thử frontend bằng cách mở `portfolio-web/index.html` mô phỏng trực tiếp xem UI load css/js/assets hợp lệ không.
- Kiểm thử backend:
  - Khởi động thử service Streamlit tại `quant-engine/vn_stocks_quant/app.py`.
  - Khởi động backend FastAPI tại `quant-engine/dnt_quant_lab/backend/main.py` xem API có kết nối cache database bình thường không.
- Chạy `docker build` cục bộ tại context `quant-engine/Dockerfile` để test quá trình rebuild không gặp lỗi missing files.
