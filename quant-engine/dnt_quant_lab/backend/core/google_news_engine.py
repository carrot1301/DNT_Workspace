"""
Google News Search Engine cho DNT Quant Lab.
Tìm tin tức chủ động từ Google News RSS theo mã cổ phiếu / keyword.
Miễn phí, không cần API Key. Dùng requests + xml.etree (đã có sẵn).
Cache 10 phút trong RAM theo ticker.
"""
import time
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from html import unescape
from urllib.parse import quote_plus

# ═══ RAM Cache ═══
_gnews_cache = {}  # key = ticker, value = {"ts": float, "data": list}
CACHE_TTL = 600  # 10 phút

# ═══ Company Aliases — dùng để build search query chính xác hơn ═══
COMPANY_NAMES = {
    "FPT": "FPT",
    "VCB": "Vietcombank",
    "MBB": "MB Bank",
    "TCB": "Techcombank",
    "HPG": "Hòa Phát",
    "ACB": "ACB",
    "VPB": "VPBank",
    "MWG": "Thế Giới Di Động",
    "VNM": "Vinamilk",
    "VIC": "Vingroup",
    "VHM": "Vinhomes",
    "SSI": "SSI",
    "VJC": "Vietjet",
    "STB": "Sacombank",
    "CTG": "VietinBank",
    "BID": "BIDV",
    "GAS": "PV Gas",
    "MSN": "Masan",
    "PLX": "Petrolimex",
    "PNJ": "PNJ Phú Nhuận",
    "REE": "REE",
    "SAB": "Sabeco",
    "SHB": "SHB",
    "TPB": "TPBank",
    "VIB": "VIB",
    "SSB": "SeABank",
    "POW": "PV Power",
    "BVH": "Bảo Việt",
    "GVR": "Cao su Việt Nam",
    "VRE": "Vincom Retail",
    "VND": "VNDirect",
    "HDB": "HDBank",
    "VCI": "Vietcap",
    "DGC": "Đức Giang Hóa chất",
    "KDH": "Khang Điền",
    "NLG": "Nam Long",
    "DPM": "Đạm Phú Mỹ",
    "DCM": "Đạm Cà Mau",
    "PHR": "Phước Hòa",
    "GMD": "Gemadept",
    "VCG": "Vinaconex",
    "HAG": "Hoàng Anh Gia Lai",
    "DXG": "Đất Xanh",
    "PDR": "Phát Đạt",
    "KBC": "Kinh Bắc",
    "IJC": "Becamex IJC",
    "BCM": "Becamex IDC",
    "HSG": "Hoa Sen",
    "NKG": "Nam Kim",
    "VCK": "Vĩnh Cửu",
    "EIB": "Eximbank",
    "LPB": "LienVietPostBank",
    "OCB": "OCB",
    "TCH": "Hoàng Huy",
    "VGC": "Viglacera",
    "PC1": "PC1",
    "GEX": "Gelex",
    "PVD": "PV Drilling",
    "PVS": "PV Kỹ thuật",
    "BSR": "Lọc Hóa dầu Bình Sơn",
    "ORS": "Chứng khoán Tiên Phong",
    "CTS": "Chứng khoán Vietinbank",
    "SHS": "Chứng khoán Sài Gòn Hà Nội",
    "HCM": "Chứng khoán Hồ Chí Minh",
    "AGG": "An Gia",
    "DIG": "DIC Corp",
    "CEO": "CEO Group",
    "NVL": "Novaland",
    "HDG": "Hà Đô",
    "SCR": "TTC Land",
    "ANV": "Nam Việt",
    "VHC": "Vĩnh Hoàn",
    "IDC": "IDICO",
}


def _clean_html(raw_html: str) -> str:
    """Loại bỏ HTML tags, giữ text thuần."""
    if not raw_html:
        return ""
    text = unescape(raw_html)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _parse_rss_date(date_str: str) -> str:
    """Parse RSS date string (RFC 2822) thành ISO format."""
    if not date_str:
        return ""
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str.strip())
        return dt.isoformat()
    except Exception:
        pass
    for fmt in [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
    ]:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.isoformat()
        except ValueError:
            continue
    return date_str


def _build_search_query(ticker: str) -> str:
    """
    Build search query tối ưu cho Google News.
    Ưu tiên: tên công ty + 'cổ phiếu' (cho kết quả Tiếng Việt sát nhất).
    Fallback: dùng mã ticker trực tiếp.
    """
    ticker = ticker.upper().strip()
    company_name = COMPANY_NAMES.get(ticker, "")

    if company_name:
        # Ưu tiên tìm theo tên công ty + mã ticker
        return f'"{company_name}" OR "{ticker}" cổ phiếu'
    else:
        # Mã không có trong mapping → tìm generic
        return f'"{ticker}" cổ phiếu chứng khoán'


def search_google_news(query: str, max_results: int = 5) -> list:
    """
    Tìm tin tức từ Google News RSS feed.
    
    Args:
        query: Search keyword (VD: '"Vietcombank" OR "VCB" cổ phiếu')
        max_results: Số lượng kết quả tối đa

    Returns:
        list of dict: [{title, summary, link, pubDate, source, sourceIcon}, ...]
    """
    encoded_query = quote_plus(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=vi&gl=VN&ceid=VN:vi"

    try:
        res = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            timeout=10,
        )
        if res.status_code != 200:
            print(f"Google News RSS Error: HTTP {res.status_code} for query='{query}'")
            return []

        root = ET.fromstring(res.content)
        items = root.findall(".//item")[:max_results]

        results = []
        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            date_el = item.find("pubDate")
            desc_el = item.find("description")
            source_el = item.find("source")

            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            link = link_el.text.strip() if link_el is not None and link_el.text else ""
            pub_date = date_el.text if date_el is not None and date_el.text else ""
            raw_desc = desc_el.text if desc_el is not None and desc_el.text else ""
            source_name = source_el.text.strip() if source_el is not None and source_el.text else "Google News"

            summary = _clean_html(raw_desc)
            if len(summary) > 200:
                summary = summary[:200].rsplit(' ', 1)[0] + "..."

            if title:
                results.append({
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "pubDate": _parse_rss_date(pub_date),
                    "publishDate": _parse_rss_date(pub_date),  # Tương thích format vnstock
                    "source": source_name,
                    "sourceIcon": "🔍",
                })

        return results

    except ET.ParseError as e:
        print(f"Google News XML Parse Error: {e}")
        return []
    except Exception as e:
        print(f"Google News Fetch Error: {e}")
        return []


def search_ticker_news(ticker: str, limit: int = 5) -> list:
    """
    Tìm tin tức liên quan đến mã cổ phiếu cụ thể từ Google News.
    Có RAM cache theo ticker (TTL 10 phút).

    Args:
        ticker: Mã cổ phiếu (VD: 'VND', 'FPT', 'VCK')
        limit: Số bài tối đa

    Returns:
        list of dict tương thích format vnstock news
    """
    ticker = ticker.upper().strip()
    now = time.time()

    # Check cache
    cached = _gnews_cache.get(ticker)
    if cached and (now - cached["ts"]) < CACHE_TTL:
        return cached["data"][:limit]

    # Build query và search
    query = _build_search_query(ticker)
    results = search_google_news(query, max_results=limit)

    # Cập nhật cache
    _gnews_cache[ticker] = {"ts": now, "data": results}

    return results[:limit]


def get_google_news_for_ai_prompt(tickers: list, limit_per_ticker: int = 3) -> str:
    """
    Tạo text block tin tức Google News để inject vào AI prompt.
    Format phù hợp cho Gemini đọc.
    """
    if not tickers:
        return ""

    lines = []
    seen_titles = set()

    for ticker in tickers:
        articles = search_ticker_news(ticker, limit=limit_per_ticker)
        if articles:
            lines.append(f"  [{ticker}]:")
            for art in articles:
                title = art.get("title", "")
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                source = art.get("source", "")
                pub = art.get("pubDate", "")[:10]
                summary = art.get("summary", "")[:150]
                lines.append(f"    - [{pub}] ({source}) {title}")
                if summary:
                    lines.append(f"      Tóm tắt: {summary}")

    if not lines:
        return ""

    return "\n".join(lines)
