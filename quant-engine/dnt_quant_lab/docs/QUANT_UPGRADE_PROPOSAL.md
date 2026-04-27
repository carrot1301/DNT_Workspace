# 📊 Đề Xuất Nâng Cấp Mô Hình Định Lượng — DNT Quant Lab
### Phiên bản: v2.0 — Tháng 04/2026
### Tác giả: DNT Engineering Team
### Mục đích: Tham vấn chuyên gia trước khi triển khai

---

## Mục Lục

1. [Tổng Quan Hệ Thống Hiện Tại](#1-tổng-quan-hệ-thống-hiện-tại)
2. [Chẩn Đoán: Vấn Đề Gốc Rễ](#2-chẩn-đoán-vấn-đề-gốc-rễ)
3. [Đề Xuất 1: Tích Hợp TA Score vào Factor Model](#3-đề-xuất-1-tích-hợp-ta-score-vào-factor-model)
4. [Đề Xuất 2: Thêm Risk Parity Strategy](#4-đề-xuất-2-thêm-risk-parity-strategy)
5. [Kiến Trúc Đề Xuất Tổng Thể](#5-kiến-trúc-đề-xuất-tổng-thể)
6. [Câu Hỏi Mở cho Chuyên Gia](#6-câu-hỏi-mở-cho-chuyên-gia)

---

## 1. Tổng Quan Hệ Thống Hiện Tại

### 1.1. Pipeline Tối Ưu Hóa Danh Mục

```
Input (User)                    Processing (Backend)                 Output
─────────────                   ────────────────────                 ──────
Mã CK: [VIC, VPB, ...]    →    Fetch OHLCV (Entrade API)       →   Tỷ trọng tối ưu (w₁...wₙ)
Vốn: 30,000,000 VNĐ       →    Log Returns → Cov Matrix        →   Giá trị kỳ vọng (VNĐ)
Thời gian: 6 tháng         →    Factor Model → Black-Litterman  →   VaR 95%, CI 95%
Min/Max Weight: 5%/40%     →    MVO Max Sharpe (scipy)          →   Efficient Frontier
                           →    Trend Following Overlay          →   Backtest vs VN30
                           →    Backtest Buy-and-Hold            →   Advanced Metrics
```

### 1.2. Các Module Hiện Có

| Module | Chức năng | Trạng thái |
|--------|-----------|------------|
| `data_engine.py` | Fetch dữ liệu OHLCV từ Entrade, tính Log Returns | ✅ Hoạt động |
| `portfolio_opt.py` | MVO + Black-Litterman + Monte Carlo 10K kịch bản | ✅ Hoạt động |
| `factor_model.py` | 3-Factor Model (Momentum, Low-Vol, Trend) | ✅ Mới triển khai |
| `ta_engine.py` | 21 chỉ báo kỹ thuật (12 MA + 9 Oscillator) | ⚠️ Chỉ hiển thị, chưa feed vào optimizer |
| `signals.py` | Tổng hợp tín hiệu BUY/SELL/HOLD | ⚠️ Chỉ hiển thị |
| `backtester.py` | Backtest Buy-and-Hold với trọng số MVO | ✅ Hoạt động |
| `screener.py` | Bộ lọc FA + TA cho VN30 (Daily Radar) | ✅ Hoạt động |

### 1.3. Mô Hình Toán Học Hiện Tại

**Bước 1: Ước lượng Hiệp Phương Sai**

$$\hat{\Sigma} = \alpha \cdot S + (1-\alpha) \cdot F$$

Sử dụng Ledoit-Wolf Shrinkage, trong đó $S$ là ma trận mẫu (sample covariance) và $F$ là ma trận mục tiêu (target matrix). Hệ số $\alpha$ được tự động tối ưu.

**Bước 2: Multi-Factor Expected Returns**

3 Factor dựa 100% trên dữ liệu giá (không phụ thuộc TCBS API):

| Factor | Weight | Công thức | Cơ sở lý thuyết |
|--------|--------|-----------|------------------|
| Momentum | 40% | $R_{6M} = P_{t-21}/P_{t-126} - 1$ | Jegadeesh & Titman (1993) |
| Low-Volatility | 30% | $-\sigma_{daily} \times \sqrt{252}$ | Baker, Bradley & Wurgler (2011) |
| Trend | 30% | $(P_{current} - SMA200) / SMA200$ | Moskowitz, Ooi & Pedersen (2012) |

Mỗi factor được Z-Score normalize, clip $\pm 3\sigma$, rồi tính Composite:

$$Score_i = 0.4 \cdot z_{momentum,i} + 0.3 \cdot z_{vol,i} + 0.3 \cdot z_{trend,i}$$

$$\alpha_i = Score_i \times 0.10 \quad (\text{Alpha Scale})$$

**Bước 3: Black-Litterman Integration**

Composite Scores → chuyển thành Views $(P, Q)$ → feed vào BL:

$$E(R) = [(\tau\Sigma)^{-1} + P^T\Omega^{-1}P]^{-1} \cdot [(\tau\Sigma)^{-1}\Pi + P^T\Omega^{-1}Q]$$

- $\Pi$: Implied Equilibrium Returns (từ Equal-Weighted prior)
- $\tau = 0.15$: Confidence scaling
- $\Omega$: Ma trận uncertainty của Views (tự suy từ $P$ và $\Sigma$)

**Bước 4: MVO Max Sharpe**

$$\max_w \frac{w^T E(R) - R_f}{\sqrt{w^T \Sigma w}} \quad \text{s.t.} \quad \sum w_i = 1, \quad w_i \in [w_{min}, w_{max}]$$

**Bước 5: Trend Following Overlay** (Hậu tối ưu)

| Trạng thái | Điều kiện | Điều chỉnh |
|------------|-----------|-------------|
| Uptrend | $P > SMA50$ và $P > SMA200$ | Giữ nguyên $w$ |
| Mild Downtrend | $SMA200 \le P < SMA50$ | $w_{new} = 0.80 \cdot w$ |
| Strong Downtrend | $P < SMA200$ | $w_{new} = 0.60 \cdot w$ |

Re-normalize: $w_i \leftarrow w_i / \sum w_j$

---

## 2. Chẩn Đoán: Vấn Đề Gốc Rễ

### 2.1. Cornering / Concentration Risk

Với input 6 mã `[VIC, VPB, TCB, SHB, SSI, ACB]`, kết quả phân bổ:
- **VIC: 40%, SHB: 40%** (đụng trần)
- **4 mã còn lại: 5% mỗi mã** (đụng sàn)

**Nguyên nhân**: MVO cực đại hóa Sharpe → ưu tiên tài sản có expected return/risk ratio cao nhất → đẩy lên trần. Trend Overlay sau đó giảm weight các mã downtrend → re-normalize đẩy uptrend stocks lên trần thêm lần nữa.

**Hệ quả**: Danh mục mất đa dạng hóa, rủi ro phi hệ thống (idiosyncratic risk) chiếm ưu thế.

### 2.2. Bất Hợp Lý Risk/Reward

| Chỉ số | Giá trị | Vấn đề |
|--------|---------|--------|
| Expected Return (6M) | +4.23% | Thấp |
| VaR 95% | -25% | Cao |
| Max Drawdown | -31.3% | Rất cao |
| Risk/Reward | 4.23 / 25 = **0.17** | Quá thấp cho "tối ưu" |

### 2.3. Backtest Look-Ahead Bias

Backtest hiện tại áp dụng trọng số tối ưu **ngày hôm nay** lên dữ liệu **quá khứ** → kết quả backtest 75-80% return **không phản ánh thực tế** vì tại thời điểm quá khứ, optimizer sẽ cho trọng số khác.

### 2.4. Tín Hiệu TA Bị Lãng Phí

`ta_engine.py` tính toán **21 chỉ báo kỹ thuật** nhưng chỉ dùng để hiển thị trên UI:

```
Moving Averages (12 tín hiệu):
  SMA/EMA × [5, 10, 20, 50, 100, 200]

Oscillators (9 tín hiệu):
  RSI(14), Stochastic(14,3), Stochastic RSI(14), MACD(12,26),
  Williams %R(14), CCI(14), Awesome Oscillator(5,34), ROC(14), MFI(14)

Output: Composite Score ∈ [-1.0, +1.0]
  - MUA MẠNH: score ≥ 0.54
  - MUA: score > 0
  - TRUNG TÍNH: score = 0
  - BÁN: score < 0
  - BÁN MẠNH: score ≤ -0.54
```

Score này tổng hợp cả **trend** (MA), **momentum** (RSI, ROC), **overbought/oversold** (Stochastic, Williams %R), và **money flow** (MFI) — phong phú hơn nhiều so với Trend Factor hiện tại (chỉ dùng Price vs SMA200).

---

## 3. Đề Xuất 1: Tích Hợp TA Score vào Factor Model

### 3.1. Ý Tưởng

Thêm **TA Composite Score** làm Factor thứ 4 trong Multi-Factor Model. Score từ `ta_engine.py` sẽ tham gia trực tiếp vào quá trình ước lượng Expected Returns qua Black-Litterman.

### 3.2. Bảng Factor Weights Đề Xuất

| Factor | Hiện tại | Đề xuất v2 | Lý do thay đổi |
|--------|----------|-------------|-----------------|
| Momentum (6M skip 1M) | 40% | **30%** | TA Score đã gồm ROC, MACD (momentum signals) |
| Low-Volatility | 30% | **25%** | Giữ ổn, hơi giảm vì thêm factor mới |
| Trend (Price/SMA200) | 30% | **15%** | TA Score đã gồm 12 MA signals, coverage rộng hơn |
| **TA Composite (MỚI)** | — | **30%** | 21 tín hiệu, đa chiều (trend + momentum + flow + overbought) |

### 3.3. Implementation

```python
# Trong factor_model.py

def compute_ta_factor_score(ticker: str) -> float:
    """
    Lấy TA Composite Score từ ta_engine.
    
    Score = (total_buy - total_sell) / (total_buy + total_sell + total_neutral)
    Kết quả ∈ [-1.0, +1.0]
    
    Lợi thế so với Trend Factor đơn giản:
    - 21 indicators vs 1 indicator (SMA200)
    - Bao gồm cả leading indicators (RSI, Stochastic)
    - Phản ánh cả money flow (MFI) — proxy cho dòng tiền tổ chức
    """
    df = fetch_stock_data(ticker, days_back=365)
    if df.empty or len(df) < 200:
        return 0.0
    
    ta_data = compute_full_ta(df, ticker)
    if 'summary' not in ta_data:
        return 0.0
    
    return ta_data['summary']['score']  # Đã tính sẵn ∈ [-1, 1]
```

### 3.4. Composite Score Mới

$$Score_i^{v2} = 0.30 \cdot z_{momentum} + 0.25 \cdot z_{vol} + 0.15 \cdot z_{trend} + 0.30 \cdot z_{TA}$$

### 3.5. Ưu/Nhược Điểm

**Ưu điểm:**
- Tận dụng 21 chỉ báo đã có sẵn, không cần thêm data source
- TA Score cung cấp tín hiệu **timing** (khi nào nên mua) — bổ sung cho MVO (chỉ biết **bao nhiêu** nên mua)
- Leading indicators (RSI, Stochastic) có thể phát hiện đảo chiều trước khi Price/SMA200 phản ứng

**Nhược điểm / Rủi ro:**
- TA indicators phần lớn dựa trên **cùng một dữ liệu giá** → nguy cơ multicollinearity cao
- Trong thị trường sideway, nhiều oscillators cho tín hiệu nhiễu → Score dao động mạnh
- Hầu hết nghiên cứu học thuật cho thấy TA indicators **không có alpha thống kê** (Efficient Market Hypothesis)

**Câu hỏi cần chuyên gia xác nhận:**
> Liệu việc thêm TA Score (vốn dĩ tính từ cùng price data) có thực sự cải thiện estimation, hay chỉ là thêm nhiễu (noise) vào mô hình?

---

## 4. Đề Xuất 2: Thêm Risk Parity Strategy

### 4.1. Vấn Đề Cốt Lõi của MVO

Mean-Variance Optimization có 2 hạn chế được ghi nhận rộng rãi trong giới học thuật:

1. **Estimation Error Amplification**: MVO nhạy cảm cực đoan với expected returns. Sai số nhỏ trong ước lượng returns → thay đổi lớn trong trọng số → concentration (Chopra & Ziemba, 1993).
2. **Diversification Failure**: Khi expected returns gần nhau (phổ biến với rổ cùng ngành), optimizer đẩy lên/xuống bounds thay vì diversify.

### 4.2. Giải Pháp: Risk Parity (Equal Risk Contribution)

**Triết lý**: Thay vì tối đa Return/Risk, phân bổ sao cho **mỗi tài sản đóng góp bằng nhau vào tổng rủi ro danh mục**.

**Định nghĩa toán học:**

Marginal Risk Contribution của tài sản $i$:

$$MRC_i = \frac{\partial \sigma_p}{\partial w_i} = \frac{(\Sigma w)_i}{\sigma_p}$$

Risk Contribution của tài sản $i$:

$$RC_i = w_i \times MRC_i = \frac{w_i \cdot (\Sigma w)_i}{\sigma_p}$$

**Mục tiêu Risk Parity**: Tìm $w$ sao cho $RC_i = RC_j \quad \forall i, j$

Tương đương với bài toán tối ưu:

$$\min_w \sum_{i=1}^{n} \sum_{j=1}^{n} (RC_i - RC_j)^2 \quad \text{s.t.} \quad \sum w_i = 1, \quad w_i \ge 0$$

### 4.3. So Sánh MVO vs Risk Parity

| Tiêu chí | MVO Max Sharpe | Risk Parity |
|----------|----------------|-------------|
| Input cần thiết | Expected Returns + Covariance | **Chỉ Covariance** |
| Nhạy cảm với estimation error | Rất cao | Thấp |
| Concentration risk | Cao (đụng bounds) | **Thấp (bản chất diversified)** |
| Cần bounds min/max | Bắt buộc | Không cần |
| Hiệu suất khi rổ cùng ngành | Kém (cornering) | **Tốt** |
| Được dùng bởi | Học thuật, retail | **Bridgewater ($150B), AQR ($140B)** |
| Trường hợp tốt nhất | Rổ đa ngành, ước lượng returns chính xác | **Rổ cùng ngành, thị trường không chắc chắn** |

### 4.4. Implementation Đề Xuất

```python
def risk_parity_optimization(cov_matrix: pd.DataFrame, 
                              tickers: list) -> dict:
    """
    Risk Parity: Equal Risk Contribution.
    
    Mỗi tài sản đóng góp bằng nhau vào tổng rủi ro danh mục.
    Không cần ước lượng expected returns → loại bỏ nguồn lỗi lớn nhất.
    """
    n = len(tickers)
    Sigma = cov_matrix.values
    
    def risk_budget_objective(w):
        port_var = w @ Sigma @ w
        port_vol = np.sqrt(port_var)
        
        # Risk Contribution cho mỗi asset
        marginal_risk = Sigma @ w
        risk_contribution = w * marginal_risk / port_vol
        
        # Target: mỗi asset đóng góp 1/n rủi ro
        target_rc = port_vol / n
        
        # Minimize squared differences
        return np.sum((risk_contribution - target_rc) ** 2)
    
    # Constraints & Bounds
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    bounds = [(0.01, 0.60)] * n
    init = np.ones(n) / n
    
    result = minimize(risk_budget_objective, init, 
                     method='SLSQP', bounds=bounds, 
                     constraints=constraints)
    
    return dict(zip(tickers, result.x))
```

### 4.5. UI Integration

Thêm option cho user chọn chiến lược trong sidebar **Cài đặt Nâng cao**:

```
Chiến lược tối ưu:
  ○ Max Sharpe (MVO)          ← Hiện tại
  ○ Risk Parity (Equal Risk)  ← Mới
  ○ Minimum Variance          ← Mới
```

### 4.6. Ưu/Nhược Điểm

**Ưu điểm:**
- Giải quyết triệt để concentration risk
- Robust hơn MVO khi estimation error cao
- Không cần expected returns → loại bỏ nguồn lỗi lớn nhất
- Phù hợp đặc biệt khi rổ cổ phiếu cùng ngành (ngân hàng, chứng khoán)

**Nhược điểm / Rủi ro:**
- Không tối đa return — chỉ cân bằng rủi ro
- Trong rổ mà 1 mã volatility rất thấp → Risk Parity dồn vào mã đó (giống concentration nhưng từ phía vol)
- Không tận dụng được factor views / BL (vì không dùng expected returns)

**Câu hỏi cần chuyên gia xác nhận:**
> Risk Parity có nên kết hợp với Factor Model không? Một số quỹ dùng "Factor-Tilted Risk Parity" — phân bổ risk-parity trước, sau đó tilt nhẹ theo factor views.

---

## 5. Kiến Trúc Đề Xuất Tổng Thể

### 5.1. Pipeline v2.0

```
                        ┌─────────────────────┐
                        │   Data Layer         │
                        │   (Entrade OHLCV)    │
                        └─────────┬───────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │ Log       │  │ TA Engine│  │ Cov      │
            │ Returns   │  │ 21 Chỉ   │  │ Matrix   │
            │           │  │ Báo      │  │ (LW)     │
            └─────┬────┘  └────┬─────┘  └────┬─────┘
                  │            │              │
                  ▼            ▼              │
         ┌────────────────────────┐           │
         │  4-Factor Model (MỚI) │           │
         │  Momentum  30%        │           │
         │  Low-Vol   25%        │           │
         │  Trend     15%        │           │
         │  TA Score  30%        │           │
         └──────────┬────────────┘           │
                    │                         │
                    ▼                         │
         ┌──────────────────┐                │
         │  Black-Litterman │ ◄──────────────┘
         │  (τ = 0.15)      │
         └────────┬─────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
  ┌──────────────┐  ┌──────────────┐
  │ MVO          │  │ Risk Parity  │   ← User chọn
  │ Max Sharpe   │  │ Equal Risk   │
  └──────┬───────┘  └──────┬───────┘
         │                 │
         └────────┬────────┘
                  ▼
         ┌──────────────────┐
         │ Trend Following  │
         │ Overlay (Post)   │
         └────────┬─────────┘
                  ▼
         ┌──────────────────┐
         │ Final Weights    │
         │ + Backtest       │
         │ + Risk Metrics   │
         └──────────────────┘
```

### 5.2. Tóm Tắt Thay Đổi Kỹ Thuật

| File | Thay đổi |
|------|----------|
| `factor_model.py` | Thêm `compute_ta_factor_score()`, cập nhật weights |
| `portfolio_opt.py` | Thêm `risk_parity_optimization()`, UI parameter routing |
| `main.py` | Thêm parameter `strategy_type` vào API |
| `app.html` | Thêm radio buttons chọn strategy |
| `script.js` | Gửi `strategy_type` lên API |
| `backtester.py` | Không đổi |

---

## 6. Câu Hỏi Mở cho Chuyên Gia

### Về Mô Hình

1. **TA Score Multicollinearity**: 21 chỉ báo TA đều tính từ cùng dữ liệu OHLCV. Liệu Z-Score normalized TA Composite có thực sự cung cấp thông tin bổ sung (orthogonal information) so với Momentum + Trend factors, hay chỉ thêm nhiễu?

2. **Factor Weights**: Phân bổ `[30%, 25%, 15%, 30%]` hiện đang là heuristic. Có nên dùng **Elastic Net Regression** hoặc **PCA** để xác định weights tối ưu từ dữ liệu lịch sử không?

3. **Alpha Scale = 0.10**: Hệ số chuyển đổi từ Factor Score sang Expected Return Adjustment. Giá trị này quá lớn → overshoot, quá nhỏ → BL bỏ qua views. Có benchmark nào cho thị trường VN không?

### Về Chiến Lược

4. **Risk Parity khi rổ cùng ngành**: 6 mã test (VIC, VPB, TCB, SHB, SSI, ACB) đều là Tài chính + BĐS. Correlation cao → Risk Parity có thể cho kết quả gần Equal Weight. Lợi ích thực sự có đáng kể không?

5. **Factor-Tilted Risk Parity**: Có nên kết hợp Risk Parity (cho base allocation) + Factor Model (cho small tilt) thay vì để riêng 2 strategy không?

6. **Rebalancing Frequency**: Hệ thống hiện chạy 1 lần (snapshot). Có nên thêm tính năng **tái cân bằng theo tuần/tháng** với rolling window không?

### Về Dữ Liệu

7. **Entrade API Reliability**: Dữ liệu OHLCV từ Entrade đôi khi có spike do chia tách cổ phiếu. Hiện đang clip ±15%. Có phương pháp adjusted price nào tốt hơn không?

8. **TCBS Fundamentals**: API financials (P/E, ROE, Growth) hiện fallback sang random mock data khi API timeout. Có data source nào ổn định hơn cho thị trường VN không?

---

## Phụ Lục: Kết Quả Backtest Hiện Tại

**Input**: VIC, VPB, TCB, SHB, SSI, ACB | Vốn: 30,000,000 VNĐ | 6 tháng

| Chỉ số | Giá trị | Đánh giá |
|--------|---------|----------|
| Expected Return | +4.23% (6M) | Hợp lý |
| VaR 95% | -7,500,168 VNĐ (-25%) | Cao |
| Max Drawdown | -31.30% | Cao |
| Sharpe Ratio | 0 → 0.15 | Dương nhưng thấp |
| Beta vs VNINDEX | 0.99 | Gần thị trường |
| Sortino | 1.55 | Tốt |
| Calmar | 1.36 | Chấp nhận |
| R² | 0.62 | Trung bình |
| Allocation | VIC 40%, SHB 40%, 4 mã 5% | Quá tập trung |

**Backtest lịch sử (9 tháng)**: MVO ~75%, VNINDEX ~28% — chênh lệch lớn do look-ahead bias.

---

*Tài liệu này được soạn để tham vấn chuyên gia Quant trước khi triển khai. Mọi feedback xin gửi về DNT Engineering Team.*
