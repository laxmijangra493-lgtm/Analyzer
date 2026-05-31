# pages/dashboard.py
# python3 -m streamlit run app.py  →  navigate to dashboard

import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import requests
import feedparser
import hashlib
import re
import time
import os
from datetime import datetime, timezone, timedelta
from dateutil import parser as dateparser
from urllib.parse import quote

st.set_page_config(page_title="Analyzr · Dashboard", page_icon="📈", layout="wide")

# ── Auth guard ────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

name = st.session_state.get("name", "User")
uid  = st.session_state.get("id", "—")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

.logo-container { display:flex; align-items:center; gap:16px; padding:10px 0 6px; }
.logo-icon {
    width:48px; height:48px;
    background: linear-gradient(135deg,#22d3ee,#6366f1,#a855f7);
    clip-path: polygon(10% 90%,40% 10%,55% 40%,75% 25%,90% 10%,90% 90%);
}
.logo-text { font-size:32px; font-weight:700; color:#e5e7eb; }
.logo-text span {
    background: linear-gradient(135deg,#22d3ee,#6366f1,#a855f7);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.tagline {
    font-size:10px; letter-spacing:3px; margin-top:-4px;
    background: linear-gradient(90deg,#22d3ee,#6366f1,#a855f7);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.user-badge {
    text-align:right; padding:10px 14px; border-radius:12px;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
}
.feature-card {
    background: rgba(15,23,42,0.8); border: 1px solid rgba(99,102,241,0.2);
    border-radius: 14px; padding: 18px 20px; height: 100%; transition: border-color 0.2s;
}
.feature-card:hover { border-color: rgba(99,102,241,0.5); }
div[data-testid="metric-container"] {
    background: rgba(15,23,42,0.7); border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px; padding: 14px 18px;
}
div[data-testid="stButton"] > button {
    border-radius: 10px !important; font-weight: 600 !important; transition: all 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: #6366f1 !important; box-shadow: 0 0 14px rgba(99,102,241,0.4) !important;
}
div[data-testid="stSelectbox"] > div { border-radius: 10px !important; }
div[data-testid="stTextInput"] input { border-radius: 10px !important; }
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── News styles ─────────────────────────────────────── */
.news-section-title {
    font-size:16px; font-weight:700; color:#e2e8f0;
    margin:0 0 12px; display:flex; align-items:center; gap:8px;
}
.news-card {
    background: rgba(15,23,42,0.75);
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 14px; padding: 14px 16px; margin-bottom: 10px;
    transition: border-color 0.2s, box-shadow 0.2s;
    display: flex; gap: 14px; align-items: flex-start;
}
.news-card:hover {
    border-color: rgba(99,102,241,0.45);
    box-shadow: 0 4px 24px rgba(99,102,241,0.12);
}
.news-card.alert   { border-color:rgba(234,179,8,0.4);  background:rgba(234,179,8,0.06); }
.news-card.bullish { border-color:rgba(34,197,94,0.3);  background:rgba(34,197,94,0.05); }
.news-card.bearish { border-color:rgba(239,68,68,0.3);  background:rgba(239,68,68,0.05); }
.news-thumb {
    width:72px; height:58px; border-radius:8px;
    object-fit:cover; flex-shrink:0;
}
.news-thumb-placeholder {
    width:72px; height:58px; border-radius:8px; flex-shrink:0;
    background:linear-gradient(135deg,rgba(99,102,241,0.25),rgba(168,85,247,0.25));
    display:flex; align-items:center; justify-content:center; font-size:22px;
}
.news-body { flex:1; min-width:0; }
.news-title-text {
    font-size:13px; font-weight:600; color:#e2e8f0;
    margin:0 0 5px; line-height:1.45;
    display:-webkit-box; -webkit-line-clamp:2;
    -webkit-box-orient:vertical; overflow:hidden;
}
.news-meta {
    display:flex; gap:10px; align-items:center;
    font-size:11px; color:#64748b; flex-wrap:wrap;
}
.news-source { font-weight:600; color:#94a3b8; }
.news-time   { color:#475569; }
.badge { display:inline-block; padding:2px 8px; border-radius:20px; font-size:10px; font-weight:700; letter-spacing:0.5px; }
.badge-alert   { background:rgba(234,179,8,0.2);  color:#fbbf24; }
.badge-bullish { background:rgba(34,197,94,0.2);  color:#22c55e; }
.badge-bearish { background:rgba(239,68,68,0.2);  color:#f87171; }
.badge-neutral { background:rgba(100,116,139,0.2);color:#94a3b8; }
.badge-latest  { background:rgba(100,116,139,0.2);color:#94a3b8; }
.sym-chip {
    display:inline-block; background:rgba(99,102,241,0.2);
    color:#818cf8; font-size:10px; font-weight:700;
    padding:1px 6px; border-radius:4px; margin-right:3px;
}
.score-badge {
    background:rgba(15,23,42,0.9); border:1px solid rgba(99,102,241,0.3);
    border-radius:6px; padding:2px 7px; font-size:10px;
    font-weight:700; color:#a5b4fc; min-width:28px; text-align:center;
}
.news-feed-empty { text-align:center; padding:28px 0; color:#475569; font-size:13px; }
.refresh-info    { font-size:11px; color:#475569; text-align:right; margin-bottom:8px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  NEWS ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

_BULLISH_KW = [
    "surge","rally","beat","record","profit","gain","growth","strong","bullish",
    "upgrade","outperform","positive","revenue","boost","soar","rise","jump",
    "recover","optimism","expansion","dividend","buyback","breakout","high",
]
_BEARISH_KW = [
    "crash","plunge","fall","loss","miss","decline","weak","bearish","downgrade",
    "underperform","negative","layoff","debt","risk","recession","drop","slip",
    "warning","concern","fraud","lawsuit","fine","penalty","default","sell-off",
]
_HIGH_IMPACT_KW = [
    "fed","rbi","sebi","earnings","gdp","inflation","interest rate","cpi","merger",
    "acquisition","ipo","bankruptcy","sec","war","crisis","rate cut","rate hike",
    "quantitative","stimulus","tariff","sanction","central bank","fomc","policy",
]
_FINANCIAL_KW = [
    "stock","market","share","equity","bond","etf","fund","invest","trade","nasdaq",
    "nyse","nse","bse","sensex","nifty","dow","s&p","index","portfolio","dividend",
    "earnings","revenue","profit","loss","ipo","analyst","upgrade","downgrade",
    "quarter","annual","fiscal","financial","economy","economic","bank","fed","rbi",
]
_SOURCE_QUALITY: dict = {
    "reuters":90,"bloomberg":88,"wsj":86,"ft":85,"financial times":85,
    "cnbc":80,"marketwatch":76,"economist":82,"barrons":78,
    "seeking alpha":70,"seekingalpha":70,"yahoo":65,"google":60,
    "finnhub":70,"marketaux":72,"mint":68,"economic times":72,
    "business standard":70,"moneycontrol":68,"livemint":68,
    "ndtv profit":65,"default":50,
}
_LOGO_MAP: dict = {
    "AAPL":"🍎","MSFT":"🪟","GOOGL":"🔍","AMZN":"📦","META":"👥",
    "TSLA":"⚡","NVDA":"💚","NFLX":"🎬","AMD":"🔴","INTC":"🔵",
    "RELIANCE":"🛢️","TCS":"💻","INFY":"🔷","HDFC":"🏦","WIPRO":"🟠",
}


def _source_quality(source: str) -> int:
    s = source.lower()
    for k, v in _SOURCE_QUALITY.items():
        if k in s: return v
    return _SOURCE_QUALITY["default"]


def _impact_score(title: str, desc: str, source: str) -> int:
    text  = (title + " " + desc).lower()
    score = _source_quality(source)
    score += min(25, sum(5 for kw in _HIGH_IMPACT_KW if kw in text))
    score += min(15, sum(2 for kw in _BULLISH_KW + _BEARISH_KW if kw in text))
    score += min(10, len(text) // 80)
    return min(100, max(0, score))


def _sentiment(title: str, desc: str) -> str:
    text = (title + " " + desc).lower()
    b = sum(1 for k in _BULLISH_KW if k in text)
    r = sum(1 for k in _BEARISH_KW if k in text)
    if b > r + 1: return "bullish"
    if r > b + 1: return "bearish"
    return "neutral"


def _is_financial(title: str, desc: str) -> bool:
    text = (title + " " + desc).lower()
    return sum(1 for k in _FINANCIAL_KW if k in text) >= 2


def _extract_symbols(text: str) -> list:
    raw = re.findall(r'\$([A-Z]{1,5})|(?<![a-z])([A-Z]{2,5})(?![a-z])', text)
    candidates = [a or b for a, b in raw]
    ignore = {"THE","AND","FOR","ARE","BUT","NOT","YOU","ALL","CAN","HER","WAS",
               "ONE","OUR","OUT","DAY","GET","HAS","HIM","HIS","HOW","MAN","NEW",
               "NOW","OLD","SEE","TWO","WAY","WHO","BOY","DID","ITS","LET","PUT",
               "SAY","SHE","TOO","USE","US","IT","OR","IN","AS","AT","BY","AN","UP",
               "AI","US","UK","EU","CEO","IPO","GDP","CPI","ETF","RSI","NSE","BSE"}
    return list({s for s in candidates if s not in ignore and len(s) >= 2})[:5]


def _deduplicate(articles: list) -> list:
    seen: set = set()
    out: list = []
    for a in articles:
        key = hashlib.md5(a["title"].lower().strip()[:80].encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            out.append(a)
    return out


def _parse_time(raw) -> datetime:
    if not raw:
        return datetime.now(timezone.utc)
    try:
        if isinstance(raw, (int, float)):
            return datetime.fromtimestamp(raw, tz=timezone.utc)
        dt = dateparser.parse(str(raw))
        if dt and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt or datetime.now(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def _rel_time(dt: datetime) -> str:
    now = datetime.now(timezone.utc)
    try:
        delta = now - dt.astimezone(timezone.utc)
    except Exception:
        return "recently"
    s = int(delta.total_seconds())
    if s < 60:    return "just now"
    if s < 3600:  return f"{s//60}m ago"
    if s < 86400: return f"{s//3600}h ago"
    return f"{s//86400}d ago"


def _categorize(score: int, sentiment: str) -> str:
    if score >= 78:             return "alert"
    if sentiment == "bullish":  return "bullish"
    if sentiment == "bearish":  return "bearish"
    return "latest"


def _normalize(title, url, source, published=None, description="", image=None, symbols=None) -> dict:
    if not title or len(title.strip()) < 5:
        return {}
    dt   = _parse_time(published)
    desc = re.sub(r"<[^>]+>", "", description).strip()[:300]
    syms = symbols or _extract_symbols(title + " " + desc)
    score = _impact_score(title, desc, source)
    sent  = _sentiment(title, desc)
    return {
        "title":       title.strip(),
        "url":         url or "#",
        "source":      source,
        "published":   dt,
        "rel_time":    _rel_time(dt),
        "description": desc,
        "image":       image,
        "symbols":     syms,
        "impact":      score,
        "sentiment":   sent,
        "category":    _categorize(score, sent),
    }


# ── Source 1: MarketAux ───────────────────────────────────────────────────────
def _fetch_marketaux(api_key: str, symbol=None, limit: int = 20) -> list:
    """
    Primary source. User key goes in .streamlit/secrets.toml as MARKETAUX_KEY.
    Free tier: 100 req/day. https://www.marketaux.com/
    """
    if not api_key:
        return []
    try:
        params: dict = {
            "api_token":       api_key,
            "language":        "en",
            "limit":           limit,
            "filter_entities": "true",
        }
        if symbol:
            clean = symbol.split(".")[0].replace("^", "")
            params["symbols"] = clean
        r = requests.get(
            "https://api.marketaux.com/v1/news/all",
            params=params, timeout=8,
            headers={"Accept": "application/json"},
        )
        if r.status_code != 200:
            return []
        results = []
        for item in r.json().get("data", []):
            ents = item.get("entities", [])
            syms = [e.get("symbol","") for e in ents if e.get("symbol")]
            n = _normalize(
                title=item.get("title",""),
                url=item.get("url","#"),
                source=item.get("source","MarketAux"),
                published=item.get("published_at"),
                description=item.get("description",""),
                image=item.get("image_url"),
                symbols=syms,
            )
            if n: results.append(n)
        return results
    except Exception:
        return []


# ── Source 2: Finnhub ─────────────────────────────────────────────────────────
def _fetch_finnhub(api_key: str, symbol=None) -> list:
    """
    Secondary source. User key in secrets.toml as FINNHUB_KEY.
    Free tier: 60 calls/min. https://finnhub.io/
    """
    if not api_key:
        return []
    try:
        headers = {"X-Finnhub-Token": api_key, "Accept": "application/json"}
        if symbol and not symbol.startswith("^"):
            clean   = symbol.split(".")[0]
            to_dt   = datetime.now().strftime("%Y-%m-%d")
            from_dt = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            r = requests.get(
                "https://finnhub.io/api/v1/company-news",
                params={"symbol": clean, "from": from_dt, "to": to_dt},
                headers=headers, timeout=8,
            )
        else:
            r = requests.get(
                "https://finnhub.io/api/v1/news",
                params={"category": "general"},
                headers=headers, timeout=8,
            )
        if r.status_code != 200:
            return []
        items = r.json()
        if not isinstance(items, list):
            return []
        results = []
        for item in items[:25]:
            syms = [item["related"]] if item.get("related") else []
            n = _normalize(
                title=item.get("headline",""),
                url=item.get("url","#"),
                source=item.get("source","Finnhub"),
                published=item.get("datetime"),
                description=item.get("summary",""),
                image=item.get("image"),
                symbols=syms,
            )
            if n: results.append(n)
        return results
    except Exception:
        return []


# ── Source 3: Google News RSS (free fallback, no key) ─────────────────────────
def _fetch_google_rss(query: str = "stock market finance", limit: int = 35) -> list:
    rss_urls = [
        f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pKVGlnQVAB?hl=en-US&gl=US&ceid=US:en",
    ]
    results = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit]:
                raw_title = entry.get("title","")
                source    = "Google News"
                if isinstance(raw_title, str) and " - " in raw_title:
                    parts     = raw_title.rsplit(" - ", 1)
                    raw_title = parts[0].strip()
                    source    = parts[1].strip()
                # Try media image
                img = None
                for tag in ["media_content","media_thumbnail","enclosures"]:
                    val = entry.get(tag)
                    if isinstance(val, list) and val:
                        img = val[0].get("url"); break
                    elif isinstance(val, dict):
                        img = val.get("url"); break
                raw_desc = entry.get("summary", "")
                if isinstance(raw_desc, list):
                    raw_desc = str(raw_desc[0]) if raw_desc else ""
                elif isinstance(raw_desc, dict):
                    raw_desc = str(raw_desc.get("value", ""))
                elif raw_desc is None:
                    raw_desc = ""
                else:
                    raw_desc = str(raw_desc)
                n = _normalize(
                    title=raw_title,
                    url=entry.get("link","#"),
                    source=source,
                    published=entry.get("published"),
                    description=raw_desc,
                    image=img,
                )
                if n: results.append(n)
            if results: break  # first successful RSS is enough
        except Exception:
            continue
    return results


# ── Source 4: yfinance news (symbol-specific last resort) ─────────────────────
def _fetch_yfinance_news(symbol: str) -> list:
    try:
        items = yf.Ticker(symbol).get_news(count=15)
        if not items:
            return []
        results = []
        for item in items:
            content = item.get("content", {})
            if not isinstance(content, dict):
                content = {}
            title   = content.get("title") or item.get("title","")
            url     = (content.get("canonicalUrl",{}) or {}).get("url","#") or item.get("link","#")
            pub     = content.get("pubDate") or item.get("providerPublishTime","")
            provider= content.get("provider",{}) or {}
            source  = (provider.get("displayName") if isinstance(provider,dict) else None) or "Yahoo Finance"
            thumb   = content.get("thumbnail",{}) or {}
            img     = None
            resols  = thumb.get("resolutions",[]) if isinstance(thumb,dict) else []
            if resols and isinstance(resols[0],dict):
                img = resols[0].get("url")
            desc = content.get("summary","") or item.get("summary","")
            n = _normalize(
                title=title, url=url, source=source,
                published=pub, description=desc, image=img,
                symbols=[symbol.split(".")[0]],
            )
            if n: results.append(n)
        return results
    except Exception:
        return []


# ── Master pipeline ───────────────────────────────────────────────────────────
def _get_api_key(name: str) -> str:
    try:
        val = st.secrets.get(name, "")
        return val if val else ""
    except Exception:
        pass
    return os.environ.get(name, "")


@st.cache_data(ttl=60, show_spinner=False)
def fetch_news(symbol=None) -> list:
    """
    Merge → deduplicate → filter → score → sort.
    TTL=60s → auto-refreshes every minute.
    """
    marketaux_key = _get_api_key("enter your api key")
    finnhub_key   = _get_api_key("enter your api key")
    rss_query     = (f"{symbol.split('.')[0].replace('^','')} stock finance" if symbol
                     else "stock market finance economy India NSE BSE")

    all_articles: list = []
    all_articles += _fetch_marketaux(marketaux_key, symbol)
    all_articles += _fetch_finnhub(finnhub_key, symbol)
    all_articles += _fetch_google_rss(rss_query)
    if symbol and len(all_articles) < 8:
        all_articles += _fetch_yfinance_news(symbol)

    articles = _deduplicate(all_articles)
    if not symbol:
        articles = [a for a in articles if _is_financial(a["title"], a["description"])]
    articles = [a for a in articles if len(a.get("title","")) > 10]
    articles.sort(key=lambda x: (x["impact"], x["published"].timestamp()), reverse=True)
    return articles[:60]


def categorize_news(articles: list) -> dict:
    return {
        "alert":   [a for a in articles if a["category"] == "alert"][:8],
        "bullish": [a for a in articles if a["category"] == "bullish"][:12],
        "bearish": [a for a in articles if a["category"] == "bearish"][:12],
        "latest":  articles[:20],
    }


# ── Image helper ──────────────────────────────────────────────────────────────
def _img_html(article: dict) -> str:
    img  = article.get("image")
    syms = article.get("symbols", [])
    if img:
        return f'<img class="news-thumb" src="{img}" onerror="this.style.display=\'none\'" loading="lazy">'
    emoji = "📰"
    for s in syms:
        if s.upper() in _LOGO_MAP:
            emoji = _LOGO_MAP[s.upper()]
            break
    return f'<div class="news-thumb-placeholder">{emoji}</div>'


def _news_card_html(a: dict) -> str:
    cat   = a["category"]
    score = a["impact"]
    syms  = a.get("symbols", [])
    badge_lbl  = {"alert":"🔔 Alert","bullish":"📈 Bullish","bearish":"📉 Bearish","latest":"📰 News"}.get(cat,"📰 News")
    bar_color  = "#fbbf24" if cat=="alert" else ("#22c55e" if a["sentiment"]=="bullish" else ("#f87171" if a["sentiment"]=="bearish" else "#6366f1"))
    sym_chips  = "".join(f'<span class="sym-chip">{s}</span>' for s in syms[:3])
    card_cls   = cat if cat in ("alert","bullish","bearish") else ""
    return f"""
<a href="{a['url']}" target="_blank" style="text-decoration:none;">
<div class="news-card {card_cls}">
    {_img_html(a)}
    <div class="news-body">
        <div class="news-title-text">{a['title']}</div>
        <div class="news-meta">
            <span class="news-source">{a['source']}</span>
            <span class="news-time">{a['rel_time']}</span>
            <span class="badge badge-{cat}">{badge_lbl}</span>
            <span class="score-badge">{score}</span>
            {sym_chips}
        </div>
        <div style="margin-top:5px;display:flex;align-items:center;gap:4px;">
            <div style="height:3px;border-radius:2px;width:{score}%;background:{bar_color};max-width:120px;"></div>
            <span style="font-size:10px;color:#475569;">impact</span>
        </div>
    </div>
</div>
</a>"""


def _render_feed(articles: list, empty_msg: str = "No news found.") -> None:
    if not articles:
        st.markdown(f'<div class="news-feed-empty">{empty_msg}</div>', unsafe_allow_html=True)
        return
    for a in articles:
        st.markdown(_news_card_html(a), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  STOCK HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)
def load_stock_data(symbol: str, period: str, interval: str) -> pd.DataFrame:
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    return df.tail(1000) if not df.empty else df


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta    = close.diff()
    avg_gain = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    avg_loss = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs       = avg_gain / avg_loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))


INTERVAL_MAP = {
    "1d":  "5m",
    "5d":  "15m",
    "1mo": "30m",
    "6mo": "1h",
    "1y":  "1d",
    "5y":  "1wk",
}


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════

def show_logo():
    st.markdown("""
    <div class="logo-container">
        <div class="logo-icon"></div>
        <div>
            <div class="logo-text">Analy<span>zr</span></div>
            <div class="tagline">INSIGHTS • ANALYSIS • GROWTH</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
hcol1, hcol2 = st.columns([8, 2])
with hcol1:
    show_logo()
with hcol2:
    st.markdown(f"""
    <div class="user-badge">
        <div style="font-size:13px;">👤 <b>{name}</b></div>
        <div style="font-size:11px;color:gray;">ID: {uid}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Action bar ────────────────────────────────────────────────────────────────
st.markdown("")
a1, a2, a3, a4, a5 = st.columns([3, 2, 2, 2, 2])
with a2:
    if st.button("📈 NIFTY 50", use_container_width=True):
        st.session_state["stock_symbol"] = "^NSEI"
with a3:
    if st.button("👁 Watchlist", use_container_width=True):
        st.switch_page("pages/watchlist.py")
with a4:
    if st.button("💹 Paper Trade", use_container_width=True):
        st.switch_page("pages/trading.py")
with a5:
    if st.button("🚪 Logout", use_container_width=True):
        for k in ["logged_in", "id", "name", "stock_symbol"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")

st.divider()

# ── Feature cards ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="feature-card">
        <h4>📈 Real-Time Charts</h4>
        <p style="color:#94a3b8;font-size:13px;">Track stock movements with live market data and candlestick indicators.</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="feature-card">
        <h4>🧠 AI Insights</h4>
        <p style="color:#94a3b8;font-size:13px;">Smart signals using RSI, Moving Averages and trend detection.</p>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="feature-card">
        <h4>⚡ Fast Analysis</h4>
        <p style="color:#94a3b8;font-size:13px;">Analyze multiple stocks instantly with optimized cached data fetching.</p>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── Search bar ────────────────────────────────────────────────────────────────
st.markdown("### 🔍 Search Stocks")
sc1, sc2, sc3 = st.columns([5, 2, 1])
with sc1:
    stock_input = st.text_input(
        "Symbol", label_visibility="collapsed",
        placeholder="e.g. RELIANCE.NS · TCS.NS · INFY.NS · ^NSEI"
    )
with sc2:
    timeframe = st.selectbox("Timeframe", INTERVAL_MAP.keys(), label_visibility="collapsed")
with sc3:
    search_btn = st.button("Search 🔎", use_container_width=True)

if "stock_symbol" not in st.session_state:
    st.session_state["stock_symbol"] = "^NSEI"

if search_btn and stock_input:
    st.session_state["stock_symbol"] = stock_input.strip().upper()
    fetch_news.clear()

# ── Chart ─────────────────────────────────────────────────────────────────────
symbol   = st.session_state["stock_symbol"]
interval = INTERVAL_MAP[timeframe]

st.markdown(f"#### {symbol} &nbsp;·&nbsp; {timeframe} chart")

with st.spinner(f"Loading {symbol}…"):
    try:
        df = load_stock_data(symbol, timeframe, interval)
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        df = pd.DataFrame()

if df.empty:
    st.warning("⚠️ No data found. Check the symbol and try again.")
else:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        increasing_line_color="#22c55e",
        decreasing_line_color="#ef4444",
        name=symbol,
    ))
    fig.update_layout(
        template="plotly_dark",
        title=dict(text=f"{symbol} — {timeframe}", font=dict(size=15)),
        xaxis_title="Time", yaxis_title="Price (₹)",
        xaxis_rangeslider_visible=False,
        hovermode="x unified", height=480,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(
        showspikes=True, spikemode="across", spikesnap="cursor",
        spikethickness=0.5, spikedash="dot",
        rangebreaks=[
            dict(bounds=["sat","mon"]),
            dict(bounds=[15.5, 9.25], pattern="hour"),
        ],
    )
    fig.update_yaxes(showspikes=True, spikemode="across", spikesnap="cursor",
                     spikethickness=0.5, spikedash="dot")
    st.plotly_chart(fig, use_container_width=True)

    # ── Metrics ───────────────────────────────────────────────────────────────
    try:
        info = yf.Ticker(symbol).info
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("P/E Ratio",  info.get("trailingPE",  "N/A"))
        with m2: st.metric("EPS",        info.get("trailingEps", "N/A"))
        with m3:
            mc     = info.get("marketCap")
            mc_str = f"₹{mc/1e7:.1f} Cr" if isinstance(mc, (int,float)) else "N/A"
            st.metric("Market Cap", mc_str)
        with m4: st.metric("52W High", info.get("fiftyTwoWeekHigh","N/A"))
    except Exception:
        pass

    st.divider()

    # ── RSI ───────────────────────────────────────────────────────────────────
    df["RSI"] = calculate_rsi(df["Close"])
    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"], mode="lines", name="RSI",
        line=dict(color="#22d3ee", width=2)
    ))
    rsi_fig.add_hrect(y0=70, y1=100, fillcolor="red",   opacity=0.08, line_width=0)
    rsi_fig.add_hrect(y0=0,  y1=30,  fillcolor="green", opacity=0.08, line_width=0)
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="rgba(239,68,68,0.6)")
    rsi_fig.add_hline(y=50, line_dash="dot",  line_color="rgba(148,163,184,0.4)")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="rgba(34,197,94,0.6)")
    rsi_fig.update_layout(
        title=dict(text=f"{symbol} — RSI (14)", font=dict(size=13)),
        template="plotly_dark", height=230,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, 100]),
    )
    st.plotly_chart(rsi_fig, use_container_width=True)

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
#  NEWS SECTION
# ═══════════════════════════════════════════════════════════════════════════════

news_h1, news_h2, news_h3 = st.columns([5, 2, 1])
with news_h1:
    st.markdown("### 📰 Market News Intelligence")
with news_h2:
    filter_sym = st.checkbox(
        f"Filter by {symbol}", value=False,
        key="news_filter_sym",
        help=f"Show only news related to {symbol}",
    )
with news_h3:
    if st.button("🔄 Refresh", use_container_width=True, key="news_refresh"):
        fetch_news.clear()
        st.rerun()

# API key hint
marketaux_configured = bool(_get_api_key("MARKETAUX_KEY"))
finnhub_configured   = bool(_get_api_key("FINNHUB_KEY"))
missing = []
if not marketaux_configured: missing.append("`MARKETAUX_KEY`")
if not finnhub_configured:   missing.append("`FINNHUB_KEY`")
if missing:
    st.info(
        f"💡 Add {' and '.join(missing)} to `.streamlit/secrets.toml` for premium sources. "
        "Google News RSS is active as a free fallback.",
        icon="🔑",
    )

# Fetch
news_symbol = symbol if filter_sym else None
with st.spinner("Fetching market news…"):
    articles = fetch_news(news_symbol)

feeds = categorize_news(articles)

# Status bar
sources_used = list({a["source"].split()[0] for a in articles})[:8]
src_str = " · ".join(sources_used) if sources_used else "None yet"
st.markdown(
    f'<div class="refresh-info">🔄 Auto-refresh every 60s &nbsp;|&nbsp; '
    f'<b>{len(articles)}</b> articles &nbsp;|&nbsp; Sources: {src_str} &nbsp;|&nbsp; '
    f'Updated: {datetime.now().strftime("%H:%M:%S")}</div>',
    unsafe_allow_html=True,
)

# Tabs
tab_alert, tab_bull, tab_bear, tab_latest = st.tabs([
    f"🔔 Top Alerts ({len(feeds['alert'])})",
    f"📈 Bullish ({len(feeds['bullish'])})",
    f"📉 Bearish ({len(feeds['bearish'])})",
    f"📰 Latest ({len(feeds['latest'])})",
])

with tab_alert:
    st.markdown('<div class="news-section-title">🔔 High-Impact Alerts <span style="font-size:11px;color:#475569;font-weight:400;">Impact score ≥ 78</span></div>', unsafe_allow_html=True)
    shown = feeds["alert"] or sorted(articles, key=lambda x: x["impact"], reverse=True)[:5]
    _render_feed(shown, "No high-impact alerts right now.")

with tab_bull:
    st.markdown('<div class="news-section-title">📈 Bullish Signals <span style="font-size:11px;color:#475569;font-weight:400;">Positive sentiment</span></div>', unsafe_allow_html=True)
    _render_feed(feeds["bullish"], "No bullish news detected.")

with tab_bear:
    st.markdown('<div class="news-section-title">📉 Bearish Signals <span style="font-size:11px;color:#475569;font-weight:400;">Negative sentiment</span></div>', unsafe_allow_html=True)
    _render_feed(feeds["bearish"], "No bearish news detected.")

with tab_latest:
    st.markdown('<div class="news-section-title">📰 Latest Feed <span style="font-size:11px;color:#475569;font-weight:400;">All articles · sorted by impact</span></div>', unsafe_allow_html=True)
    # Sub-filter
    lf1, lf2, lf3, lf4 = st.columns(4)
    if "latest_filter" not in st.session_state:
        st.session_state["latest_filter"] = "all"
    with lf1:
        if st.button("All",        key="lf_all", use_container_width=True): st.session_state["latest_filter"] = "all"
    with lf2:
        if st.button("📈 Bullish", key="lf_b",   use_container_width=True): st.session_state["latest_filter"] = "bullish"
    with lf3:
        if st.button("📉 Bearish", key="lf_r",   use_container_width=True): st.session_state["latest_filter"] = "bearish"
    with lf4:
        if st.button("🔔 Alerts",  key="lf_a",   use_container_width=True): st.session_state["latest_filter"] = "alert"
    f = st.session_state["latest_filter"]
    shown = feeds["latest"] if f == "all" else [a for a in feeds["latest"] if a["category"] == f]
    _render_feed(shown, "No articles in this filter.")

st.markdown('<div style="text-align:center;padding:16px 0 4px;color:#334155;font-size:11px;">News refreshes automatically every 60 seconds · Click any article to open source</div>', unsafe_allow_html=True)

# ── Auto-rerun every 60 s ─────────────────────────────────────────────────────
if "last_news_refresh" not in st.session_state:
    st.session_state["last_news_refresh"] = time.time()
if time.time() - st.session_state["last_news_refresh"] >= 60:
    st.session_state["last_news_refresh"] = time.time()
    fetch_news.clear()
    st.rerun()