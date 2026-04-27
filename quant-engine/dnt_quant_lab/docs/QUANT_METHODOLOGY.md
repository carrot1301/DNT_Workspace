# Báo Cáo Phương Pháp Định Lượng (Quant Methodology) — DNT Quant Lab v3.0

Tài liệu này mô tả chi tiết các mô hình toán học và logic định lượng được sử dụng trong nền tảng **DNT Quant Lab** để tối ưu hóa danh mục đầu tư và phân bổ tài sản.

**Phiên bản:** v3.0 — Tháng 04/2026
**Cập nhật:** Tích hợp Expert Feedback từ DeepSeek, GPT, Gemini, Grok

---

## 1. Kiến Trúc Cốt Lõi: Dual Strategy Engine

DNT Quant Lab cung cấp 2 chiến lược tối ưu hóa cho người dùng lựa chọn:

| Chiến lược | Mục tiêu | Input cần thiết | Phù hợp khi |
|------------|----------|------------------|-------------|
| **Max Sharpe (MVO)** | Tối đa Return/Risk | Expected Returns + Covariance | Rổ đa ngành, có dữ liệu tốt |
| **Risk Parity + Factor Tilt** | Cân bằng Risk Contribution | Covariance + Factor Scores | Rổ cùng ngành, thị trường bất ổn |

---

## 2. Data Pipeline

### 2.1. Nguồn Dữ Liệu
- **Giá OHLCV:** Entrade API (`entrade.com.vn`)
- **VN30 Benchmark:** Entrade Index API
- **Dữ liệu cơ bản (FA):** Không sử dụng trong mô hình tối ưu (do TCBS API không đáng tin cậy)

### 2.2. Xử Lý Dữ Liệu
- **Log Returns:** $r_t = \ln(P_t / P_{t-1})$
- **Spike Filtering:** Per-column clipping tại $\pm 15\%$ (biên độ sàn UPCOM)
- **Covariance Shrinkage:** Ledoit-Wolf Estimator
  $$\hat{\Sigma} = \alpha \cdot S + (1-\alpha) \cdot F$$
  Giảm estimation error khi $T < N^2$

---

## 3. Multi-Factor Model (3 Factor, Price-only)

Hệ thống xây dựng **Composite Factor Score** hoàn toàn từ dữ liệu giá:

### 3.1. Momentum Factor (40% Weight)
- **Cơ sở:** Jegadeesh & Titman (1993) — Cross-sectional Momentum
- **Công thức:** $Momentum = \frac{P_{t-21}}{P_{t-126}} - 1$
- Skip 1 tháng cuối để tránh Short-term Reversal

### 3.2. Low-Volatility Factor (30% Weight)
- **Cơ sở:** Baker, Bradley & Wurgler (2011) — Low-Volatility Anomaly
- **Công thức:** $VolScore = -\sigma_{daily,63d} \times \sqrt{252}$
- Dùng 63 ngày gần nhất (3 tháng) cho ước lượng volatility

### 3.3. Trend Factor (30% Weight)
- **Cơ sở:** Moskowitz, Ooi & Pedersen (2012) — Time Series Momentum
- **Công thức:** $Trend = \frac{P_{current} - SMA200}{SMA200}$

### 3.4. Composite Score & Alpha
$$Score_i = 0.4 \cdot z_{momentum} + 0.3 \cdot z_{vol} + 0.3 \cdot z_{trend}$$

Z-Score normalize mỗi factor riêng, clip $\pm 3\sigma$. Chuyển thành alpha:
$$\alpha_i = Score_i \times 0.03$$

> **Lưu ý (v3):** Alpha Scale giảm từ 0.10 → **0.03** theo expert consensus.
> Giá trị 0.10 quá lớn cho thị trường VN (emerging market), khiến BL "rewrite market"
> thay vì "tilt nhẹ". Phạm vi hợp lý: 0.02–0.05.

### 3.5. TA Engine (21 Chỉ Báo) — Không Tham Gia Factor Model

> **Quyết định thiết kế (v3):** Cả 4 chuyên gia đồng thuận:
> TA Score (21 indicators) **KHÔNG** được đưa vào Factor Model vì:
> 1. **Multicollinearity:** 21 chỉ báo TA đều tính từ cùng chuỗi giá OHLCV
> 2. **Double-counting:** TA là nonlinear transform của Momentum + Trend (đã có sẵn)
> 3. **Noise amplification:** Thêm TA chỉ khuếch đại nhiễu, không tạo orthogonal information
>
> TA được dùng cho: hiển thị khuyến nghị UI + đóng góp vào Dynamic Bounds (xem §5).

---

## 4. Black-Litterman Integration

### 4.1. Implied Equilibrium Returns
$$\Pi = \delta \cdot \Sigma \cdot w_{eq}$$
- $\delta = 2.5$ (risk aversion)
- $w_{eq}$: Equal-weighted prior (không có market cap data)

### 4.2. Posterior Expected Returns
$$E(R) = [(\tau\Sigma)^{-1} + P^T\Omega^{-1}P]^{-1} \cdot [(\tau\Sigma)^{-1}\Pi + P^T\Omega^{-1}Q]$$

- $\tau = 0.05$ (v3: giảm từ 0.15 — BL tilt nhẹ hơn)
- $P$: Identity matrix (absolute views cho từng asset)
- $Q$: Alpha values từ Factor Model
- $\Omega$: Tự suy từ $P$ và $\Sigma$: $\Omega = diag(P \cdot \tau\Sigma \cdot P^T)$

### 4.3. FTSE Event Views (Optional Overlay)
Các mã thụ hưởng FTSE nhận thêm alpha bump:
- 3 tháng: +2%, 6 tháng: +3%, 12 tháng: +5%

> **Lưu ý (v3):** Không áp dụng Variance Drag ở individual asset level.
> Sharpe Optimization đã tự cân bằng risk-return. Variance Drag ở individual level
> double-penalize → kéo expected returns quá thấp.

---

## 5. Dynamic Bounds (Thay Thế Trend Overlay)

> **Thay đổi quan trọng (v3):** Trend constraint được đưa VÀO optimizer thay vì
> áp dụng SAU optimization. Lý do: post-optimization overlay phá vỡ tính tối ưu
> của solution (optimizer giải constraint A, overlay áp constraint B → kết quả không
> còn tối ưu trong bất kỳ constraint set nào).

### 5.1. Logic Dynamic Bounds

| Trạng thái | Điều kiện | Max Bound |
|------------|-----------|-----------|
| **Uptrend** | $P > SMA50$ và $P > SMA200$ | `user_max` (giữ nguyên) |
| **Mild Downtrend** | $SMA200 \le P < SMA50$ | `min(user_max, 25%)` |
| **Strong Downtrend** | $P < SMA200$ | `min(user_max, 10%)` |

### 5.2. Ưu Điểm
- Optimizer **biết** constraint trước khi giải → solution tối ưu trong constraint thực tế
- Không cần re-normalize → trọng số tổng luôn = 100%
- Giảm concentration tự nhiên hơn (downtrend stocks bị cap thấp)

---

## 6. Chiến Lược 1: MVO Max Sharpe

### 6.1. Hàm Mục Tiêu
$$\max_w \frac{w^T E(R) - R_f}{\sqrt{w^T \Sigma w}}$$

- $R_f = 3\% \times \frac{trading\_days}{252}$ (lãi suất phi rủi ro)
- **Solver:** `scipy.optimize.minimize` (SLSQP)

### 6.2. Ràng Buộc
- $\sum w_i = 1$
- $w_i \in [dynamic\_min_i, dynamic\_max_i]$ (từ Dynamic Bounds)

---

## 7. Chiến Lược 2: Factor-Tilted Risk Parity

### 7.1. Bước 1: Risk Parity Base (Equal Risk Contribution)
$$\min_w \sum_{i=1}^{n} (RC_i - \bar{RC})^2$$

Trong đó:
$$RC_i = w_i \times \frac{(\Sigma w)_i}{\sigma_p}$$
$$\bar{RC} = \frac{\sigma_p}{n}$$

### 7.2. Bước 2: Factor Tilt
$$w_{tilted} = w_{RP} \times (1 + \gamma \cdot z_{factor})$$
- $\gamma = 0.15$ (tilt strength)
- $z_{factor}$: Z-score normalized Composite Factor Score

### 7.3. Bước 3: Clip & Re-normalize
- Clip theo Dynamic Bounds: $w_i \in [lb_i, ub_i]$
- Re-normalize: $w_i \leftarrow w_i / \sum w_j$

### 7.4. Ưu/Nhược Điểm

| Tiêu chí | Max Sharpe | Risk Parity + Tilt |
|----------|------------|---------------------|
| Concentration risk | Cao | **Thấp** |
| Cần expected returns | Có | **Không (chỉ cov)** |
| Alpha capture | Trực tiếp qua BL | **Gián tiếp qua tilt** |
| Robustness | Thấp | **Cao** |
| Phù hợp rổ cùng ngành | Kém | **Tốt** |

---

## 8. Backtesting Framework: Rolling Walk-Forward

> **Thay đổi quan trọng (v3):** Thay Buy-and-Hold tĩnh bằng Rolling Walk-Forward
> để loại bỏ **look-ahead bias** (dùng weight hôm nay cho quá khứ → return ảo).

### 8.1. Pipeline

```
for t in monthly_rebalance_dates:
    train_data = returns[t - 126 days : t]         # In-sample (6 tháng)
    weights_t = optimize(train_data)                # Optimize trên quá khứ
    test_returns = returns[t : t + 21 days]         # Out-of-sample (1 tháng)
    
    turnover = |new_weights - old_weights|.sum()
    net_return = test_returns @ weights_t - turnover × 0.0015
    
    cumulative += net_return
```

### 8.2. Đặc Điểm
- **Train window:** 126 ngày (6 tháng in-sample)
- **Rebalance:** Mỗi 21 ngày (~1 tháng)
- **Transaction cost:** 0.15% mỗi lệnh (phí sàn VN tiêu chuẩn)
- **Turnover tracking:** $Turnover_t = \sum |w_{t,i} - w_{t-1,i}|$

### 8.3. So Sánh Với Backtest Cũ

| Tiêu chí | v2 (Static) | v3 (Rolling) |
|----------|-------------|--------------|
| Look-ahead bias | **Có** (weight hiện tại áp cho quá khứ) | **Không** |
| Transaction costs | Không tính | **0.15%/lệnh** |
| Rebalancing | Không (Buy-and-Hold) | **Monthly** |
| Out-of-sample | Không | **Có** |
| Return thực tế hơn | Không | **Có** |

---

## 9. Monte Carlo Simulation

- 10,000 kịch bản ngẫu nhiên (Random Portfolios)
- Tính: Return, Volatility, Sharpe cho mỗi kịch bản
- Xác định: Expected Value, CI 95%, VaR 95%

### 9.1. Giá Trị Kỳ Vọng
$$E(V) = Capital \times (1 + w^T E(R))$$

### 9.2. Khoảng Tin Cậy 95%
$$CI = E(R_p) \pm 1.96 \times \sigma_p$$

### 9.3. Value-at-Risk 95%
$$VaR_{95} = E(R_p) - 1.645 \times \sigma_p$$
Nếu $VaR_{95} > 0$ → Rủi ro mất vốn = 0 (trong kịch bản xấu vẫn có lời)

---

## 10. Advanced Metrics

| Chỉ số | Công thức | Ý nghĩa |
|--------|-----------|---------|
| **Beta** | $\beta = \frac{Cov(R_p, R_m)}{Var(R_m)}$ | Độ nhạy với thị trường |
| **Sortino** | $\frac{R_p - R_f}{\sigma_{downside}}$ | Return/Downside Risk |
| **Treynor** | $\frac{R_p - R_f}{\beta}$ | Return/Systematic Risk |
| **Calmar** | $\frac{R_p}{MaxDD}$ | Return/Max Drawdown |
| **R²** | $Corr(R_p, R_m)^2$ | % variance giải thích bởi thị trường |
| **Max Drawdown** | $\min(\frac{V_t - V_{peak}}{V_{peak}})$ | Sụt giảm tối đa từ đỉnh |

---

## 11. Tổng Quan Kiến Trúc v3.0

```
                        ┌─────────────────────┐
                        │   Data Layer         │
                        │   (Entrade OHLCV)    │
                        └─────────┬───────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             │             ▼
            ┌──────────┐         │      ┌──────────┐
            │ Log       │         │      │ Cov      │
            │ Returns   │         │      │ Matrix   │
            │           │         │      │ (LW)     │
            └─────┬────┘         │      └────┬─────┘
                  │              │            │
                  ▼              │            │
         ┌────────────────┐     │            │
         │ 3-Factor Model │     │            │
         │ Mom/Vol/Trend  │     │            │
         └──────┬─────────┘     │            │
                │               │            │
                ▼               │            │
         ┌──────────────┐      │            │
         │ Black-        │ ◄───┘            │
         │ Litterman     │                   │
         │ (τ=0.05)      │                   │
         └──────┬────────┘                   │
                │                            │
         ┌──────┴───────┐                    │
         ▼              ▼                    ▼
  ┌────────────┐ ┌──────────────┐   ┌──────────────┐
  │ Dynamic    │ │ MVO          │   │ Risk Parity  │
  │ Bounds     │ │ Max Sharpe   │   │ + Factor     │
  │ (SMA trend)│ │              │   │ Tilt         │
  └─────┬──────┘ └──────┬───────┘   └──────┬───────┘
        │               │                  │
        └───────────────┼──────────────────┘
                        ▼
               ┌──────────────────┐
               │ Rolling Backtest │
               │ Walk-Forward     │
               │ + Tx Costs       │
               └──────────────────┘
```

---

## Tham Khảo Học Thuật

1. Jegadeesh, N., & Titman, S. (1993). *Returns to Buying Winners and Selling Losers.* Journal of Finance.
2. Baker, M., Bradley, B., & Wurgler, J. (2011). *Benchmarks as Limits to Arbitrage.* Financial Analysts Journal.
3. Moskowitz, T., Ooi, Y. H., & Pedersen, L. H. (2012). *Time Series Momentum.* Journal of Financial Economics.
4. Black, F., & Litterman, R. (1992). *Global Portfolio Optimization.* Financial Analysts Journal.
5. Ledoit, O., & Wolf, M. (2004). *A Well-Conditioned Estimator for Large-Dimensional Covariance Matrices.* Journal of Multivariate Analysis.
6. Maillard, S., Roncalli, T., & Teïletche, J. (2010). *The Properties of Equally Weighted Risk Contribution Portfolios.* Journal of Portfolio Management.
7. Chopra, V. K., & Ziemba, W. T. (1993). *The Effect of Errors in Means, Variances, and Covariances on Optimal Portfolio Choice.* Journal of Portfolio Management.
8. Pardo, R. (2008). *The Evaluation and Optimization of Trading Strategies.* Wiley.

---

*DNT Quant Lab — Engineered by Doan Nguyen Tri*
