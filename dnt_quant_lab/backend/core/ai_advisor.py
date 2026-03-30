import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env từ thư mục backend
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


def _get_model():
    """Khởi tạo Gemini model từ API Key trong .env."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def _format_vnd(value: float) -> str:
    """Định dạng số tiền VNĐ."""
    return f"{value:,.0f}đ"


def build_prompt(data: dict, lang: str = "vi") -> str:
    """
    Xây dựng prompt chuyên nghiệp từ kết quả Monte Carlo + Stress Test.
    Hỗ trợ cả Optimizer (max_sharpe) lẫn Evaluator mode.
    """
    mc = data.get("monte_carlo", {})
    stress = data.get("stress_test", {})

    # --- Trích xuất dữ liệu theo từng mode ---
    is_optimizer = "max_sharpe" in mc

    if is_optimizer:
        ms = mc["max_sharpe"]
        values = mc["monetary_values"]
        expected_return_pct = ms.get("expected_return", 0) * 100
        volatility_pct = ms.get("volatility", 0) * 100
        sharpe = ms.get("sharpe", 0)
        weights: dict = ms.get("weights", {})
        initial_capital = values.get("initial_capital", 0)
        timeframe_note = "1 năm (252 ngày giao dịch)"
    else:
        values = mc.get("monetary_values", {})
        expected_return_pct = mc.get("expected_return", 0) * 100
        volatility_pct = mc.get("volatility", 0) * 100
        sharpe = None
        weights = {}
        initial_capital = values.get("initial_capital", 0)
        days = mc.get("timeframe_days", 63)
        timeframe_map = {21: "1 tháng", 63: "3 tháng", 126: "6 tháng", 252: "1 năm"}
        timeframe_note = timeframe_map.get(days, f"{days} ngày giao dịch")

    expected_value = values.get("expected_value", 0)
    ci_lower = values.get("ci_lower_value", 0)
    ci_upper = values.get("ci_upper_value", 0)
    var_loss = values.get("var_value_loss", 0)

    # Stress Test
    beta = stress.get("portfolio_beta", 1.0)
    stress_loss = stress.get("estimated_loss_vnd", 0)
    crash_pct = abs(stress.get("simulated_market_crash", -0.05)) * 100

    # --- Format phân bổ tỉ trọng ---
    weights_section = ""
    if weights:
        sorted_w = sorted(weights.items(), key=lambda x: -x[1])
        weights_lines = "\n".join(
            f"    • {t}: {w * 100:.1f}%" for t, w in sorted_w
        )
        weights_section = f"\n🏆 **PHÂN BỔ TỐI ƯU (Max Sharpe):**\n{weights_lines}"

    # --- VaR interpretation ---
    if var_loss >= 0:
        var_interpretation = (
            f"+{_format_vnd(var_loss)} "
            f"(ngay cả kịch bản xấu nhất 5%, danh mục ước tính vẫn có lãi)"
        )
    else:
        var_interpretation = (
            f"{_format_vnd(var_loss)} "
            f"(mức lỗ tối đa ước tính ở xác suất 95%)"
        )

    # --- Sharpe assessment ---
    sharpe_note = ""
    if sharpe is not None:
        if sharpe > 1.5:
            sharpe_note = f"{sharpe:.2f} ✨ (Xuất sắc)"
        elif sharpe > 1.0:
            sharpe_note = f"{sharpe:.2f} ✅ (Tốt)"
        elif sharpe > 0.5:
            sharpe_note = f"{sharpe:.2f} ⚠️ (Trung bình)"
        else:
            sharpe_note = f"{sharpe:.2f} ❌ (Kém)"

    # --- Build the prompt string based on language ---
    if lang == "en":
        prompt = f"""You are a professional Vietnamese stock market analyst and investment advisor with over 10 years of real-world trading experience on the HOSE and HNX. Your tone is professional, direct, data-driven, and you never promise guaranteed returns.

Below are the full results of a Monte Carlo quantitative analysis (10,000 random scenarios) for the client's investment portfolio:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **ANALYSIS PARAMETERS:**
- Initial Capital: {_format_vnd(initial_capital)}
- Projected Timeframe: {timeframe_note}
- Model: Markowitz Modern Portfolio Theory + Monte Carlo Simulation

📈 **SIMULATION RESULTS:**
- Expected Return: {expected_return_pct:.2f}%
- Volatility: {volatility_pct:.2f}%
{"- Sharpe Ratio: " + sharpe_note if sharpe is not None else ""}
- Expected Value: {_format_vnd(expected_value)}
- 95% Confidence Interval: [{_format_vnd(ci_lower)} → {_format_vnd(ci_upper)}]
- Value at Risk (VaR 95%): {var_interpretation}

⚡ **STRESS TEST — VN-Index drops -{crash_pct:.0f}%:**
- Portfolio Beta: {beta:.2f}
- Estimated Loss: {_format_vnd(stress_loss)}
{weights_section.replace("PHÂN BỔ TỐI ƯU", "OPTIMAL ALLOCATION")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Based on the simulation results, provide investment advice to the user following this structure:

**1. 📊 Portfolio Overview**
(Assess portfolio quality based on Sharpe, Volatility, and Expected Return. Compare to market benchmark if applicable.)

**2. 💪 Key Strengths**
(List 2-3 specific positive points supported by the data.)

**3. ⚠️ Risk Considerations**
(Analyze Beta, VaR, confidence intervals, and the stress test scenario—are the risks concerning?)

**4. 🎯 Actionable Recommendations**
(Specific advice: hold / rebalance / increase/decrease which positions? Based on optimal allocations if optimizer mode.)

**5. 🔮 Conclusion**
(1-2 concise summary sentences.)

---
⚠️ *Analysis is based on historical data. Past performance is not indicative of future results. This is not official financial advice.*
"""
    else:
        prompt = f"""Bạn là một chuyên gia phân tích và tư vấn đầu tư chứng khoán Việt Nam với hơn 10 năm kinh nghiệm thực chiến tại thị trường HOSE và HNX. Phong cách của bạn: chuyên nghiệp, thẳng thắn, dùng số liệu cụ thể để lập luận, và không hứa hẹn lợi nhuận chắc chắn.

Dưới đây là toàn bộ kết quả phân tích định lượng Monte Carlo (10.000 kịch bản ngẫu nhiên) cho danh mục đầu tư của khách hàng:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **THÔNG SỐ PHÂN TÍCH:**
- Vốn đầu tư: {_format_vnd(initial_capital)}
- Kỳ hạn dự phóng: {timeframe_note}
- Mô hình: Markowitz Modern Portfolio Theory + Monte Carlo Simulation

📈 **KẾT QUẢ MÔ PHỎNG:**
- Lợi nhuận kỳ vọng: {expected_return_pct:.2f}%
- Độ biến động (Volatility): {volatility_pct:.2f}%
{"- Sharpe Ratio: " + sharpe_note if sharpe is not None else ""}
- Giá trị kỳ vọng: {_format_vnd(expected_value)}
- Khoảng tin cậy 95%: [{_format_vnd(ci_lower)} → {_format_vnd(ci_upper)}]
- Rủi ro tối đa VaR (95%): {var_interpretation}

⚡ **STRESS TEST — VN-Index sụt -{crash_pct:.0f}%:**
- Beta danh mục: {beta:.2f}
- Tổn thất ước tính: {_format_vnd(stress_loss)}
{weights_section}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dựa vào kết quả chạy mô phỏng trên, hãy đưa ra lời khuyên đầu tư cho người dùng theo cấu trúc sau:

**1. 📊 Đánh giá tổng quan danh mục**
(Nhận xét về chất lượng danh mục qua các chỉ số — Sharpe, Volatility, kỳ vọng lợi nhuận. So sánh với benchmark thị trường nếu phù hợp.)

**2. 💪 Điểm mạnh nổi bật**
(Liệt kê 2-3 điểm tích cực cụ thể dựa trên số liệu phân tích)

**3. ⚠️ Rủi ro cần lưu ý**
(Phân tích Beta, VaR, khoảng tin cậy, và kịch bản stress test — rủi ro có đáng lo ngại không?)

**4. 🎯 Gợi ý hành động**
(Khuyến nghị cụ thể: nên giữ nguyên / tái cân bằng / tăng/giảm vị thế nào? Dựa vào phân bổ tỉ trọng tối ưu.)

**5. 🔮 Kết luận**
(1-2 câu tóm tắt ngắn gọn nhất)

---
⚠️ *Kết quả phân tích dựa trên dữ liệu lịch sử. Hiệu suất quá khứ không đảm bảo kết quả tương lai. Đây không phải lời khuyên đầu tư chính thức.*
"""
    return prompt


def stream_ai_advice(data: dict, lang: str = "vi"):
    """
    Generator: Gọi Gemini API và yield từng text chunk về cho FastAPI StreamingResponse.
    """
    model = _get_model()

    if model is None:
        err_msg = (
            "⚠️ **Gemini API Key haven't been configured.**\n\n" if lang == "en" else
            "⚠️ **Gemini API Key chưa được cấu hình.**\n\n"
        )
        yield err_msg
        return

    prompt = build_prompt(data, lang)

    try:
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"\n\n❌ **Lỗi khi gọi Gemini API:** {str(e)}"
