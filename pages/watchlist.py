# pages/watchlist.py

import streamlit as st
import yfinance as yf
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import DB_NAME, init_db

st.set_page_config(
    page_title="Analyzer · Watchlist",
    page_icon="📈",
    layout="wide"
)

init_db()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

user_id = st.session_state.get("id")
name    = st.session_state.get("name", "User")

if user_id is None:
    st.error("Session expired. Please login again.")
    st.switch_page("app.py")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #f8faf8 !important;
    color: #111827 !important;
}
#MainMenu, footer, header { visibility: hidden; }

.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Top bar ── */
.top-bar {
    display: flex;
    align-items: center;
    padding: 0 24px;
    height: 56px;
    background: #fff;
    border-bottom: 1px solid #e5e7eb;
    gap: 20px;
    position: sticky; top: 0; z-index: 100;
}
.tb-logo { font-size: 17px; font-weight: 800; color: #16a34a; letter-spacing: -0.3px; }
.tb-sub  { font-size: 11px; color: #9ca3af; font-weight: 500; margin-top: -1px; }
.tb-search {
    flex: 1; max-width: 300px;
    background: #f3f4f6; border: 1px solid #e5e7eb;
    border-radius: 8px; padding: 7px 14px; font-size: 13px;
    color: #374151; display: flex; align-items: center; gap: 8px;
}
.tb-nav { display: flex; gap: 4px; }
.tb-nav a {
    font-size: 13px; font-weight: 500; color: #374151;
    text-decoration: none; padding: 6px 12px; border-radius: 6px;
}
.tb-nav a.active { color: #16a34a; border-bottom: 2px solid #16a34a; border-radius: 0; }
.tb-right { margin-left: auto; display: flex; align-items: center; gap: 16px; }
.paper-bal {
    text-align: right;
    font-size: 15px; font-weight: 700; color: #16a34a;
    line-height: 1.2;
}
.paper-label { font-size: 10px; color: #6b7280; font-weight: 500; letter-spacing: 0.5px; }
.avatar {
    width: 34px; height: 34px; background: #e5e7eb;
    border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: 14px; font-weight: 700; color: #374151;
}

/* ── Layout ── */
.main-layout {
    display: flex; min-height: calc(100vh - 56px);
}

/* ── Sidebar ── */
.sidebar {
    width: 220px; flex-shrink: 0;
    background: #fff;
    border-right: 1px solid #e5e7eb;
    padding: 16px 0;
    display: flex; flex-direction: column;
}
.sidebar-brand { padding: 0 16px 20px; }
.sidebar-brand .logo { font-size: 17px; font-weight: 800; color: #16a34a; }
.sidebar-brand .sub  { font-size: 10px; color: #9ca3af; font-weight: 500; }
.nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 16px; font-size: 14px; font-weight: 500;
    color: #374151; text-decoration: none;
    border-radius: 0; transition: background 0.15s;
    cursor: pointer; border: none; background: none; width: 100%;
    text-align: left;
}
.nav-item:hover { background: #f3f4f6; }
.nav-item.active {
    background: #f0fdf4;
    color: #16a34a;
    border-right: 3px solid #16a34a;
    font-weight: 600;
}
.nav-icon { width: 18px; text-align: center; }
.sidebar-bottom { margin-top: auto; padding: 16px; }
.trade-btn {
    width: 100%; background: #16a34a; color: #fff;
    border: none; border-radius: 8px; padding: 11px;
    font-size: 14px; font-weight: 600; cursor: pointer;
    transition: background 0.2s;
}
.trade-btn:hover { background: #15803d; }
.sidebar-footer a {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 16px; font-size: 13px; color: #6b7280;
    text-decoration: none;
}

/* ── Content area ── */
.content-area {
    flex: 1; padding: 24px 28px; overflow-y: auto;
    background: #f8faf8;
}

/* ── Right panel ── */
.right-panel {
    width: 260px; flex-shrink: 0;
    background: #fff;
    border-left: 1px solid #e5e7eb;
    padding: 20px 16px;
    overflow-y: auto;
}

/* ── Watchlist table ── */
.wl-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 16px;
}
.wl-title { font-size: 18px; font-weight: 700; color: #111827; }
.badge-rt {
    background: #dcfce7; color: #16a34a;
    font-size: 10px; font-weight: 700;
    padding: 3px 8px; border-radius: 4px; letter-spacing: 0.5px;
}
.add-btn {
    border: 1.5px solid #d1d5db; background: #fff;
    border-radius: 6px; padding: 7px 14px;
    font-size: 13px; font-weight: 600; color: #374151;
    cursor: pointer; white-space: nowrap;
}

/* Table */
.tbl-head {
    display: grid;
    grid-template-columns: 2fr 2.5fr 1.5fr 1.5fr 1.5fr 1.5fr;
    padding: 8px 12px;
    font-size: 11px; font-weight: 700; color: #9ca3af;
    letter-spacing: 0.5px; text-transform: uppercase;
    border-bottom: 1px solid #f3f4f6;
}
.tbl-row {
    display: grid;
    grid-template-columns: 2fr 2.5fr 1.5fr 1.5fr 1.5fr 1.5fr;
    padding: 14px 12px;
    border-bottom: 1px solid #f9fafb;
    align-items: center;
    transition: background 0.12s;
}
.tbl-row:hover { background: #f9fafb; }
.ticker-badge {
    width: 34px; height: 34px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 800;
    color: #fff; flex-shrink: 0;
}
.ticker-cell { display: flex; align-items: center; gap: 8px; }
.ticker-sym  { font-size: 14px; font-weight: 700; color: #111827; }
.ticker-name { font-size: 11px; color: #9ca3af; margin-top: 1px; }
.price-cell  { font-size: 14px; font-weight: 700; color: #111827; }
.chg-pos { font-size: 13px; font-weight: 700; color: #16a34a; }
.chg-neg { font-size: 13px; font-weight: 700; color: #ef4444; }
.chg-neu { font-size: 13px; font-weight: 600; color: #9ca3af; }
.vol-cell { font-size: 12px; color: #6b7280; }
.sparkline { height: 28px; width: 80px; }

/* Market summary panel */
.ms-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 14px;
}
.ms-title { font-size: 13px; font-weight: 700; color: #111827; }
.ms-open  {
    font-size: 11px; font-weight: 600; color: #16a34a;
    display: flex; align-items: center; gap: 4px;
}
.ms-row {
    padding: 10px 0;
    border-bottom: 1px solid #f3f4f6;
}
.ms-name  { font-size: 12px; color: #374151; margin-bottom: 3px; }
.ms-val   { font-size: 14px; font-weight: 700; color: #111827; }
.ms-chg-pos { font-size: 11px; font-weight: 600; color: #16a34a; }
.ms-chg-neg { font-size: 11px; font-weight: 600; color: #ef4444; }

/* Sector grid */
.sector-title { font-size: 11px; font-weight: 700; color: #9ca3af; letter-spacing: 0.5px; text-transform: uppercase; margin: 16px 0 10px; }
.sector-grid  { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.sector-card  {
    padding: 10px 10px;
    border-radius: 8px;
    text-align: center;
}
.sector-card.pos { background: #f0fdf4; }
.sector-card.neg { background: #fff5f5; }
.sector-name { font-size: 9px; font-weight: 700; color: #9ca3af; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 4px; }
.sector-pct.pos { font-size: 14px; font-weight: 700; color: #16a34a; }
.sector-pct.neg { font-size: 14px; font-weight: 700; color: #ef4444; }

/* Earnings alert */
.alert-card {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 10px;
    padding: 14px 14px;
    margin-top: 16px;
}
.alert-title { font-size: 11px; font-weight: 700; color: #2563eb; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 6px; }
.alert-text  { font-size: 12px; color: #374151; line-height: 1.5; margin-bottom: 10px; }
.alert-btn   {
    width: 100%; background: #1d4ed8; color: #fff;
    border: none; border-radius: 6px; padding: 9px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
    cursor: pointer; text-transform: uppercase;
}

/* Streamlit button/input overrides */
div[data-testid="stButton"] > button {
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all 0.15s !important;
}
div[data-testid="stTextInput"] input {
    background: #fff !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 8px !important;
    color: #111827 !important;
    font-size: 13px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #16a34a !important;
    box-shadow: 0 0 0 3px rgba(22,163,74,0.1) !important;
}
div[data-testid="stAlert"] { border-radius: 8px !important; font-size: 13px !important; }
</style>
""", unsafe_allow_html=True)


# ── DB helpers ────────────────────────────────────────────────────────────────
def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def add_stock(uid: int, symbol: str) -> bool:
    try:
        with _conn() as conn:
            exists = conn.execute(
                "SELECT 1 FROM watchlist WHERE user_id=? AND symbol=?", (uid, symbol)
            ).fetchone()
            if not exists:
                conn.execute("INSERT INTO watchlist (user_id, symbol) VALUES (?, ?)", (uid, symbol))
                conn.commit()
                return True
        return False
    except sqlite3.Error:
        return False

def get_watchlist(uid: int) -> list:
    try:
        with _conn() as conn:
            rows = conn.execute(
                "SELECT symbol FROM watchlist WHERE user_id=? ORDER BY symbol", (uid,)
            ).fetchall()
        return [r["symbol"] for r in rows]
    except sqlite3.Error:
        return []

def remove_stock(uid: int, symbol: str):
    try:
        with _conn() as conn:
            conn.execute("DELETE FROM watchlist WHERE user_id=? AND symbol=?", (uid, symbol))
            conn.commit()
    except sqlite3.Error:
        pass

@st.cache_data(ttl=60, show_spinner=False)
def fetch_quote(symbol: str) -> dict:
    try:
        data = yf.Ticker(symbol).history(period="1d", interval="1m")
        if data.empty:
            return {}
        price      = data["Close"].iloc[-1]
        open_price = data["Open"].iloc[0]
        change     = price - open_price
        pct        = (change / open_price) * 100 if open_price else 0
        return {"price": price, "change": change, "pct": pct}
    except Exception:
        return {}


# Ticker badge colors
BADGE_COLORS = {
    "NV": "#22c55e", "TS": "#ef4444", "AP": "#22c55e",
    "AM": "#f59e0b", "ME": "#ef4444", "RE": "#6366f1",
    "TC": "#0ea5e9", "IN": "#8b5cf6",
}
def badge_color(sym: str) -> str:
    key = sym[:2].upper()
    return BADGE_COLORS.get(key, "#6b7280")

def ticker_abbr(sym: str) -> str:
    base = sym.split(".")[0]
    return base[:2].upper()

def sparkline_svg(positive: bool) -> str:
    if positive:
        return """<svg viewBox="0 0 80 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="0,22 15,18 28,20 42,12 55,9 68,6 80,4"
                stroke="#16a34a" stroke-width="1.8" fill="none"/>
        </svg>"""
    else:
        return """<svg viewBox="0 0 80 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="0,6 15,8 28,7 42,14 55,18 68,21 80,24"
                stroke="#ef4444" stroke-width="1.8" fill="none"/>
        </svg>"""


# ── TOP BAR ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="top-bar">
    <div>
        <div class="tb-logo">Analyzer</div>
        <div class="tb-sub">Terminal v1.0</div>
    </div>
    <div class="tb-search">🔍 &nbsp;Search Markets...</div>
    <div class="tb-nav">
        <a href="#" class="active" style="color:#16a34a;font-size:13px;font-weight:600;padding:6px 12px;border-bottom:2px solid #16a34a;">Markets</a>
        <a href="#" style="color:#374151;font-size:13px;font-weight:500;padding:6px 12px;text-decoration:none;">Indices</a>
        <a href="#" style="color:#374151;font-size:13px;font-weight:500;padding:6px 12px;text-decoration:none;">Sectors</a>
    </div>
    <div class="tb-right">
        <div>
            <div class="paper-bal">$100,000.00</div>
            <div class="paper-label">PAPER TRADING</div>
        </div>
        <div style="font-size:20px;">🔔</div>
        <div class="avatar">{name[0].upper()}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Three-column layout using Streamlit columns ───────────────────────────────
sidebar_col, main_col, right_col = st.columns([1, 4.5, 1.5], gap="small")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with sidebar_col:
    st.markdown("""
    <div style="background:#fff;border-right:1px solid #e5e7eb;min-height:calc(100vh - 56px);padding:20px 0;">
        <div style="padding:0 16px 20px;">
            <div style="font-size:17px;font-weight:800;color:#16a34a;">Analyzer</div>
            <div style="font-size:10px;color:#9ca3af;font-weight:500;">Terminal v1.0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .sb-item {
        display:flex;align-items:center;gap:10px;padding:9px 16px;
        font-size:13px;font-weight:500;color:#374151;
        border-radius:0;cursor:pointer;
    }
    .sb-item.active{background:#f0fdf4;color:#16a34a;border-right:3px solid #16a34a;font-weight:600;}
    .sb-item:hover{background:#f3f4f6;}
    </style>
    """, unsafe_allow_html=True)

    if st.button("📊  Watchlist", key="nav_wl", use_container_width=True):
        pass  # already here
    if st.button("📈  Market",    key="nav_mkt", use_container_width=True):
        st.switch_page("pages/dashboard.py")
    if st.button("💼  Portfolio", key="nav_port", use_container_width=True):
        st.switch_page("pages/trading.py")
    if st.button("📰  News",      key="nav_news", use_container_width=True):
        pass
    if st.button("⚙️  Settings",  key="nav_set",  use_container_width=True):
        pass

    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)

    if st.button("💹  Trade Now", key="trade_now", use_container_width=True):
        st.switch_page("pages/trading.py")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
        for k in ["logged_in", "id", "name", "stock_symbol"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────
with main_col:
    # Header row
    hdr1, hdr2 = st.columns([3, 1])
    with hdr1:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <span style="font-size:18px;font-weight:700;color:#111827;">Active Watchlist</span>
            <span style="background:#dcfce7;color:#16a34a;font-size:10px;font-weight:700;
                         padding:3px 8px;border-radius:4px;letter-spacing:0.5px;">REAL-TIME</span>
        </div>
        """, unsafe_allow_html=True)
    with hdr2:
        add_col1, add_col2 = st.columns([3, 1])
        with add_col1:
            new_stock = st.text_input("add", label_visibility="collapsed", placeholder="Add symbol…", key="wl_add")
        with add_col2:
            if st.button("＋ ADD", key="btn_add", use_container_width=True):
                if new_stock.strip():
                    sym = new_stock.strip().upper()
                    if "." not in sym and not sym.startswith("^"):
                        sym += ".NS"
                    if add_stock(int(user_id), sym):
                        st.success(f"{sym} added!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.info(f"{sym} already in watchlist.")

    # Table header
    st.markdown("""
    <div class="tbl-head">
        <span>TICKER</span>
        <span>NAME</span>
        <span>PRICE</span>
        <span>CHANGE</span>
        <span>VOLUME</span>
        <span>TREND (24H)</span>
    </div>
    """, unsafe_allow_html=True)

    watchlist = get_watchlist(int(user_id))

    if not watchlist:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;color:#9ca3af;">
            <div style="font-size:32px;margin-bottom:10px;">📭</div>
            <div style="font-size:14px;font-weight:600;">Your watchlist is empty</div>
            <div style="font-size:13px;margin-top:4px;">Add a ticker above to get started.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for sym in watchlist:
            q    = fetch_quote(sym)
            base = sym.split(".")[0]
            abbr = ticker_abbr(sym)
            bc   = badge_color(sym)

            price_str  = "N/A"
            chg_str    = "N/A"
            pct_str    = ""
            chg_class  = "chg-neu"
            vol_str    = "—"
            positive   = True

            if q:
                price_str = f"${q['price']:,.2f}"
                sign      = "+" if q["change"] >= 0 else ""
                chg_str   = f"{sign}${q['change']:,.2f}"
                pct_str   = f"{sign}{q['pct']:.2f}%"
                chg_class = "chg-pos" if q["change"] >= 0 else "chg-neg"
                positive  = q["change"] >= 0

            col_t, col_n, col_p, col_c, col_v, col_s, col_x = st.columns([1.2, 2.2, 1.4, 1.8, 1.3, 1.5, 0.5])

            with col_t:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;padding:6px 0;">
                    <div style="width:34px;height:34px;background:{bc};border-radius:8px;
                                display:flex;align-items:center;justify-content:center;
                                font-size:10px;font-weight:800;color:#fff;flex-shrink:0;">
                        {abbr}
                    </div>
                    <div>
                        <div style="font-size:13px;font-weight:700;color:#111827;">{base}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_n:
                st.markdown(f"<div style='padding-top:12px;font-size:13px;color:#374151;'>{sym}</div>",
                            unsafe_allow_html=True)
            with col_p:
                st.markdown(f"<div style='padding-top:12px;font-size:13px;font-weight:700;color:#111827;'>{price_str}</div>",
                            unsafe_allow_html=True)
            with col_c:
                st.markdown(f"<div class='{chg_class}' style='padding-top:10px;'>{chg_str}<br><span style='font-size:11px;'>{pct_str}</span></div>",
                            unsafe_allow_html=True)
            with col_v:
                st.markdown(f"<div style='padding-top:12px;font-size:12px;color:#6b7280;'>—</div>",
                            unsafe_allow_html=True)
            with col_s:
                st.markdown(f"<div style='padding-top:8px;'>{sparkline_svg(positive)}</div>",
                            unsafe_allow_html=True)
            with col_x:
                if st.button("✕", key=f"del_{sym}", use_container_width=True):
                    remove_stock(int(user_id), sym)
                    st.cache_data.clear()
                    st.rerun()

            st.markdown("<hr style='margin:0;border-color:#f3f4f6;'>", unsafe_allow_html=True)

# ── RIGHT PANEL ───────────────────────────────────────────────────────────────
with right_col:
    # Market Summary
    st.markdown("""
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px;margin-bottom:12px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
            <span style="font-size:13px;font-weight:700;color:#111827;">Market Summary</span>
            <span style="font-size:11px;font-weight:600;color:#16a34a;">● OPEN</span>
        </div>

        <div style="padding:8px 0;border-bottom:1px solid #f3f4f6;">
            <div style="font-size:12px;color:#374151;margin-bottom:2px;">S&P 500</div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;">
                <span style="font-size:14px;font-weight:700;color:#111827;">5,620.12</span>
                <span style="font-size:11px;font-weight:600;color:#16a34a;">+0.45%</span>
            </div>
        </div>
        <div style="padding:8px 0;border-bottom:1px solid #f3f4f6;">
            <div style="font-size:12px;color:#374151;margin-bottom:2px;">Nasdaq 100</div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;">
                <span style="font-size:14px;font-weight:700;color:#111827;">19,450.40</span>
                <span style="font-size:11px;font-weight:600;color:#16a34a;">+1.12%</span>
            </div>
        </div>
        <div style="padding:8px 0;">
            <div style="font-size:12px;color:#374151;margin-bottom:2px;">Dow 30</div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;">
                <span style="font-size:14px;font-weight:700;color:#111827;">41,390.50</span>
                <span style="font-size:11px;font-weight:600;color:#ef4444;">-0.08%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sector Performance
    st.markdown("""
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px;margin-bottom:12px;">
        <div style="font-size:11px;font-weight:700;color:#9ca3af;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:10px;">
            SECTOR PERFORMANCE
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
            <div style="background:#f0fdf4;border-radius:8px;padding:10px;text-align:center;">
                <div style="font-size:9px;font-weight:700;color:#9ca3af;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:4px;">TECHNOLOGY</div>
                <div style="font-size:14px;font-weight:700;color:#16a34a;">+2.84%</div>
            </div>
            <div style="background:#fff5f5;border-radius:8px;padding:10px;text-align:center;">
                <div style="font-size:9px;font-weight:700;color:#9ca3af;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:4px;">ENERGY</div>
                <div style="font-size:14px;font-weight:700;color:#ef4444;">-1.20%</div>
            </div>
            <div style="background:#f0fdf4;border-radius:8px;padding:10px;text-align:center;">
                <div style="font-size:9px;font-weight:700;color:#9ca3af;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:4px;">HEALTHCARE</div>
                <div style="font-size:14px;font-weight:700;color:#16a34a;">+0.12%</div>
            </div>
            <div style="background:#f0fdf4;border-radius:8px;padding:10px;text-align:center;">
                <div style="font-size:9px;font-weight:700;color:#9ca3af;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:4px;">FINANCIALS</div>
                <div style="font-size:14px;font-weight:700;color:#16a34a;">+0.85%</div>
            </div>
            <div style="background:#fff5f5;border-radius:8px;padding:10px;text-align:center;">
                <div style="font-size:9px;font-weight:700;color:#9ca3af;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:4px;">UTILITIES</div>
                <div style="font-size:14px;font-weight:700;color:#ef4444;">-0.44%</div>
            </div>
            <div style="background:#f0fdf4;border-radius:8px;padding:10px;text-align:center;">
                <div style="font-size:9px;font-weight:700;color:#9ca3af;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:4px;">CONSUMER</div>
                <div style="font-size:14px;font-weight:700;color:#16a34a;">+1.42%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Earnings Alert
    st.markdown("""
    <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:14px;">
        <div style="font-size:11px;font-weight:700;color:#2563eb;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:6px;">
            EARNINGS ALERT
        </div>
        <div style="font-size:12px;color:#374151;line-height:1.5;margin-bottom:10px;">
            NVDA reports in 4 days. Implied move ±8.2%.
        </div>
        <button style="width:100%;background:#1d4ed8;color:#fff;border:none;border-radius:6px;
                        padding:9px;font-size:11px;font-weight:700;letter-spacing:0.5px;
                        cursor:pointer;text-transform:uppercase;">
            SET REMINDER
        </button>
    </div>
    """, unsafe_allow_html=True)