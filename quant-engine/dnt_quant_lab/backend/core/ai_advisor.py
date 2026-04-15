import os
import json
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
    adv = data.get("advanced_metrics", {})
    fundamentals_data = data.get("fundamentals", {})

    # --- Trích xuất dữ liệu theo từng mode ---
    is_optimizer = "max_sharpe" in mc

    # Lấy thông tin thời gian (áp dụng chung)
    days = mc.get("timeframe_days", 252) # Mặc định 252 (1 năm)
    timeframe_map = {
        21: "1 tháng", 
        63: "3 tháng", 
        126: "6 tháng", 
        189: "9 tháng",
        252: "1 năm",
        504: "2 năm",
        756: "3 năm"
    }
    timeframe_note = timeframe_map.get(days, f"{days} ngày giao dịch")

    if is_optimizer:
        ms = mc["max_sharpe"]
        values = mc["monetary_values"]
        expected_return_pct = ms.get("expected_return", 0) * 100
        volatility_pct = ms.get("volatility", 0) * 100
        sharpe = ms.get("sharpe", 0)
        weights: dict = ms.get("weights", {})
        initial_capital = values.get("initial_capital", 0)
    else:
        values = mc.get("monetary_values", {})
        expected_return_pct = mc.get("expected_return", 0) * 100
        volatility_pct = mc.get("volatility", 0) * 100
        sharpe = None
        weights = {}
        initial_capital = values.get("initial_capital", 0)

    expected_value = values.get("expected_value", 0)
    ci_lower = values.get("ci_lower_value", 0)
    ci_upper = values.get("ci_upper_value", 0)
    var_loss = values.get("var_value_loss", 0)

    # Stress Test
    beta = stress.get("portfolio_beta", 1.0)
    stress_loss = stress.get("estimated_loss_vnd", 0)
    crash_pct = abs(stress.get("simulated_market_crash", -0.05)) * 100
    
    # Advanced Metrics (Max Drawdown)
    advanced = data.get("advanced_metrics", {})
    max_drawdown = advanced.get("max_drawdown", 0)
    mdd_pct = abs(max_drawdown) * 100
    
    mdd_warning_en = ""
    mdd_warning_vi = ""
    if mdd_pct > 20:
        mdd_warning_en = f"\n CRITICAL RISK WARNING: As a strict Quantitative Risk Director, you MUST explicitly evaluate the 'Max Drawdown' which is currently {mdd_pct:.2f}% (> 20%). Compare this directly with the Expected Return ({expected_return_pct:.2f}%). Warn the user about the psychological risk of holding this portfolio. Analyze the trade-off: Is the expected return worth the risk of devastating losses from the peak? Be firm and professional."
        mdd_warning_vi = f"\n CẢNH BÁO RỦI RO TỚI HẠN: Trong vai trò là một Giám đốc Quản trị Rủi ro Định lượng khắt khe, bạn BẮT BUỘC phải đánh giá trực tiếp chỉ số 'Max Drawdown' (Mức sụt giảm tối đa hiện tại là {mdd_pct:.2f}%, > 20%). Hãy so sánh trực tiếp Max Drawdown này với Kỳ vọng lợi nhuận ({expected_return_pct:.2f}%). Phải cảnh báo người dùng về rủi ro tâm lý khi nắm giữ. Phân tích bài toán Đánh đổi: Liệu lợi nhuận kỳ vọng có xứng đáng với nguy cơ chia tài khoản từ đỉnh hay không? Hãy đưa ra nhận định thẳng thắn và chuyên nghiệp."

    # Lời nhắc về Overfitting (Yêu cầu của người dùng)
    overfit_warning_en = ""
    overfit_warning_vi = ""
    if any(w >= 0.30 for w in weights.values()) or 'VIC' in weights:
        overfit_warning_en = "\n OVERFITTING WARNING: The model heavily leverages historical volatility/Alpha (especially checking for VIC or >=30% allocations). Inform the user that this might be 'Severe Overfitting'. They should strongly research financial statements or consult experts rather than purely trusting the mathematical weights."
        overfit_warning_vi = "\n LƯU Ý QUAN TRỌNG: Mô hình có dấu hiệu bị 'Overfitting nặng' (quá khớp) do dồn tỉ trọng vào các mã có độ biến động/Alpha cao trong quá khứ (như VIC). Hãy khuyên người dùng tìm hiểu kỹ Báo cáo tài chính và ý kiến chuyên gia, không nên nhắm mắt tin vào tỷ trọng này."

    # --- Tóm tắt Fundamentals (BCTC) ---
    fund_section = ""
    if fundamentals_data:
        fund_section = " **SỨC KHỎE TÀI CHÍNH (Từ BCTC):**\n"
        for t, fd in fundamentals_data.items():
            fund_section += f"- {t}: Ngành {fd.get('industry', '--')} | P/E: {fd.get('pe', '--')} | P/B: {fd.get('pb', '--')} | Biên ROE: {fd.get('roe', '--')}% | Nợ/Vốn CSH: {fd.get('debt_on_equity', '--')} Lần\n"
        fund_section += "\n*Nhiệm vụ đặc biệt: Hãy đối chiếu tỉ trọng tối ưu phía trên với sức khỏe cơ bản ở đây. Cảnh báo rủi ro nếu thuật toán MVO dồn tỉ trọng quá lớn vào mã có ROE thấp, P/E quá cao hoặc dính nợ rủi ro.*"

    # Lấy thêm list manual BCTC (RAG Mode)
    manual_bctc_tickers = data.get("manual_bctc_tickers", [])
    manual_bctc_section = ""
    if manual_bctc_tickers:
        registry_path = os.path.join(os.path.dirname(__file__), "..", "data", "bctc_registry.json")
        if os.path.exists(registry_path):
            with open(registry_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
            
            for t in manual_bctc_tickers:
                t = t.upper()
                if t in registry:
                    bctc_file = registry[t].get("file")
                    bctc_path = os.path.join(os.path.dirname(__file__), "..", "data", "bctc_manual", bctc_file)
                    if os.path.exists(bctc_path):
                        with open(bctc_path, "r", encoding="utf-8") as bf:
                            content = bf.read()
                            manual_bctc_section += f"\n\n--- BÁO CÁO TÀI CHÍNH THỦ CÔNG: {t} ---\n{content}\n"
    
        if manual_bctc_section:
            if lang == "vi":
                manual_bctc_section = f"\n **TÀI LIỆU BCTC BỔ SUNG (RAG MODE):**\nNgười dùng đã chủ động đính kèm BCTC chuyên sâu dưới đây cho các mã {', '.join(manual_bctc_tickers)}. Bạn PHẢI đọc kỹ và dùng thông tin này làm trọng tâm để tư vấn dài hạn, đối chiếu chúng với trọng số của thuật toán Quant." + manual_bctc_section
            else:
                manual_bctc_section = f" **SUPPLEMENTARY FINANCIAL REPORTS (RAG MODE):**\nThe user actively attached the following deep-dive reports for {', '.join(manual_bctc_tickers)}. You MUST read this carefully and use it as the core for long-term advice, contrasting it against the Quant algorithm's weights." + manual_bctc_section

    # Lấy tin tức (vnstock3 - RAG)
    news_data = data.get("news_data", {})
    news_section = ""
    if news_data:
        if lang == "vi":
            news_section = "\n**TIN TỨC THỊ TRƯỜNG MỚI NHẤT (SENTIMENT):**\n"
        else:
            news_section = "\n**LATEST MARKET NEWS (SENTIMENT):**\n"

        for t, news_list in news_data.items():
            if news_list:
                news_section += f" {t}:\n"
                for nItem in news_list:
                    news_section += f"  - [{nItem.get('publishDate', '')}] {nItem.get('title', '')}: {nItem.get('summary', '')}\n"
        
        if lang == "vi":
            news_section += "\n*Nhiệm vụ: Hãy phân tích tâm lý dòng tiền (Sentiment) từ các tin tức này để kết hợp với số liệu định lượng, đưa ra thông điệp mua/bán.*"
        else:
            news_section += "\n*Task: Analyze market sentiment from these news events to evaluate the short-term outlook, combined with the quantitative metrics.*"

    # Lấy Technical Analysis từ signals_data
    ta_data = data.get("trading_signals", {})
    ta_section = ""
    if ta_data:
        if lang == "vi":
            ta_section = "\n**PHÂN TÍCH KỸ THUẬT (TECHNICAL ANALYSIS - Dài hạn & Ngắn hạn):**\n"
        else:
            ta_section = "\n**TECHNICAL ANALYSIS:**\n"
        for t, signal_info in ta_data.items():
            ta_analysis = signal_info.get("ta_analysis")
            if ta_analysis and "summary" in ta_analysis:
                summary = ta_analysis["summary"]
                ta_section += f" - {t}: Tổng quan ({summary['overall_signal']}) | Score: {summary['score']:.2f}\n"
                ta_section += f"   + Trend: SMA20={ta_analysis['trend'].get('SMA20', '')}, SMA50={ta_analysis['trend'].get('SMA50', '')}, SMA200={ta_analysis['trend'].get('SMA200', '')}\n"
                ta_section += f"   + RSI: {ta_analysis['oscillators'].get('RSI', '')}\n"
                ta_section += f"   + MACD Line: {ta_analysis['trend'].get('MACD', {}).get('line', '')}\n"
        if lang == "vi":
            ta_section += "\n*Nhiệm vụ: Kết hợp TA để đưa ra khuyến nghị thời điểm mua/bán ngắn hạn so với chiến lược dài hạn.*"
        else:
            ta_section += "\n*Task: Combine TA signals to advise on short-term entry/exit points alongside the long-term strategy.*"

    # --- Format phân bổ tỉ trọng ---
    bl_event = mc.get("black_litterman_event", {})
    is_bl_active = bl_event.get("is_active", False)
    
    weights_section = ""
    if weights:
        b_note = ""
        if is_bl_active:
            if lang == "vi":
                b_note = "\n*(Lưu ý từ thuật toán Quant: Phân bổ này đã được tái định giá bằng thuật toán Black-Litterman (theo ma trận P, Q). Hệ thống tự động đẩy Alpha kỳ vọng với nhóm cổ phiếu hưởng lợi từ lộ trình Nâng hạng FTSE 4 giai đoạn. Bạn hãy nhắc người dùng điều này khi phân tích)*\n"
            else:
                b_note = "\n*(Quant Engine Note: Returns have been recalibrated using the Black-Litterman algorithm. Alpha was injected for key stocks benefiting from the 4-phase FTSE upgrade. Mention this to the user).* \n"

        sorted_w = sorted(weights.items(), key=lambda x: -x[1])
        weights_lines = "\n".join(
            f"    • {t}: {w * 100:.1f}%" for t, w in sorted_w
        )
        weights_section = f"\n**PHÂN BỔ TỐI ƯU (Max Sharpe):**{b_note}\n{weights_lines}"

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
            sharpe_note = f"{sharpe:.2f}  (Xuất sắc)"
        elif sharpe > 1.0:
            sharpe_note = f"{sharpe:.2f}  (Tốt)"
        elif sharpe > 0.5:
            sharpe_note = f"{sharpe:.2f}  (Trung bình)"
        else:
            sharpe_note = f"{sharpe:.2f}  (Kém)"

    # --- Build the prompt string based on language ---
    if lang == "en":
        prompt = f"""You are a professional Vietnamese stock market analyst and investment advisor with over 10 years of real-world trading experience on the HOSE and HNX. Your tone is professional, direct, data-driven, and you never promise guaranteed returns. 

STRICT REQUIREMENT: DO NOT use any emojis or icons in your response. Output as a professional text-based analytical report, using bold text for emphasis where necessary.

{mdd_warning_en}
{overfit_warning_en}

Below are the full results of a Monte Carlo quantitative analysis (10,000 random scenarios) for the client's investment portfolio:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**ANALYSIS PARAMETERS:**
- Initial Capital: {_format_vnd(initial_capital)}
- Projected Timeframe: {timeframe_note}
- Model: Markowitz Modern Portfolio Theory + Monte Carlo Simulation

**SIMULATION RESULTS:**
- Expected Return: {expected_return_pct:.2f}%
- Volatility: {volatility_pct:.2f}%
{"- Sharpe Ratio: " + sharpe_note if sharpe is not None else ""}
- Expected Value: {_format_vnd(expected_value)}
- 95% Confidence Interval: [{_format_vnd(ci_lower)} → {_format_vnd(ci_upper)}]
- Value at Risk (VaR 95%): {var_interpretation}

**STRESS TEST — VN-Index drops -{crash_pct:.0f}%:**
- Portfolio Beta: {beta:.2f}
- Estimated Loss: {_format_vnd(stress_loss)}
{weights_section.replace("PHÂN BỔ TỐI ƯU", "OPTIMAL ALLOCATION")}
{fund_section}
{ta_section}
{manual_bctc_section}
{news_section}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Based on the simulation results and fundamental data, provide investment advice to the user following this structure:

**1. Portfolio Overview**
(Assess portfolio quality based on Sharpe, Volatility, and Expected Return. Compare to market benchmark if applicable.)

**2. Key Strengths**
(List 2-3 specific positive points supported by the data.)

**3. Risk Considerations**
(Analyze Beta, VaR, confidence intervals, and the stress test scenario—are the risks concerning?)

**4. Actionable Recommendations**
(Specific advice: hold / rebalance / increase/decrease which positions? Based on optimal allocations if optimizer mode.)

**5. Conclusion**
(1-2 concise summary sentences.)

---
*Analysis is based on historical data. Past performance is not indicative of future results. This is not official financial advice.*
"""
    else:
        prompt = f"""Bạn là một chuyên gia phân tích và tư vấn đầu tư chứng khoán Việt Nam với hơn 10 năm kinh nghiệm thực chiến tại thị trường HOSE và HNX. Phong cách của bạn: chuyên nghiệp, thẳng thắn, dùng số liệu cụ thể để lập luận, và không hứa hẹn lợi nhuận chắc chắn.

YÊU CẦU NGHIÊM NGẶT: TUYỆT ĐỐI KHÔNG sử dụng bất kỳ biểu tượng cảm xúc (emoji) hay icon nào trong câu trả lời của bạn. Trình bày dưới dạng văn bản báo cáo phân tích chuyên nghiệp, chỉ định dạng in đậm để nhấn mạnh các ý quan trọng.

{mdd_warning_vi}
{overfit_warning_vi}

Dưới đây là toàn bộ kết quả phân tích định lượng Monte Carlo (10.000 kịch bản ngẫu nhiên) cho danh mục đầu tư của khách hàng:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**THÔNG SỐ PHÂN TÍCH:**
- Vốn đầu tư: {_format_vnd(initial_capital)}
- Kỳ hạn dự phóng: {timeframe_note}
- Mô hình: Markowitz Modern Portfolio Theory + Monte Carlo Simulation

**KẾT QUẢ MÔ PHỎNG:**
- Lợi nhuận kỳ vọng: {expected_return_pct:.2f}%
- Độ biến động (Volatility): {volatility_pct:.2f}%
{"- Sharpe Ratio: " + sharpe_note if sharpe is not None else ""}
- Giá trị kỳ vọng: {_format_vnd(expected_value)}
- Khoảng tin cậy 95%: [{_format_vnd(ci_lower)} → {_format_vnd(ci_upper)}]
- Rủi ro tối đa VaR (95%): {var_interpretation}

**STRESS TEST — VN-Index sụt -{crash_pct:.0f}%:**
- Beta danh mục: {beta:.2f}
- Tổn thất ước tính: {_format_vnd(stress_loss)}
{weights_section}
{fund_section}
{ta_section}
{manual_bctc_section}
{news_section}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dựa vào kết quả chạy mô phỏng và sức khỏe tài chính trên, hãy đưa ra lời khuyên đầu tư cho người dùng theo cấu trúc sau:

**1. Đánh giá tổng quan danh mục**
(Nhận xét về chất lượng danh mục qua các chỉ số — Sharpe, Volatility, kỳ vọng lợi nhuận. So sánh với benchmark thị trường nếu phù hợp.)

**2. Điểm mạnh nổi bật**
(Liệt kê 2-3 điểm tích cực cụ thể dựa trên số liệu phân tích)

**3. Rủi ro cần lưu ý**
(Phân tích Beta, VaR, khoảng tin cậy, và kịch bản stress test — rủi ro có đáng lo ngại không?)

**4. Gợi ý hành động**
(Khuyến nghị cụ thể: nên giữ nguyên / tái cân bằng / tăng/giảm vị thế nào? Dựa vào phân bổ tỉ trọng tối ưu.)

**5. Kết luận**
(1-2 câu tóm tắt ngắn gọn nhất)

---
*Kết quả phân tích dựa trên dữ liệu lịch sử. Hiệu suất quá khứ không đảm bảo kết quả tương lai. Đây không phải lời khuyên đầu tư chính thức.*
"""
    return prompt


def stream_ai_advice(data: dict, lang: str = "vi"):
    """
    Generator: Gọi Gemini API và yield từng text chunk về cho FastAPI StreamingResponse.
    """
    model = _get_model()

    if model is None:
        err_msg = (
            "**Gemini API Key haven't been configured.**\n\n" if lang == "en" else
            "**Gemini API Key chưa được cấu hình.**\n\n"
        )
        yield err_msg
        return

    prompt = build_prompt(data, lang)

    import time
    max_wait = 240
    start_time = time.time()

    while True:
        try:
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                try:
                    txt = chunk.text
                    if txt:
                        yield txt
                except ValueError:
                    # Bỏ qua lỗi invalid Part khi finish_reason=1 (chunk rỗng)
                    pass
            return
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Quota exceeded" in error_msg:
                elapsed = time.time() - start_time
                if elapsed < max_wait:
                    # Giữ kết nối (keep-alive) không bị đứt bởi Koyeb/Vercel timeout trong lúc chờ retry
                    for _ in range(15):
                        yield "<!-- wait -->"
                        time.sleep(1)
                    continue
                else:
                    err_msg_vi = "\n\n**🤖 Máy chủ AI đang quá tải (Rate Limit)**\nDo bạn đang sử dụng gói tính năng AI miễn phí nên hệ thống đã tạm thời giới hạn số lần yêu cầu liên tục để tránh lạm dụng. Vui lòng chờ khoảng **60 giây** rồi thử lại nhé!"
                    err_msg_en = "\n\n**🤖 AI Server is overloaded (Rate Limit)**\nYou are currently using the Free Tier AI which limits rapid consecutive requests. Please wait about **60 seconds** and try again!"
                    
                    msg = err_msg_vi if lang == "vi" else err_msg_en
                    for word in msg.split(" "):
                        yield word + " "
                        time.sleep(0.05)
                    return
            else:
                err_msg = f"\n\n**Lỗi khi gọi Gemini API:** {error_msg}"
                for word in err_msg.split(" "):
                    yield word + " "
                    time.sleep(0.05)
                return
