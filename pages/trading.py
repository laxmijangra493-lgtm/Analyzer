# pages/trading.py

import streamlit as st
import yfinance as yf
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import (
    init_db, get_or_create_wallet, get_holdings,
    get_trades, execute_trade, reset_wallet, STARTING_BALANCE,
)

st.set_page_config(page_title="Analyzer · Portfolio", page_icon="💼", layout="wide")
init_db()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

user_id = st.session_state.get("id")
name    = st.session_state.get("name", "trader_pro")
if user_id is None:
    st.error("Session expired.")
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

.top-bar {
    display: flex; align-items: center;
    padding: 0 24px; height: 56px;
    background: #fff; border-bottom: 1px solid #e5e7eb;
    gap: 20px; position: sticky; top: 0; z-index: 100;
}
.tb-logo { font-size: 17px; font-weight: 800; color: #16a34a; }
.tb-sub  { font-size: 10px; color: #9ca3af; font-weight: 500; }
.tb-right { margin-left: auto; display: flex; align-items: center; gap: 16px; }
.paper-bal { font-size: 15px; font-weight: 700; color: #16a34a; line-height: 1.2; }
.paper-label { font-size: 10px; color: #6b7280; font-weight: 500; letter-spacing: 0.5px; }
.avatar {
    width: 34px; height: 34px; background: #e5e7eb;
    border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: 14px; font-weight: 700; color: #374151;
}

/* Summary cards */
.sum-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.sum-card {
    background: #fff; border: 1px solid #e5e7eb; border-radius: 10px;
    padding: 16px 18px;
}
.sum-label { font-size: 11px; font-weight: 500; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.sum-value { font-size: 22px; font-weight: 800; color: #111827; }
.sum-sub   { font-size: 12px; margin-top: 4px; }
.sum-pos   { color: #16a34a; }
.sum-neg   { color: #ef4444; }
.sum-blue  { color: #2563eb; }

/* Holdings table */
.table-card {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 10px; overflow: hidden; margin-bottom: 16px;
}
.table-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 20px; border-bottom: 1px solid #f3f4f6;
}
.table-title { font-size: 15px; font-weight: 700; color: #111827; }
.col-head {
    font-size: 11px; font-weight: 700; color: #9ca3af;
    letter-spacing: 0.5px; text-transform: uppercase;
}
.hold-row {
    display: grid;
    grid-template-columns: 2.5fr 1fr 1.5fr 2fr 2fr 2.5fr;
    padding: 14px 20px; align-items: center;
    border-bottom: 1px solid #f9fafb;
    transition: background 0.1s;
}
.hold-row:last-child { border-bottom: none; }
.hold-row:hover { background: #f9fafb; }
.ticker-badge {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.ticker-sym  { font-size: 14px; font-weight: 700; color: #111827; }
.ticker-name { font-size: 11px; color: #9ca3af; }
.price-pos   { font-size: 14px; font-weight: 700; color: #16a34a; }
.price-neg   { font-size: 14px; font-weight: 700; color: #ef4444; }
.price-neu   { font-size: 14px; font-weight: 600; color: #111827; }
.pnl-pos { font-size: 13px; font-weight: 700; color: #16a34a; }
.pnl-neg { font-size: 13px; font-weight: 700; color: #ef4444; }

/* Order / Activity cards */
.side-card {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 16px;
}
.side-title {
    font-size: 14px; font-weight: 700; color: #111827;
    margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between;
}
.order-row {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 10px 0; border-bottom: 1px solid #f3f4f6;
}
.order-row:last-child { border-bottom: none; }
.order-dot { width: 8px; height: 8px; border-radius: 50%; background: #16a34a; flex-shrink: 0; margin-top: 5px; }
.order-main { flex: 1; }
.order-sym  { font-size: 13px; font-weight: 700; color: #111827; }
.order-sub  { font-size: 11px; color: #9ca3af; margin-top: 2px; }
.cancel-btn {
    font-size: 11px; font-weight: 700; color: #ef4444;
    background: none; border: none; cursor: pointer; padding: 0;
}
.active-badge {
    background: #dcfce7; color: #16a34a;
    font-size: 10px; font-weight: 700;
    padding: 3px 8px; border-radius: 4px; letter-spacing: 0.5px;
}
.act-row {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 0; border-bottom: 1px solid #f3f4f6;
}
.act-row:last-child { border-bottom: none; }
.act-icon {
    width: 30px; height: 30px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;
}
.act-icon.green  { background: #dcfce7; }
.act-icon.blue   { background: #dbeafe; }
.act-icon.orange { background: #fef3c7; }
.act-main { flex: 1; }
.act-sym  { font-size: 13px; font-weight: 700; color: #111827; }
.act-sub  { font-size: 11px; color: #9ca3af; }
.act-val-pos { font-size: 13px; font-weight: 700; color: #16a34a; }
.act-val-neg { font-size: 13px; font-weight: 700; color: #ef4444; }

/* Trade form */
.trade-card {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 18px;
    margin-bottom: 12px;
}
.trade-tab {
    display: flex; gap: 0; margin-bottom: 16px;
    border-bottom: 1px solid #e5e7eb;
}
.trade-tab-btn {
    flex: 1; padding: 8px; font-size: 14px; font-weight: 600;
    background: none; border: none; cursor: pointer; color: #6b7280;
    border-bottom: 2px solid transparent; margin-bottom: -1px;
}
.trade-tab-btn.active-buy  { color: #16a34a; border-bottom-color: #16a34a; }
.trade-tab-btn.active-sell { color: #ef4444; border-bottom-color: #ef4444; }

/* Buttons */
div[data-testid="stButton"] > button {
    border-radius: 7px !important; font-weight: 600 !important;
    font-size: 13px !important; transition: all 0.15s !important;
}
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
    background: #fff !important; border: 1.5px solid #d1d5db !important;
    border-radius: 8px !important; color: #111827 !important; font-size: 13px !important;
}
div[data-testid="stTextInput"] input:focus, div[data-testid="stNumberInput"] input:focus {
    border-color: #16a34a !important;
    box-shadow: 0 0 0 3px rgba(22,163,74,0.1) !important;
}
div[data-testid="stSelectbox"] > div { border-radius: 8px !important; }
div[data-testid="stAlert"] { border-radius: 8px !important; font-size: 13px !important; }
div[data-testid="stRadio"] label { font-size: 13px !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30, show_spinner=False)
def live_price(symbol: str):
    try:
        data = yf.Ticker(symbol).history(period="1d", interval="1m")
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except Exception:
        pass
    return None

def fmt(v: float) -> str:
    return f"${v:,.2f}"

BADGE_COLORS = {
    "N": "#22c55e", "A": "#6366f1", "M": "#3b82f6",
    "T": "#f59e0b", "R": "#ec4899", "G": "#14b8a6",
}
def badge_col(sym: str) -> str:
    return BADGE_COLORS.get(sym[0].upper(), "#6b7280")

def portfolio_snapshot(uid: int):
    cash     = get_or_create_wallet(uid)
    holdings = get_holdings(uid)
    invested = current = 0.0
    enriched = []
    for h in holdings:
        lp    = live_price(h["symbol"])
        cost  = h["qty"] * h["avg_price"]
        cur   = h["qty"] * lp if lp else cost
        pnl   = cur - cost
        pp    = (pnl / cost * 100) if cost else 0.0
        invested += cost
        current  += cur
        enriched.append({**h, "live_price": lp, "cost": round(cost,2),
                         "current_value": round(cur,2), "pnl": round(pnl,2), "pnl_pct": round(pp,4)})
    total_pnl     = round(current - invested, 2)
    total_pnl_pct = round((total_pnl / invested * 100) if invested else 0.0, 4)
    return {
        "cash": round(cash,2), "invested_value": round(invested,2),
        "current_value": round(current,2), "total_pnl": total_pnl,
        "total_pnl_pct": total_pnl_pct,
        "portfolio_value": round(cash + current, 2),
        "holdings": enriched,
    }


# ── TOP BAR ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="top-bar">
    <div>
        <div class="tb-logo">Analyzer</div>
        <div class="tb-sub">Terminal v1.0</div>
    </div>
    <div style="flex:1;max-width:280px;background:#f3f4f6;border:1px solid #e5e7eb;border-radius:8px;
                padding:7px 14px;font-size:13px;color:#9ca3af;">🔍 &nbsp;Search Markets...</div>
    <div style="display:flex;gap:4px;">
        <span style="font-size:13px;font-weight:500;color:#374151;padding:6px 12px;">Markets</span>
        <span style="font-size:13px;font-weight:500;color:#374151;padding:6px 12px;">Indices</span>
        <span style="font-size:13px;font-weight:500;color:#374151;padding:6px 12px;">Sectors</span>
    </div>
    <div class="tb-right">
        <div>
            <div class="paper-bal">$100,000.00</div>
            <div class="paper-label">PAPER TRADING</div>
        </div>
        <div style="font-size:20px;">🔔</div>
        <div style="font-size:13px;color:#374151;font-weight:500;">👤 {name}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar + Main ────────────────────────────────────────────────────────────
sidebar_col, main_col = st.columns([1, 5.5], gap="small")

with sidebar_col:
    st.markdown("""
    <div style="background:#fff;border-right:1px solid #e5e7eb;min-height:calc(100vh - 56px);padding:20px 0;">
        <div style="padding:0 16px 20px;">
            <div style="font-size:17px;font-weight:800;color:#16a34a;">Analyzer</div>
            <div style="font-size:10px;color:#9ca3af;font-weight:500;">Terminal v1.0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📊  Watchlist", key="nav_wl",   use_container_width=True):
        st.switch_page("pages/watchlist.py")
    if st.button("📈  Market",    key="nav_mkt",  use_container_width=True):
        st.switch_page("pages/dashboard.py")
    if st.button("💼  Portfolio", key="nav_port", use_container_width=True):
        pass  # already here
    if st.button("📰  News",      key="nav_news", use_container_width=True):
        pass
    if st.button("⚙️  Settings",  key="nav_set",  use_container_width=True):
        pass
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    if st.button("💹  Trade Now", key="trade_now", use_container_width=True):
        pass
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    if st.button("🚪  Logout",    key="nav_logout", use_container_width=True):
        for k in ["logged_in", "id", "name", "stock_symbol"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")

# ── MAIN ─────────────────────────────────────────────────────────────────────
with main_col:
    uid_int = int(user_id)
    snap    = portfolio_snapshot(uid_int)

    # ── Summary cards ─────────────────────────────────────────────────────────
    pnl_today = snap["total_pnl"]
    pnl_sign  = "+" if pnl_today >= 0 else ""
    pnl_color = "sum-pos" if pnl_today >= 0 else "sum-neg"

    s1, s2, s3, s4 = st.columns(4)
    summary_data = [
        ("TOTAL VALUE",    fmt(snap["portfolio_value"]),
         f"↗ +{snap['total_pnl_pct']:.2f}%", "sum-pos"),
        ("TODAY'S P&L",    f"{pnl_sign}{fmt(abs(pnl_today))}",
         f"{'↑' if pnl_today>=0 else '↓'} {pnl_sign}{abs(snap['total_pnl_pct']):.2f}%", pnl_color),
        ("ALL-TIME P&L",   f"{pnl_sign}{fmt(abs(pnl_today))}",
         "↗ Lifetime", "sum-pos"),
        ("BUYING POWER",   fmt(snap["cash"]),
         "Cash Available", "sum-blue"),
    ]
    for col, (label, val, sub, cls) in zip([s1, s2, s3, s4], summary_data):
        with col:
            st.markdown(f"""
            <div class="sum-card">
                <div class="sum-label">{label}</div>
                <div class="sum-value {cls}">{val}</div>
                <div class="sum-sub {cls}">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── Holdings table ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="table-card">
        <div class="table-header">
            <div class="table-title">Holdings</div>
            <div style="display:flex;gap:10px;font-size:18px;color:#9ca3af;">
                <span style="cursor:pointer;">☰</span>
                <span style="cursor:pointer;">⬇</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    holdings = snap["holdings"]

    # Column headers
    h_cols = st.columns([2.5, 1, 1.5, 2, 2, 2.5])
    for col, label in zip(h_cols, ["TICKER", "QTY", "AVG PRICE", "CURRENT PRICE", "TOTAL VALUE", "UNREALIZED P&L"]):
        col.markdown(f"<div class='col-head' style='padding:8px 0 6px;'>{label}</div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:0 0 6px;border-color:#f3f4f6;'>", unsafe_allow_html=True)

    if not holdings:
        st.markdown("""
        <div style="text-align:center;padding:40px;color:#9ca3af;">
            <div style="font-size:28px;margin-bottom:8px;">📭</div>
            <div style="font-size:14px;font-weight:600;">No holdings yet</div>
            <div style="font-size:13px;margin-top:4px;">Place your first trade below.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for h in holdings:
            rc1,rc2,rc3,rc4,rc5,rc6 = st.columns([2.5, 1, 1.5, 2, 2, 2.5])
            lp = h["live_price"]
            lp_str  = fmt(lp) if lp else "N/A"
            pnl_cls = "price-pos" if h["pnl"] >= 0 else "price-neg"
            pnl_sign2 = "+" if h["pnl"] >= 0 else ""
            bc = badge_col(h["symbol"])
            abbr = h["symbol"][0].upper()

            with rc1:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;padding:6px 0;">
                    <div class="ticker-badge" style="background:{bc};">{abbr}</div>
                    <div>
                        <div class="ticker-sym">{h['symbol'].split('.')[0]}</div>
                        <div class="ticker-name">{h['symbol']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            rc2.markdown(f"<div style='padding-top:12px;font-size:13px;color:#374151;'>{h['qty']:.0f}</div>", unsafe_allow_html=True)
            rc3.markdown(f"<div style='padding-top:12px;font-size:13px;color:#374151;'>{fmt(h['avg_price'])}</div>", unsafe_allow_html=True)
            with rc4:
                lp_class = "price-pos" if (lp and lp > h["avg_price"]) else "price-neg" if lp else "price-neu"
                rc4.markdown(f"<div class='{lp_class}' style='padding-top:12px;'>{lp_str}</div>", unsafe_allow_html=True)
            rc5.markdown(f"<div style='padding-top:12px;font-size:13px;font-weight:700;color:#111827;'>{fmt(h['current_value'])}</div>", unsafe_allow_html=True)
            with rc6:
                rc6.markdown(f"<div class='{pnl_cls}' style='padding-top:10px;font-size:13px;font-weight:700;'>{pnl_sign2}{fmt(abs(h['pnl']))} ({pnl_sign2}{h['pnl_pct']:.1f}%)</div>", unsafe_allow_html=True)

            st.markdown("<hr style='margin:2px 0;border-color:#f9fafb;'>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── Bottom row: Open Orders + Recent Activity + Trade Form ────────────────
    bot1, bot2, bot3 = st.columns([2, 2, 2])

    # Open Orders (static display from trade log)
    with bot1:
        recent_trades = get_trades(uid_int, limit=5)
        orders_html = ""
        active_count = min(2, len(recent_trades))

        for t in recent_trades[:2]:
            sym    = t["symbol"]
            action = t["action"]
            price  = float(t["price"])
            qty    = float(t["qty"])
            orders_html += f"""
            <div class="order-row">
                <div class="order-dot"></div>
                <div class="order-main">
                    <div class="order-sym">{action} {sym} @ {fmt(price)}</div>
                    <div class="order-sub">Market Order • {qty:.0f} Shares</div>
                </div>
                <span class="cancel-btn">CANCEL</span>
            </div>
            """
        if not orders_html:
            orders_html = '<div style="font-size:13px;color:#9ca3af;padding:16px 0;text-align:center;">No open orders</div>'

        badge = f'<span class="active-badge">{active_count} ACTIVE</span>' if active_count else ""
        st.markdown(f"""
        <div class="side-card">
            <div class="side-title">
                Open Orders {badge}
            </div>
            {orders_html}
        </div>
        """, unsafe_allow_html=True)

    # Recent Activity
    with bot2:
        activity = get_trades(uid_int, limit=3)
        act_html = ""
        icons_map = {"BUY": ("✓", "green"), "SELL": ("↑", "orange")}

        for t in activity:
            icon, icon_cls = icons_map.get(t["action"], ("·","blue"))
            val    = float(t["total"])
            sign_c = "act-val-neg" if t["action"] == "BUY" else "act-val-pos"
            sign_s = "-" if t["action"] == "BUY" else "+"
            date_s = str(t["traded_at"])[:16] if t["traded_at"] else ""
            act_html += f"""
            <div class="act-row">
                <div class="act-icon {icon_cls}">{icon}</div>
                <div class="act-main">
                    <div class="act-sym">{t["action"]} Order: {t["symbol"]}</div>
                    <div class="act-sub">{date_s} • {float(t['qty']):.0f} SHARES @ {fmt(float(t['price']))}</div>
                </div>
                <div class="{sign_c}">{sign_s}{fmt(val)}</div>
            </div>
            """
        if not act_html:
            act_html = '<div style="font-size:13px;color:#9ca3af;padding:16px 0;text-align:center;">No activity yet</div>'

        st.markdown(f"""
        <div class="side-card">
            <div class="side-title">
                Recent Activity
                <a href="#" style="font-size:11px;font-weight:600;color:#16a34a;text-decoration:none;">VIEW ALL</a>
            </div>
            {act_html}
        </div>
        """, unsafe_allow_html=True)

    # Trade Form
    with bot3:
        st.markdown('<div class="trade-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:14px;font-weight:700;color:#111827;margin-bottom:14px;display:flex;align-items:center;gap:10px;">
            Trade
        </div>
        """, unsafe_allow_html=True)

        trade_action = st.radio("action", ["Buy", "Sell"], horizontal=True, key="t_action", label_visibility="collapsed")
        action_str   = "BUY" if trade_action == "Buy" else "SELL"

        st.markdown('<div style="font-size:11px;font-weight:700;color:#6b7280;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:4px;">SYMBOL</div>', unsafe_allow_html=True)
        t_sym = st.text_input("sym", label_visibility="collapsed", placeholder="e.g. AAPL · RELIANCE.NS", key="t_sym")
        t_sym = t_sym.strip().upper() if t_sym else ""
        if t_sym and "." not in t_sym and not t_sym.startswith("^"):
            t_sym += ".NS"

        lp = None
        if t_sym:
            with st.spinner(""):
                lp = live_price(t_sym)
            if lp:
                st.markdown(f"""
                <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;
                            padding:10px 14px;margin:6px 0 10px;">
                    <span style="font-size:11px;color:#6b7280;">Live Price</span><br>
                    <span style="font-size:20px;font-weight:800;color:#16a34a;">{fmt(lp)}</span>
                    <span style="font-size:11px;color:#9ca3af;margin-left:6px;">{t_sym}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<div style="font-size:11px;font-weight:700;color:#6b7280;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:4px;margin-top:8px;">ORDER TYPE</div>', unsafe_allow_html=True)
        order_type = st.selectbox("ot", ["Market Order", "Limit Order"], label_visibility="collapsed", key="t_otype")

        exec_price = lp
        if order_type == "Limit Order":
            st.markdown('<div style="font-size:11px;font-weight:700;color:#6b7280;letter-spacing:0.5px;text-transform:uppercase;margin:8px 0 4px;">LIMIT PRICE</div>', unsafe_allow_html=True)
            exec_price = st.number_input("lp", min_value=0.01,
                                         value=float(lp) if lp else 100.0,
                                         step=0.05, format="%.2f",
                                         label_visibility="collapsed", key="t_lp")

        st.markdown('<div style="font-size:11px;font-weight:700;color:#6b7280;letter-spacing:0.5px;text-transform:uppercase;margin:8px 0 4px;">QUANTITY (SHARES)</div>', unsafe_allow_html=True)
        qty = st.number_input("qty", min_value=0.0, step=1.0, format="%.0f",
                              label_visibility="collapsed", key="t_qty")

        if exec_price and qty > 0:
            est = qty * exec_price
            trading_fee = 0.0
            st.markdown(f"""
            <div style="background:#f9fafb;border-radius:8px;padding:10px 12px;margin:8px 0;font-size:12px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="color:#6b7280;">Est. Price</span>
                    <span style="font-weight:600;color:#111827;">{fmt(est)}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="color:#6b7280;">Trading Fee</span>
                    <span style="font-weight:600;color:#111827;">{fmt(trading_fee)}</span>
                </div>
                <div style="display:flex;justify-content:space-between;border-top:1px solid #e5e7eb;padding-top:6px;">
                    <span style="font-weight:700;color:#111827;">Total</span>
                    <span style="font-weight:700;color:#16a34a;">{fmt(est)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        btn_label = f"Execute {trade_action} Order"
        if st.button(btn_label, key="exec_trade", use_container_width=True, type="primary"):
            if not t_sym:
                st.error("Enter a symbol.")
            elif qty <= 0:
                st.error("Quantity must be > 0.")
            elif not exec_price or exec_price <= 0:
                st.error("Price unavailable.")
            else:
                ok, msg = execute_trade(uid_int, t_sym, action_str, qty, exec_price)
                if ok:
                    st.success(f"{'🟢' if action_str=='BUY' else '🔴'} {msg}")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

        st.markdown('</div>', unsafe_allow_html=True)

    # Reset
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    with st.expander("⚠️ Reset Portfolio"):
        st.caption("Deletes all trades & holdings. Restores $1,000,000 paper balance.")
        if st.button("🔄 Reset Everything", use_container_width=True, type="secondary"):
            reset_wallet(uid_int)
            st.cache_data.clear()
            st.success("Portfolio reset!")
            st.rerun()