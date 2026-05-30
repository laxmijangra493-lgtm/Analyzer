# pages/watchlist.py

import streamlit as st
import yfinance as yf
import sqlite3
import sys
import os

# ── Import shared DB path from auth (single source of truth) ─────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import DB_NAME, init_db

st.set_page_config(
    page_title="Analyzr · Watchlist",
    page_icon="⭐",
    layout="wide"
)

# ── Ensure tables exist (safe to call repeatedly) ─────────────────────────────
init_db()

# ── Auth guard ────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

user_id = st.session_state.get("id")
name = st.session_state.get("name", "User")

if user_id is None:
    st.error("Session expired. Please login again.")
    st.switch_page("app.py")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.logo-container {
    display:flex;
    align-items:center;
    gap:16px;
    padding:10px 0 6px;
}

.logo-icon {
    width:48px;
    height:48px;
    background: linear-gradient(135deg,#22d3ee,#6366f1,#a855f7);
    clip-path: polygon(10% 90%,40% 10%,55% 40%,75% 25%,90% 10%,90% 90%);
}

.logo-text {
    font-size:32px;
    font-weight:700;
    color:#e5e7eb;
}

.logo-text span {
    background: linear-gradient(135deg,#22d3ee,#6366f1,#a855f7);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.tagline {
    font-size:10px;
    letter-spacing:3px;
    margin-top:-4px;
    background: linear-gradient(90deg,#22d3ee,#6366f1,#a855f7);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.wl-row {
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 12px;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.wl-row:hover {
    border-color: rgba(34,211,238,0.4);
    box-shadow: 0 0 16px rgba(34,211,238,0.1);
}

.sym {
    font-weight:700;
    font-size:15px;
    color:#e5e7eb;
    letter-spacing:0.5px;
}

.price {
    font-size:14px;
    color:#cbd5e1;
}

.up {
    color:#22c55e;
    font-weight:600;
}

.down {
    color:#ef4444;
    font-weight:600;
}

.neutral {
    color:#94a3b8;
    font-weight:600;
}

div[data-testid="stButton"] > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}

.section-header {
    font-size: 22px;
    font-weight: 700;
    color: #e5e7eb;
    margin: 12px 0 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}
</style>
""", unsafe_allow_html=True)


# ── DB helpers ────────────────────────────────────────────────────────────────
def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def add_stock(uid: int, symbol: str) -> bool:
    """Returns True if added, False if already exists."""
    try:
        with _conn() as conn:
            exists = conn.execute(
                "SELECT 1 FROM watchlist WHERE user_id=? AND symbol=?",
                (uid, symbol)
            ).fetchone()

            if not exists:
                conn.execute(
                    "INSERT INTO watchlist (user_id, symbol) VALUES (?, ?)",
                    (uid, symbol)
                )
                conn.commit()
                return True
        return False
    except sqlite3.Error:
        return False


def get_watchlist(uid: int) -> list:
    try:
        with _conn() as conn:
            rows = conn.execute(
                "SELECT symbol FROM watchlist WHERE user_id=? ORDER BY symbol",
                (uid,)
            ).fetchall()
        return [r["symbol"] for r in rows]
    except sqlite3.Error:
        return []


def remove_stock(uid: int, symbol: str):
    try:
        with _conn() as conn:
            conn.execute(
                "DELETE FROM watchlist WHERE user_id=? AND symbol=?",
                (uid, symbol)
            )
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


# ── Logo / header ─────────────────────────────────────────────────────────────
hcol1, hcol2 = st.columns([8, 2])

with hcol1:
    st.markdown("""
    <div class="logo-container">
        <div class="logo-icon"></div>
        <div>
            <div class="logo-text">Analy<span>zr</span></div>
            <div class="tagline">INSIGHTS • ANALYSIS • GROWTH</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with hcol2:
    st.markdown(f"""
    <div style="
        text-align:right;
        padding:10px 14px;
        border-radius:12px;
        background:rgba(255,255,255,0.03);
        border:1px solid rgba(255,255,255,0.08);
    ">
        <div style="font-size:13px;">👤 <b>{name}</b></div>
    </div>
    """, unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
n1, n2, n3 = st.columns([6, 2, 2])

with n2:
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")

with n3:
    if st.button("🚪 Logout", use_container_width=True):
        for k in ["logged_in", "id", "name", "stock_symbol"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")

st.divider()

# ── Add stock ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="section-header">⭐ My Watchlist</div>',
    unsafe_allow_html=True
)

add_col1, add_col2 = st.columns([5, 1])

with add_col1:
    new_stock = st.text_input(
        "Add Stock",
        label_visibility="collapsed",
        placeholder="Search / Add symbol e.g. RELIANCE.NS · TCS.NS · INFY.NS"
    )

with add_col2:
    if st.button("➕ Add", use_container_width=True):
        if new_stock.strip():
            sym = new_stock.strip().upper()
            if "." not in sym:
                sym += ".NS"

            if add_stock(user_id, sym):
                st.success(f"**{sym}** added to watchlist!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.info(f"**{sym}** is already in your watchlist.")
        else:
            st.warning("Please enter a stock symbol.")

st.markdown("")

# ── Watchlist ─────────────────────────────────────────────────────────────────
watchlist = get_watchlist(user_id)

if not watchlist:
    st.info("Your watchlist is empty. Add your first stock above! 📭")

else:
    h1, h2, h3, h4, h5, h6 = st.columns([3, 2, 2, 2, 2, 1])

    for col, label in zip(
        [h1, h2, h3, h4, h5, h6],
        ["Symbol", "Price (₹)", "Change", "% Change", "Actions", ""]
    ):
        col.markdown(
            f"<div style='color:#64748b;font-size:12px;font-weight:600;padding-bottom:4px;'>{label}</div>",
            unsafe_allow_html=True
        )

    st.markdown(
        "<hr style='margin:4px 0 12px;border-color:rgba(255,255,255,0.06);'>",
        unsafe_allow_html=True
    )

    for sym in watchlist:
        q = fetch_quote(sym)
        c_sym, c_price, c_chg, c_pct, c_chart, c_del = st.columns([3, 2, 2, 2, 2, 1])

        with c_sym:
            st.markdown(
                f"<div class='sym' style='padding-top:8px;'>{sym}</div>",
                unsafe_allow_html=True
            )

        if q:
            price  = q["price"]
            change = q["change"]
            pct    = q["pct"]
            color  = "up" if change >= 0 else "down"
            sign   = "+" if change >= 0 else ""

            with c_price:
                st.markdown(
                    f"<div class='price' style='padding-top:8px;'>₹{price:,.2f}</div>",
                    unsafe_allow_html=True
                )
            with c_chg:
                st.markdown(
                    f"<div class='{color}' style='padding-top:8px;'>{sign}{change:,.2f}</div>",
                    unsafe_allow_html=True
                )
            with c_pct:
                st.markdown(
                    f"<div class='{color}' style='padding-top:8px;'>{sign}{pct:.2f}%</div>",
                    unsafe_allow_html=True
                )
        else:
            for col in [c_price, c_chg, c_pct]:
                col.markdown(
                    "<div class='neutral' style='padding-top:8px;'>N/A</div>",
                    unsafe_allow_html=True
                )

        with c_chart:
            if st.button("📈 Chart", key=f"chart_{sym}", use_container_width=True):
                st.session_state["stock_symbol"] = sym
                st.switch_page("pages/dashboard.py")

        with c_del:
            if st.button("✕", key=f"del_{sym}", use_container_width=True, type="secondary"):
                remove_stock(user_id, sym)
                st.cache_data.clear()
                st.rerun()

        st.markdown(
            "<hr style='margin:4px 0;border-color:rgba(255,255,255,0.04);'>",
            unsafe_allow_html=True
        )

    st.markdown(f"""
    <div style="text-align:right;color:#475569;font-size:12px;margin-top:12px;">
        {len(watchlist)} stock{'s' if len(watchlist) != 1 else ''} · prices refresh every 60 s
    </div>
    """, unsafe_allow_html=True)