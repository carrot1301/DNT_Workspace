import os
import json
import datetime
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
        21: "1 tháng" if lang == "vi" else "1 month", 
        63: "3 tháng" if lang == "vi" else "3 months", 
        126: "6 tháng" if lang == "vi" else "6 months", 
        189: "9 tháng" if lang == "vi" else "9 months",
        252: "1 năm" if lang == "vi" else "1 year",
        504: "2 năm" if lang == "vi" else "2 years",
        756: "3 năm" if lang == "vi" else "3 years"
    }
    timeframe_note = timeframe_map.get(days, f"{days} ngày giao dịch" if lang == "vi" else f"{days} trading days")

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
        if lang == "vi":
            fund_section = " **SỨC KHỎE TÀI CHÍNH (Từ BCTC):**\n"
            for t, fd in fundamentals_data.items():
                fund_section += f"- {t}: Ngành {fd.get('industry', '--')} | P/E: {fd.get('pe', '--')} | P/B: {fd.get('pb', '--')} | Biên ROE: {fd.get('roe', '--')}% | Nợ/Vốn CSH: {fd.get('debt_on_equity', '--')} Lần\n"
            fund_section += "\n*Nhiệm vụ đặc biệt: Hãy đối chiếu tỉ trọng tối ưu phía trên với sức khỏe cơ bản ở đây. Cảnh báo rủi ro nếu thuật toán MVO dồn tỉ trọng quá lớn vào mã có ROE thấp, P/E quá cao hoặc dính nợ rủi ro.*"
        else:
            fund_section = " **FINANCIAL HEALTH (From Statements):**\n"
            for t, fd in fundamentals_data.items():
                fund_section += f"- {t}: Industry {fd.get('industry', '--')} | P/E: {fd.get('pe', '--')} | P/B: {fd.get('pb', '--')} | ROE Margin: {fd.get('roe', '--')}% | Debt/Equity: {fd.get('debt_on_equity', '--')}x\n"
            fund_section += "\n*Special task: Cross-check the optimal allocation above with this fundamental health. Warn of risks if MVO algorithm allocates heavily to stocks with low ROE, very high P/E, or risky debt.*"

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

    # Bổ sung tin tức từ RSS (VnExpress, Tuổi Trẻ) — luôn chạy nếu có tickers
    rss_section = ""
    try:
        # Lấy danh sách tickers từ weights hoặc news_data
        rss_tickers = list(news_data.keys()) if news_data else []
        if not rss_tickers and weights:
            rss_tickers = list(weights.keys())
        
        if rss_tickers:
            from core.rss_engine import get_news_for_ai_prompt
            rss_text = get_news_for_ai_prompt(rss_tickers, limit_per_ticker=3)
            if rss_text:
                if lang == "vi":
                    rss_section = f"\n**TIN TỨC BÁO CHÍ MỚI NHẤT (RSS - VnExpress, Tuổi Trẻ):**\n{rss_text}\n\n*Nhiệm vụ: Đọc kỹ tin tức báo chí này và đối chiếu với dữ liệu định lượng phía trên. Nếu tin tiêu cực liên quan đến mã trong danh mục, hãy cảnh báo rủi ro. Nếu tích cực, xác nhận quan điểm.*"
                else:
                    rss_section = f"\n**LATEST PRESS NEWS (RSS - VnExpress, Tuoi Tre):**\n{rss_text}\n\n*Task: Read these press articles carefully. Cross-reference with quantitative data above. Flag risks if negative news relates to portfolio tickers. Confirm positive sentiment if applicable.*"
    except Exception as e:
        print(f"RSS RAG Error: {e}")

    # Lấy Technical Analysis từ signals_data
    ta_data = data.get("trading_signals", {})
    ta_section = ""
    if ta_data:
        if lang == "vi":
            ta_section = "\n**PHÂN TÍCH KỸ THUẬT (TECHNICAL ANALYSIS - Dài hạn & Ngắn hạn):**\n"
            for t, signal_info in ta_data.items():
                ta_analysis = signal_info.get("ta_analysis")
                if ta_analysis and "summary" in ta_analysis:
                    summary = ta_analysis["summary"]
                    ta_section += f" - {t}: Tổng quan ({summary['overall_signal']}) | Score: {summary['score']:.2f}\n"
                    ta_section += f"   + Trend: SMA20={ta_analysis['trend'].get('SMA20', '')}, SMA50={ta_analysis['trend'].get('SMA50', '')}, SMA200={ta_analysis['trend'].get('SMA200', '')}\n"
                    ta_section += f"   + RSI: {ta_analysis['oscillators'].get('RSI', '')}\n"
                    ta_section += f"   + MACD Line: {ta_analysis['trend'].get('MACD', {}).get('line', '')}\n"
            ta_section += "\n*Nhiệm vụ: Kết hợp TA để đưa ra góc nhìn tham khảo thời điểm vào/ra lệnh ngắn hạn so với chiến lược dài hạn.*"
        else:
            ta_section = "\n**TECHNICAL ANALYSIS:**\n"
            for t, signal_info in ta_data.items():
                ta_analysis = signal_info.get("ta_analysis")
                if ta_analysis and "summary" in ta_analysis:
                    summary = ta_analysis["summary"]
                    ta_section += f" - {t}: Overview ({summary['overall_signal']}) | Score: {summary['score']:.2f}\n"
                    ta_section += f"   + Trend: SMA20={ta_analysis['trend'].get('SMA20', '')}, SMA50={ta_analysis['trend'].get('SMA50', '')}, SMA200={ta_analysis['trend'].get('SMA200', '')}\n"
                    ta_section += f"   + RSI: {ta_analysis['oscillators'].get('RSI', '')}\n"
                    ta_section += f"   + MACD Line: {ta_analysis['trend'].get('MACD', {}).get('line', '')}\n"
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
        if lang == "vi":
            weights_section = f"\n**PHÂN BỔ TỐI ƯU (Max Sharpe):**{b_note}\n{weights_lines}"
        else:
            weights_section = f"\n**OPTIMAL ALLOCATION (Max Sharpe):**{b_note}\n{weights_lines}"

    # --- VaR interpretation ---
    if var_loss >= 0:
        if lang == "vi":
            var_interpretation = (
                f"+{_format_vnd(var_loss)} "
                f"(ngay cả kịch bản xấu nhất 5%, danh mục ước tính vẫn có lãi)"
            )
        else:
            var_interpretation = (
                f"+{_format_vnd(var_loss)} "
                f"(even in the worst 5% scenario, the portfolio is estimated to be profitable)"
            )
    else:
        if lang == "vi":
            var_interpretation = (
                f"{_format_vnd(var_loss)} "
                f"(mức lỗ tối đa ước tính ở xác suất 95%)"
            )
        else:
            var_interpretation = (
                f"{_format_vnd(var_loss)} "
                f"(maximum estimated loss at 95% probability)"
            )

    # --- Sharpe assessment ---
    sharpe_note = ""
    if sharpe is not None:
        if lang == "vi":
            if sharpe > 1.5:
                sharpe_note = f"{sharpe:.2f}  (Xuất sắc)"
            elif sharpe > 1.0:
                sharpe_note = f"{sharpe:.2f}  (Tốt)"
            elif sharpe > 0.5:
                sharpe_note = f"{sharpe:.2f}  (Trung bình)"
            else:
                sharpe_note = f"{sharpe:.2f}  (Kém)"
        else:
            if sharpe > 1.5:
                sharpe_note = f"{sharpe:.2f}  (Excellent)"
            elif sharpe > 1.0:
                sharpe_note = f"{sharpe:.2f}  (Good)"
            elif sharpe > 0.5:
                sharpe_note = f"{sharpe:.2f}  (Average)"
            else:
                sharpe_note = f"{sharpe:.2f}  (Poor)"

    # --- Build the prompt string based on language ---
    current_date_en = datetime.datetime.now().strftime("%B %d, %Y")
    current_date_vi = datetime.datetime.now().strftime("%d/%m/%Y")
    
    if lang == "en":
        prompt = f"""You are a professional quantitative data analyst with over 10 years of experience in the Vietnam stock market (HOSE and HNX). Your tone is professional, direct, data-driven, and you never promise guaranteed returns. You provide insights, not financial advice.

STRICT REQUIREMENT: DO NOT use any emojis or icons in your response. Output as a professional text-based analytical report, using bold text for emphasis where necessary. ALL YOUR OUTPUT MUST BE IN ENGLISH ONLY. Do not mix languages.

{mdd_warning_en}
{overfit_warning_en}

Below are the full results of a Monte Carlo quantitative analysis (10,000 random scenarios) for the client's investment portfolio:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**ANALYSIS PARAMETERS:**
- Date: {current_date_en}
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
{weights_section}
{fund_section}
{ta_section}
{manual_bctc_section}
{news_section}
{rss_section}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Based on the simulation results and fundamental data, provide data-driven insights to the user following this structure:

**1. Portfolio Overview**
(Assess portfolio quality based on Sharpe, Volatility, and Expected Return. Compare to market benchmark if applicable.)

**2. Key Strengths**
(List 2-3 specific positive points supported by the data.)

**3. Risk Considerations**
(Analyze Beta, VaR, confidence intervals, and the stress test scenario—are the risks concerning?)

**4. Actionable Insights**
(Specific insights based on optimal allocations. No direct buy/sell commands.)

**5. Conclusion**
(1-2 concise summary sentences.)

---
*Analysis is based on historical data. Past performance is not indicative of future results. This is an automated assessment, not official financial advice or recommendation.*
"""
    else:
        prompt = f"""Bạn là một chuyên gia phân tích dữ liệu định lượng với hơn 10 năm kinh nghiệm tại thị trường chứng khoán Việt Nam (HOSE và HNX). Phong cách của bạn: chuyên nghiệp, khách quan, dùng số liệu cụ thể để lập luận, tuyệt đối không hô hào hay đảm bảo lợi nhuận. Bạn chỉ cung cấp góc nhìn phân tích, không phải tư vấn tài chính.

YÊU CẦU NGHIÊM NGẶT: TUYỆT ĐỐI KHÔNG sử dụng bất kỳ biểu tượng cảm xúc (emoji) hay icon nào trong câu trả lời của bạn. Trình bày dưới dạng văn bản báo cáo phân tích chuyên nghiệp, chỉ định dạng in đậm để nhấn mạnh các ý quan trọng. TRẢ LỜI HOÀN TOÀN BẰNG TIẾNG VIỆT, KHÔNG ĐƯỢC LẪN LỘN NGÔN NGỮ.

{mdd_warning_vi}
{overfit_warning_vi}

Dưới đây là toàn bộ kết quả phân tích định lượng Monte Carlo (10.000 kịch bản ngẫu nhiên) cho danh mục đầu tư của khách hàng:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**THÔNG SỐ PHÂN TÍCH:**
- Ngày phân tích: {current_date_vi}
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
{rss_section}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dựa vào kết quả chạy mô phỏng và sức khỏe tài chính trên, hãy đưa ra đánh giá dữ liệu chuyên sâu cho người dùng theo cấu trúc sau:

**1. Đánh giá tổng quan danh mục**
(Nhận xét về chất lượng danh mục qua các chỉ số — Sharpe, Volatility, kỳ vọng lợi nhuận. So sánh với benchmark thị trường nếu phù hợp.)

**2. Điểm mạnh nổi bật**
(Liệt kê 2-3 điểm tích cực cụ thể dựa trên số liệu phân tích)

**3. Rủi ro cần lưu ý**
(Phân tích Beta, VaR, khoảng tin cậy, và kịch bản stress test — rủi ro có đáng lo ngại không?)

**4. Góc nhìn tham khảo**
(Đánh giá khách quan các kịch bản hành động dựa vào phân bổ tỉ trọng tối ưu, không dùng từ ngữ ra lệnh hay xúi giục giao dịch trực tiếp.)

**5. Kết luận**
(1-2 câu tóm tắt ngắn gọn nhất)

---
*Kết quả tính toán từ thuật toán ngẫu nhiên. Hiệu suất quá khứ không đảm bảo kết quả tương lai. Đây chỉ là thông tin tham khảo, tuyệt đối không cấu thành tư vấn hay khuyến nghị đầu tư.*
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

def copilot_chat(message: str, context: dict, lang: str = "vi"):
    """
    Generator: Gửi câu hỏi của người dùng kèm context danh mục cho Gemini API và stream kết quả.
    """
    model = _get_model()

    if model is None:
        err_msg = "**Gemini API Key chưa được cấu hình.**\n\n" if lang == "vi" else "**Gemini API Key haven't been configured.**\n\n"
        yield err_msg
        return

    sys_prompt = f"""
Bạn là DNT Quant Copilot - một trợ lý AI chuyên nghiệp về phân tích định lượng (Quantitative Finance) của dự án DNT Quant Lab.
QUY TẮC PHÁP LÝ TỐI THƯỢNG: TUYỆT ĐỐI KHÔNG SỬ DỤNG CÁC TỪ NGỮ SAU DƯỚI MỌI HÌNH THỨC: "khuyến nghị", "khuyên bạn", "mua", "bán", "nên đầu tư", "nên giữ", "vào lệnh", "chốt lời", "cắt lỗ".
Mọi câu trả lời PHẢI dùng ngôn ngữ trung lập, phân tích dữ liệu, đánh giá rủi ro, và xác suất. Ví dụ: "Dữ liệu cho thấy", "Thuật toán phân bổ", "Tỷ trọng ưu tiên", "Có dấu hiệu rủi ro".

Dưới đây là Dữ liệu Danh mục hiện tại (JSON):
{json.dumps(context, ensure_ascii=False)}

Hãy trả lời câu hỏi sau của người dùng một cách ngắn gọn, súc tích (dưới 150 chữ), đi thẳng vào vấn đề bằng {'Tiếng Việt' if lang == 'vi' else 'English'}:
Câu hỏi: {message}
    """

    import time
    try:
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        response = model.generate_content(sys_prompt, stream=True, safety_settings=safety_settings)
        for chunk in response:
            try:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
            except (ValueError, AttributeError):
                continue
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            msg = "Hệ thống AI đang quá tải. Vui lòng thử lại sau 1 phút." if lang == "vi" else "AI Server is overloaded. Please try again in 1 minute."
            yield f"\n\n**🤖 {msg}**"
        else:
            yield f"\n\n**Lỗi:** {error_msg}"

def analyze_sentiment(news_data: dict, lang: str = "vi") -> dict:
    """
    Nhận tin tức dưới dạng dict, trả về điểm sentiment cho mỗi mã.
    """
    model = _get_model()
    if model is None:
        return {t: 0 for t in news_data.keys()}
        
    sys_prompt = f"""
Bạn là một công cụ AI phân tích NLP chuyên về tài chính. Đánh giá Sentiment (Tâm lý thị trường) dựa trên các bản tin sau.
Trọng số điểm: 0.0 (Rất Tiêu Cực), 0.5 (Trung Tính), 1.0 (Rất Tích Cực).
Dữ liệu tin tức:
{json.dumps(news_data, ensure_ascii=False)}

Chỉ trả về MỘT chuỗi JSON ĐÚNG CHUẨN duy nhất, không có markdown text bao quanh, với định dạng key là Mã CP, value là Float:
{{"FPT": 0.8, "MWG": 0.2, "VIC": 0.5}}
Tuyệt đối không dùng các từ khuyến nghị.
    """
    
    try:
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        response = model.generate_content(sys_prompt, safety_settings=safety_settings)
        text = response.text.strip() if hasattr(response, 'text') and response.text else "{}"
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Sentiment Analysis Error: {e}")
        return {t: 0.5 for t in news_data.keys()}

def copilot_chat_public(message: str, lang: str = "vi"):
    """
    Public Copilot for Landing Page — no auth, no simulation context.
    Focuses on introducing DNT Quant Lab features.
    """
    model = _get_model()
    if model is None:
        yield "API chưa sẵn sàng." if lang == "vi" else "API not ready."
        return

    if lang == "vi":
        system_prompt = """Bạn là "DNT Quant Copilot" — trợ lý AI trên trang chủ của nền tảng DNT Quant Lab.
Vai trò: Giới thiệu và giải đáp thắc mắc cho khách truy cập về các tính năng nền tảng.

TÍNH NĂNG CHÍNH CỦA DNT QUANT LAB:
- Mô phỏng Monte Carlo 10,000 kịch bản tối ưu hóa danh mục (Max Sharpe, Min Variance)
- Stress Test với kịch bản Thiên Nga Đen (VN-INDEX sụt 5%)
- Phân tích AI: Gemini đọc Báo Cáo Tài Chính tự động
- Hệ thống Tín hiệu kỹ thuật: RSI, Moving Averages, Breakout
- Kiểm thử chiến lược quá khứ (Backtrader Engine)
- Cỗ Máy Thời Gian (Backtest Time-Machine)
- AI Sentiment Radar phân tích tâm lý thị trường
- Tùy Biến Rủi Ro (Custom Constraints)
- Hệ thống đa ngôn ngữ (Tiếng Việt & English)

QUY TẮC:
- Trả lời ngắn gọn (3-5 câu), thân thiện, chuyên nghiệp.
- TUYỆT ĐỐI KHÔNG dùng từ "khuyến nghị", "nên mua", "nên bán" hay bất kỳ từ mang tính tư vấn đầu tư.
- Đây là công cụ phân tích dữ liệu, KHÔNG phải dịch vụ tư vấn tài chính.
- Khuyến khích khách bấm vào Dashboard để trải nghiệm.
"""
    else:
        system_prompt = """You are "DNT Quant Copilot" — the AI assistant on the DNT Quant Lab landing page.
Role: Introduce and answer visitor questions about the platform's features.

KEY FEATURES:
- Monte Carlo Simulation (10,000 scenarios) for portfolio optimization (Max Sharpe, Min Variance)
- Stress Test with Black Swan scenarios (VN-INDEX -5%)
- AI Analysis: Gemini auto-reads Financial Statements
- Technical Signal System: RSI, Moving Averages, Breakout
- Historical Strategy Testing (Backtrader Engine)
- Time Machine (Backtest from past to present)
- AI Sentiment Radar for market mood analysis
- Custom Risk Constraints
- Bilingual system (Vietnamese & English)

RULES:
- Answer briefly (3-5 sentences), friendly, professional.
- NEVER use words like "recommend", "should buy", "should sell" or any investment advisory language.
- This is a data analysis tool, NOT a financial advisory service.
- Encourage visitors to open the Dashboard.
"""

    try:
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        response = model.generate_content(
            [system_prompt, f"User: {message}"],
            stream=True,
            generation_config=genai.types.GenerationConfig(max_output_tokens=800, temperature=0.7),
            safety_settings=safety_settings
        )
        for chunk in response:
            try:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
            except (ValueError, AttributeError):
                continue
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            msg = "Hệ thống AI đang quá tải. Vui lòng thử lại sau." if lang == "vi" else "AI system is overloaded. Please try again later."
            yield msg
        else:
            yield f"Lỗi: {error_msg}"
