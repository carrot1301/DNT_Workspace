"""
RSS News Engine cho DNT Quant Lab.
Lấy tin tức thị trường từ VnExpress & Tuổi Trẻ qua RSS feeds.
Cache 15 phút trong RAM. Hỗ trợ lọc theo mã cổ phiếu.
"""
import time
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from html import unescape

# ═══ RSS Feed Sources ═══
RSS_SOURCES = [
    {
        "name": "VnExpress",
        "url": "https://vnexpress.net/rss/kinh-doanh.rss",
        "icon": "📰"
    },
    {
        "name": "Tuổi Trẻ",
        "url": "https://tuoitre.vn/rss/kinh-doanh.rss",
        "icon": "📄"
    },
]

# ═══ RAM Cache ═══
_news_cache = {"ts": 0, "data": []}
CACHE_TTL = 900  # 15 phút


def _clean_html(raw_html: str) -> str:
    """Loại bỏ HTML tags, giữ text thuần."""
    if not raw_html:
        return ""
    text = unescape(raw_html)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _extract_thumbnail(description: str) -> str:
    """Trích xuất URL ảnh thumbnail từ description RSS (thường chứa <img>)."""
    if not description:
        return ""
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', description)
    if match:
        return match.group(1)
    return ""


def _parse_rss_date(date_str: str) -> str:
    """Parse RSS date string (RFC 2822) thành ISO format. Locale-independent."""
    if not date_str:
        return ""
    # RFC 2822 parser (locale-independent, handles "Tue, 28 Apr 2026 13:12:22 +0700")
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str.strip())
        return dt.isoformat()
    except Exception:
        pass
    # Fallback: try standard formats
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


def fetch_rss_news(max_per_source: int = 20) -> list:
    """
    Fetch tin tức từ tất cả RSS sources.
    Cache 15 phút trong RAM.
    Returns: list of dict, sorted by pubDate mới nhất trước.
    """
    now = time.time()
    if _news_cache["data"] and (now - _news_cache["ts"]) < CACHE_TTL:
        return _news_cache["data"]

    all_news = []

    for source in RSS_SOURCES:
        try:
            res = requests.get(
                source["url"],
                headers={"User-Agent": "Mozilla/5.0 DNTQuantLab/1.0"},
                timeout=10
            )
            if res.status_code != 200:
                print(f"RSS Error: {source['name']} returned {res.status_code}")
                continue

            root = ET.fromstring(res.content)
            items = root.findall(".//item")[:max_per_source]

            for item in items:
                title_el = item.find("title")
                desc_el = item.find("description")
                link_el = item.find("link")
                date_el = item.find("pubDate")
                enclosure_el = item.find("enclosure")

                title = title_el.text if title_el is not None and title_el.text else ""
                raw_desc = desc_el.text if desc_el is not None and desc_el.text else ""
                link = link_el.text if link_el is not None and link_el.text else ""
                pub_date = date_el.text if date_el is not None and date_el.text else ""

                # Thumbnail: ưu tiên enclosure, fallback từ description
                thumbnail = ""
                if enclosure_el is not None:
                    thumbnail = enclosure_el.get("url", "")
                if not thumbnail:
                    thumbnail = _extract_thumbnail(raw_desc)

                summary = _clean_html(raw_desc)
                # Cắt summary nếu quá dài
                if len(summary) > 200:
                    summary = summary[:200].rsplit(' ', 1)[0] + "..."

                if title:
                    all_news.append({
                        "title": title.strip(),
                        "summary": summary,
                        "link": link.strip(),
                        "pubDate": _parse_rss_date(pub_date),
                        "source": source["name"],
                        "sourceIcon": source["icon"],
                        "thumbnail": thumbnail,
                    })

        except ET.ParseError as e:
            print(f"RSS XML Parse Error for {source['name']}: {e}")
        except Exception as e:
            print(f"RSS Fetch Error for {source['name']}: {e}")

    # Sort theo thời gian mới nhất
    all_news.sort(key=lambda x: x.get("pubDate", ""), reverse=True)

    # Cập nhật cache
    _news_cache["data"] = all_news
    _news_cache["ts"] = now

    return all_news


def get_market_news(limit: int = 15) -> list:
    """Lấy tin tức tổng hợp cho Landing Page."""
    news = fetch_rss_news()
    return news[:limit]


def search_news_by_tickers(tickers: list, limit: int = 5) -> dict:
    """
    Lọc tin tức có liên quan đến các mã cổ phiếu cụ thể.
    Tìm kiếm trong title + summary.
    
    Returns: dict {ticker: [news_items]}
    """
    news = fetch_rss_news()
    result = {}

    # Mapping tên công ty phổ biến -> ticker để search tốt hơn
    COMPANY_ALIASES = {
        "FPT": ["FPT", "fpt"],
        "VCB": ["VCB", "Vietcombank", "vietcombank", "VIETCOMBANK"],
        "MBB": ["MBB", "MB Bank", "MBBank", "MB bank", "Quân đội"],
        "TCB": ["TCB", "Techcombank", "techcombank"],
        "HPG": ["HPG", "Hòa Phát", "Hoa Phat", "hòa phát"],
        "ACB": ["ACB", "Á Châu"],
        "VPB": ["VPB", "VPBank", "vpbank"],
        "MWG": ["MWG", "Thế Giới Di Động", "Thegioididong", "thế giới di động"],
        "VNM": ["VNM", "Vinamilk", "vinamilk"],
        "VIC": ["VIC", "Vingroup", "vingroup"],
        "VHM": ["VHM", "Vinhomes", "vinhomes"],
        "SSI": ["SSI", "ssi"],
        "VJC": ["VJC", "Vietjet", "vietjet"],
        "STB": ["STB", "Sacombank", "sacombank"],
        "CTG": ["CTG", "VietinBank", "vietinbank", "Vietinbank"],
        "BID": ["BID", "BIDV", "bidv"],
        "GAS": ["GAS", "PV Gas", "PVGas"],
        "MSN": ["MSN", "Masan", "masan"],
        "PLX": ["PLX", "Petrolimex", "petrolimex"],
        "PNJ": ["PNJ", "Phú Nhuận", "pnj"],
        "REE": ["REE", "ree"],
        "SAB": ["SAB", "Sabeco", "sabeco", "Bia Sài Gòn"],
        "SHB": ["SHB", "shb"],
        "TPB": ["TPB", "TPBank", "tpbank"],
        "VIB": ["VIB", "vib"],
        "SSB": ["SSB", "SeABank", "seabank"],
        "POW": ["POW", "PV Power"],
        "BVH": ["BVH", "Bảo Việt", "bảo việt"],
        "GVR": ["GVR", "Cao su Việt Nam"],
        "VRE": ["VRE", "Vincom Retail"],
    }

    # Keywords chung cho thị trường chứng khoán
    MARKET_KEYWORDS = [
        "chứng khoán", "cổ phiếu", "VN-Index", "VNIndex", "VNINDEX", "VN30",
        "HOSE", "HNX", "sàn chứng", "thị trường chứng", "nhà đầu tư",
        "blue-chip", "bluechip", "cổ tức", "niêm yết", "ngân hàng",
        "bất động sản", "stock", "market", "lãi suất", "Fed",
    ]

    for ticker in tickers:
        ticker = ticker.upper().strip()
        # Lấy aliases cho ticker này
        aliases = COMPANY_ALIASES.get(ticker, [ticker])
        matched = []

        for article in news:
            search_text = f"{article.get('title', '')} {article.get('summary', '')}"
            # Tìm match ticker hoặc tên công ty
            found = any(alias in search_text for alias in aliases)
            if found and article not in matched:
                matched.append(article)

        # Nếu không tìm thấy tin riêng, lấy tin chung thị trường
        if not matched:
            for article in news:
                search_text = f"{article.get('title', '')} {article.get('summary', '')}"
                if any(kw in search_text for kw in MARKET_KEYWORDS):
                    matched.append(article)
                    if len(matched) >= 3:
                        break

        result[ticker] = matched[:limit]

    return result


def get_news_for_ai_prompt(tickers: list, limit_per_ticker: int = 3) -> str:
    """
    Tạo text block tin tức để inject vào AI prompt.
    Ưu tiên Google News (tìm chủ động), fallback RSS.
    Format phù hợp cho Gemini đọc.
    """
    if not tickers:
        return ""

    ticker_news = {}

    # Ưu tiên Google News cho từng ticker
    try:
        from core.google_news_engine import search_ticker_news
        for t in tickers:
            gnews = search_ticker_news(t, limit=limit_per_ticker)
            if gnews:
                ticker_news[t] = gnews
    except Exception as e:
        print(f"Google News for AI Prompt Error: {e}")

    # Fallback RSS cho ticker chưa có
    remaining = [t for t in tickers if t not in ticker_news]
    if remaining:
        rss_news = search_news_by_tickers(remaining, limit=limit_per_ticker)
        ticker_news.update(rss_news)

    if not any(ticker_news.values()):
        return ""

    lines = []
    seen_titles = set()  # Tránh trùng lặp
    
    for ticker, articles in ticker_news.items():
        if articles:
            lines.append(f"  [{ticker}]:")
            for art in articles:
                title = art.get("title", "")
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                source = art.get("source", "")
                pub = art.get("pubDate", art.get("publishDate", ""))[:10]  # Chỉ lấy ngày
                summary = art.get("summary", "")[:150]
                lines.append(f"    - [{pub}] ({source}) {title}")
                if summary:
                    lines.append(f"      Tóm tắt: {summary}")

    if not lines:
        return ""

    return "\n".join(lines)
