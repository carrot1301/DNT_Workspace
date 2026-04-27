# Báo Cáo Phương Pháp Định Lượng (Quant Methodology) - DNT Quant Lab

Tài liệu này mô tả chi tiết các mô hình toán học và logic định lượng được sử dụng trong nền tảng **DNT Quant Lab** để tối ưu hóa danh mục đầu tư và phân bổ tài sản. Các nâng cấp gần đây tập trung vào việc giải quyết các hạn chế của mô hình Mean-Variance Optimization (MVO) truyền thống.

## 1. Kiến Trúc Cốt Lõi: Markowitz Mean-Variance Optimization (MVO)

Nền tảng sử dụng MVO để tìm ra tập hợp các danh mục đầu tư tối ưu (Efficient Frontier), tối đa hóa tỷ lệ Sharpe (Sharpe Ratio).

*   **Hàm Mục Tiêu:** Tối đa hóa Lợi nhuận kỳ vọng điều chỉnh theo rủi ro (Risk-adjusted return). Tương đương với việc cực tiểu hóa Tỷ lệ Sharpe âm.
    *   $Sharpe = \frac{E(R_p) - R_f}{\sigma_p}$
    *   Trong đó $E(R_p)$ là lợi nhuận kỳ vọng của danh mục, $R_f$ là lãi suất phi rủi ro, và $\sigma_p$ là độ lệch chuẩn của danh mục.
*   **Ma Trận Hiệp Phương Sai (Covariance Matrix):** Sử dụng phương pháp **Ledoit-Wolf Shrinkage** để ước lượng ma trận hiệp phương sai. Điều này giúp giảm thiểu sai số ước lượng (estimation error) khi số lượng mẫu dữ liệu (số ngày) nhỏ hơn so với bình phương số lượng tài sản, làm cho ma trận nghịch đảo ổn định hơn.
*   **Lực Cản Biến Động (Variance Drag):** Lợi nhuận trung bình cộng (Arithmetic Mean) thường đánh giá quá cao Lợi nhuận kỳ vọng tích lũy theo thời gian thực (Geometric Mean). Do đó, hệ thống áp dụng Variance Drag:
    *   $E(R_{geometric}) \approx E(R_{arithmetic}) - \frac{\sigma^2}{2}$
*   **Ràng Buộc (Constraints):** Tổng tỷ trọng $\sum w_i = 1$. Tỷ trọng của mỗi tài sản $w_i \in [Min, Max]$ do người dùng tùy chỉnh.

## 2. Mô Hình Nâng Cao: Multi-Factor Model & Black-Litterman

Một điểm yếu cố hữu của MVO là sự nhạy cảm quá mức với dữ liệu đầu vào, đặc biệt là Lợi nhuận kỳ vọng lịch sử (Historical Mean Returns). Việc chỉ sử dụng dữ liệu giá trong quá khứ thường dẫn đến rủi ro tập trung (Concentration Risk) hoặc Overfitting.

Để khắc phục, DNT Quant Lab tích hợp **Mô hình Black-Litterman (BL)** kết hợp với **Mô hình Đa Yếu Tố (Multi-Factor Model)**.

### 2.1. Multi-Factor Expected Returns

Thay vì dựa vào trung bình lịch sử, hệ thống xây dựng điểm số (Composite Factor Score) hoàn toàn từ dữ liệu giá (Entrade OHLCV) dựa trên các Yếu Tố (Factors) đã được chứng minh hiệu quả trong tài chính hành vi:

1.  **Momentum Factor (40% Weight):**
    *   *Logic:* Cổ phiếu đang tăng sẽ có xu hướng tiếp tục tăng (Cross-sectional Momentum).
    *   *Công thức:* Lợi nhuận 6 tháng gần nhất, bỏ qua 1 tháng gần nhất để tránh hiệu ứng đảo chiều ngắn hạn (Short-term Reversal - Jegadeesh & Titman, 1993).
    *   $Momentum = \frac{P_{t-21}}{P_{t-126}} - 1$
2.  **Low-Volatility Factor (30% Weight):**
    *   *Logic:* Cổ phiếu ít biến động thường mang lại lợi nhuận điều chỉnh rủi ro tốt hơn (Low-Volatility Anomaly - Baker, Bradley & Wurgler, 2011).
    *   *Công thức:* Nghịch đảo của Độ lệch chuẩn thường niên (Annualized Volatility).
    *   $VolScore = -\sigma_{daily} \times \sqrt{252}$
3.  **Trend Factor (30% Weight):**
    *   *Logic:* Xu hướng giá so với đường trung bình động dài hạn (Time Series Momentum - Moskowitz, Ooi & Pedersen, 2012).
    *   *Công thức:* $Trend = \frac{P_{current} - SMA200}{SMA200}$

**Chuẩn Hóa Z-Score:** Điểm số thô của mỗi Factor được chuẩn hóa thành phân phối chuẩn (mean=0, std=1) qua Z-Score để có thể cộng gộp, và được giới hạn (clipped) tại $\pm 3\sigma$ để giảm thiểu nhiễu từ các ngoại lai (outliers).

### 2.2. Tích Hợp Black-Litterman

Điểm số tổng hợp (Composite Score) từ Multi-Factor Model được quy đổi thành **Alpha Adjustments** ($\alpha$).
*   Ví dụ: Hệ số quy đổi (Alpha Scale) là $0.06$. Điểm Z-Score $+1.5$ sẽ tương đương mức điều chỉnh $+9\%$ vào Lợi nhuận kỳ vọng.

Các giá trị $\alpha$ này được chuyển thành các Ma trận Quan điểm (Views) $P$ (Ma trận liên kết) và $Q$ (Vector lợi nhuận vượt trội) đưa vào công thức Bayes của Black-Litterman:
*   $E(R) = [(\tau \Sigma)^{-1} + P^T \Omega^{-1} P]^{-1} [(\tau \Sigma)^{-1} \Pi + P^T \Omega^{-1} Q]$
*   Trong đó: $\Pi$ là lợi nhuận ngầm định (Implied Equilibrium Returns), $\Sigma$ là ma trận hiệp phương sai.

**Kết quả:** Mô hình MVO sẽ dựa trên Lợi nhuận kỳ vọng đã được điều chỉnh kết hợp giữa điểm cân bằng thị trường (Equilibrium) và các đánh giá dựa trên Yếu Tố (Factor-based Views), giúp danh mục bền vững hơn.

## 3. Lớp Quản Trị Rủi Ro: Trend Following Overlay

MVO là quá trình tĩnh tại thời điểm $t_0$. Để giảm rủi ro mua vào các cổ phiếu đang trong chu kỳ giảm giá mạnh (Drawdown), hệ thống áp dụng một lớp lọc xu hướng (Trend Overlay) **sau khi** thuật toán tối ưu (Optimizer) chạy xong.

*   **Logic Điều Chỉnh Trọng Số (Weight Adjustment):**
    *   **Uptrend** ($P_{current} \ge SMA50$ và $P_{current} \ge SMA200$): Giữ nguyên trọng số $W$.
    *   **Mild Downtrend** ($SMA200 \le P_{current} < SMA50$): Giảm 40% trọng số ($W_{new} = W \times 0.6$).
    *   **Strong Downtrend** ($P_{current} < SMA200$): Giảm 70% trọng số ($W_{new} = W \times 0.3$).
*   Sau khi điều chỉnh, các trọng số được chuẩn hóa lại (Re-normalized) để đảm bảo tổng luôn bằng 100%.

Điều này tạo ra một hệ thống Hybrid: **Modern Portfolio Theory (MPT) kết hợp với Tactical Asset Allocation (TAA)**.

## 4. Kiểm Thử và Đánh Giá (Backtesting Framework)

Engine Backtest đã được nâng cấp từ chiến lược "Moving Average Crossover" (đòi hỏi tín hiệu mua/bán chậm trễ) sang chiến lược **"Buy-and-Hold"**.

*   Mô phỏng chính xác hiệu suất của Danh mục tối ưu MVO từ đầu kỳ.
*   Tính toán tỷ suất sinh lời tích lũy (Cumulative Returns) dựa trên Tỷ suất sinh lời logarit (Log Returns) hằng ngày, cho phép so sánh benchmark chuẩn xác với VN-INDEX / VN30.

## Kết Luận

Với việc áp dụng Ledoit-Wolf Shrinkage, Variance Drag Correction, Multi-Factor Black-Litterman và Trend Following Overlay, Quant Engine hiện tại không chỉ phụ thuộc vào dữ liệu lợi nhuận lịch sử đơn thuần. Nó cung cấp một cách tiếp cận chủ động, định lượng và thích ứng với biến động xu hướng thị trường Việt Nam.
