# AI Advisor Module using Google Gemini
import os

def generate_f0_advice(portfolio_data: dict, backtest_data: dict, api_key: str) -> str:
    """
    Kết nối với mô hình LLM để dịch số liệu phân tích định lượng thành văn bản cho F0.
    """
    if not api_key:
        return "⚠️ Bạn chưa nhập API Key. Vị cố vấn đầu tư tạm thời 'ngủ đông'!"
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Chọn mô hình nhẹ để sinh text nhanh
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Thiết kế Prompt ("câu lệnh mồi")
        prompt = f"""
        Bạn là một Cố vấn Đầu tư Chuyên nghiệp tại quỹ DNT Quant Lab, Việt Nam.
        Khách hàng của bạn là một nhà đầu tư chứng khoán mới (F0), họ không rành về Toán hay Định lượng.
        
        Hãy đọc bảng kết quả Mô phỏng Tối ưu hóa Danh mục sau đây:
        {portfolio_data}
        
        Và kết quả Backtest lịch sử:
        {backtest_data}
        
        Nhiệm vụ: Hãy viết một bài nhận định (khoảng 300 chữ) bằng Tiếng Việt. 
        - Giải thích vì sao hệ thống lại gợi ý tỉ trọng như vậy (theo kết quả 'max_sharpe').
        - Điểm mạnh của danh mục này là gì?
        - Cảnh báo rủi ro sụt giảm thật nhẹ nhàng nhưng nghiêm túc.
        - Xưng 'Tôi' và gọi khách hàng là 'Quý Nhà Đầu Tư'.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Lỗi khi liên hệ Cố vấn AI: {str(e)}"
