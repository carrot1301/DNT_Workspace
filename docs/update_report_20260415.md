# BÁO CÁO CẬP NHẬT DNT QUANT LAB
**Ngày cập nhật: 15/04/2026**

---

## Tổng quan bản cập nhật

Bản cập nhật lần này tập trung vào việc **xây dựng hoàn chỉnh hệ thống Phân tích Kỹ thuật (Technical Analysis — TA)** cho DNT Quant Lab. Thay vì phụ thuộc vào dữ liệu scrape từ bên thứ ba (FireAnt), hệ thống đã chuyển sang tự tính toán toàn bộ các chỉ báo kỹ thuật nội bộ dựa trên thư viện `pandas_ta`, nhằm đảm bảo tính chủ động, chính xác và mở rộng linh hoạt.

**Phạm vi thay đổi:**
- Backend: Tạo mới module `ta_engine.py`, tái cấu trúc `signals.py`
- AI Advisor: Cập nhật System Prompt tích hợp dữ liệu TA
- Frontend: Bổ sung giao diện trực quan TA Modal (Bento Grid)
- Dependencies: Thêm `pandas_ta` vào pipeline

---

## 1. Backend — Module `ta_engine.py` *(MỚI)*

### 1.1. Kiến trúc hàm `compute_full_ta()`

Tạo mới file `backend/core/ta_engine.py` chứa hàm tính toán TA toàn diện. Hàm nhận đầu vào là DataFrame OHLCV (tối thiểu 200 phiên) và trả về dictionary chứa đầy đủ chỉ báo kỹ thuật theo 4 nhóm chính:

| Nhóm chỉ báo | Chỉ báo cụ thể | Ý nghĩa |
|---|---|---|
| **Trend** (Xu hướng) | SMA10, SMA20, SMA50, SMA200, EMA10, EMA20, EMA50, EMA200, MACD (12/26/9), ADX (14) | Xác định xu hướng ngắn/trung/dài hạn |
| **Oscillators** (Dao động) | RSI (14), Stochastic (14/3/3), CCI (14), Williams %R (14) | Phát hiện quá mua/quá bán |
| **Volatility** (Biến động) | Bollinger Bands (20/2.0) | Đo biên độ dao động giá |
| **Volume** (Khối lượng) | OBV, MFI (14) | Xác nhận dòng tiền ủng hộ xu hướng |

### 1.2. Hệ thống chấm điểm tín hiệu tự động

Mỗi chỉ báo trong 8 chỉ báo chủ chốt đều được phân loại thành `BUY`, `SELL`, hoặc `NEUTRAL` dựa trên logic riêng. Sau đó điểm tổng hợp được tính theo công thức:

$$\text{Score} = \frac{\text{BUY\_count} - \text{SELL\_count}}{\text{Total\_signals}}$$

Kết quả tổng hợp cuối cùng (`overall_signal`) được phân loại theo ngưỡng:
- **STRONG BUY**: Score > 0.3
- **BUY**: Score > 0.1
- **STRONG SELL**: Score < -0.3
- **SELL**: Score < -0.1
- **NEUTRAL**: Còn lại

### 1.3. Chi tiết logic phân loại từng chỉ báo

| # | Chỉ báo | Điều kiện BUY | Điều kiện SELL |
|---|---|---|---|
| 1 | SMA Cluster | Giá > SMA20 > SMA50 | Giá < SMA20 < SMA50 |
| 2 | MACD | MACD Line > Signal Line & Histogram tăng | MACD Line < Signal Line & Histogram giảm |
| 3 | RSI | RSI < 30 (oversold) hoặc RSI ∈ (50, 70) | RSI > 70 (overbought) hoặc RSI < 50 |
| 4 | Bollinger | Giá < BBL (dưới biên dưới) | Giá > BBU (trên biên trên) |
| 5 | Stochastic | %K < 20 & %D < 20 & %K > %D (golden cross) | %K > 80 & %D > 80 & %K < %D (death cross) |
| 6 | ADX | ADX > 25 & DI+ > DI- | ADX > 25 & DI+ < DI- |
| 7 | CCI | CCI < -100 | CCI > 100 |
| 8 | MFI | MFI < 20 | MFI > 80 |

---

## 2. Backend — Tái cấu trúc `signals.py`

Module `signals.py` đã được viết lại hoàn toàn:

**Trước đó:** Sử dụng logic đơn giản dựa trên SMA crossover thủ công.

**Hiện tại:**
- Import và gọi trực tiếp `compute_full_ta()` từ `ta_engine.py`
- Trả về `overall_signal` từ bộ chấm điểm 8 chỉ báo (thay vì 1-2 signal thủ công)
- Kèm theo toàn bộ object `ta_analysis` trong response JSON để Frontend có thể trực quan hóa chi tiết
- Tính toán khối lượng khuyến nghị (Volume) theo lô 100 cổ phiếu dựa trên tỷ trọng phân bổ

**Cấu trúc response mới cho mỗi mã cổ phiếu:**
```json
{
  "action": "BUY | SELL | STRONG BUY | STRONG SELL | NEUTRAL",
  "detail": "Điểm TA: 0.38 | B:5 S:1 N:2",
  "price": 25600,
  "volume": 300,
  "broker_url": "https://smartoneweb.vps.com.vn/",
  "ta_analysis": {
    "summary": {...},
    "trend": {...},
    "oscillators": {...},
    "volatility": {...},
    "volume": {...}
  }
}
```

---

## 3. Tích hợp AI Advisor (`ai_advisor.py`)

### Cập nhật System Prompt

Prompt Template của mô hình Gemini LLM đã được mở rộng thêm một phần mới với nhãn:

> **PHÂN TÍCH KỸ THUẬT (TECHNICAL ANALYSIS — Dài hạn & Ngắn hạn):**

Dữ liệu TA tóm tắt (bao gồm RSI, MACD, các đường xu hướng SMA/EMA, ADX) được tự động được nạp vào LLM context. Nhờ đó, mô hình AI có thể:

- Tổng hợp cả góc nhìn **Định lượng (Quant)** lẫn **Kỹ thuật (TA)** để đưa ra tư vấn Timing (thời điểm mua/bán) chính xác hơn
- Cảnh báo rủi ro khi các chỉ báo TA cho thấy trạng thái quá mua hoặc phân kỳ (divergence)
- Phối hợp với dữ liệu Black-Litterman (đã tích hợp từ bản cập nhật 13/04) để đưa ra nhận định đa chiều

---

## 4. Frontend — Trực quan hóa TA Modal

### 4.1. Nút "Chi tiết TA" trên bảng tín hiệu

Mỗi dòng tín hiệu giao dịch trong bảng kết quả giờ đây có thêm nút bấm **"Chi tiết TA"**. Trước đây, bảng chỉ hiển thị nhãn ngắn gọn `BUY/SELL`, nhưng bản cập nhật này cho phép người dùng xem toàn bộ bức tranh kỹ thuật phía sau quyết định.

### 4.2. TA Modal — Bento Grid Layout

Khi nhấn nút "Chi tiết TA", một popup modal dạng **Bento Grid** được hiển thị với thiết kế hiện đại:

- **Ô Tổng quan**: Overall Signal (STRONG BUY / BUY / NEUTRAL / SELL / STRONG SELL) kèm thanh điểm số trực quan
- **Ô Trend**: Giá vs SMA20 / SMA50 / SMA200, MACD histogram, ADX
- **Ô Oscillators**: RSI gauge, Stochastic %K/%D, CCI, Williams %R
- **Ô Volatility**: Bollinger Bands (Upper / Middle / Lower)
- **Ô Volume**: OBV trend, MFI gauge

### 4.3. Định dạng màu sắc tín hiệu

Bảng giao dịch được áp dụng color-coding phù hợp:
- 🟢 **BUY / STRONG BUY**: Xanh lá — khuyến nghị mua
- 🔴 **SELL / STRONG SELL**: Đỏ — khuyến nghị bán
- ⚪ **NEUTRAL / HOLD**: Xám — giữ nguyên / quan sát

---

## 5. Sơ đồ luồng xử lý mới

```
User Input (Tickers + Vốn)
        │
        ▼
  ┌─────────────┐
  │ data_engine  │ ─── Fetch OHLCV từ DNSE API
  └──────┬──────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│ta_engine│ │portfolio_opt │ ─── Mean-Variance / Black-Litterman
└───┬────┘ └──────┬───────┘
    │              │
    ▼              │
┌────────┐         │
│signals │◄────────┘ ─── Tỷ trọng + TA → Action + Volume
└───┬────┘
    │
    ▼
┌───────────┐
│ai_advisor │ ─── Prompt = Quant Data + TA Summary → Gemini LLM
└───┬───────┘
    │
    ▼
┌──────────┐
│ Frontend │ ─── Bảng tín hiệu + TA Modal (Bento Grid)
└──────────┘
```

---

## 6. Danh sách file thay đổi

| File | Trạng thái | Mô tả |
|---|---|---|
| `backend/core/ta_engine.py` | **MỚI** | Module tính toán TA toàn diện (192 dòng) |
| `backend/core/signals.py` | **THAY ĐỔI** | Tái cấu trúc hoàn toàn, tích hợp TA engine |
| `backend/core/ai_advisor.py` | **THAY ĐỔI** | Bổ sung TA context vào System Prompt |
| `frontend/index.html` | **THAY ĐỔI** | Thêm HTML structure cho TA Modal |
| `frontend/script.js` | **THAY ĐỔI** | Logic render TA Modal, xử lý sự kiện nút Chi tiết |
| `frontend/style.css` | **THAY ĐỔI** | CSS cho Bento Grid layout, color-coding signals |

---

## 7. Hướng dẫn kiểm tra

```bash
cd f:\DNT_Workspace\quant-engine\dnt_quant_lab\backend
uvicorn main:app --reload
```

Mở frontend → nhập mã cổ phiếu (ví dụ: `MBB`, `FPT`) → Quan sát:
1. Cột tín hiệu hiển thị `BUY/SELL/STRONG BUY/...` kèm điểm TA
2. Nút **"Chi tiết TA"** mở modal Bento Grid với đầy đủ chỉ báo
3. AI Advisor có thêm phần phân tích kỹ thuật trong báo cáo

---

## 8. Kế hoạch phát triển tiếp theo

- [ ] Triển khai **Phân tích Cơ bản (Fundamental Analysis — FA)**: Kết nối endpoint `/api/financials/{ticker}` vào prompt AI tương tự cách đã làm cho TA
- [ ] Thêm **biểu đồ nến (Candlestick)** kết hợp overlay các đường SMA/EMA/Bollinger trực tiếp trên Frontend
- [ ] Xây dựng **Alert System**: Tự động gửi thông báo khi một mã đạt trạng thái STRONG BUY hoặc STRONG SELL
- [ ] Tích hợp **Backtesting cho TA signals**: Đo lường hiệu quả lịch sử của bộ tín hiệu 8 chỉ báo

---

*Báo cáo được khởi tạo tự động bởi hệ thống Quản lý DNT Quant Lab.*
