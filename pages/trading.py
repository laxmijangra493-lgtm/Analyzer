# pages/trading.py

import streamlit as st
import yfinance as yf
import pandas as pd
import sys, os

# ── Import shared auth helpers ────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import (
    init_db,
    get_or_create_wallet,
    get_holdings,
    get_trades,
    execute_trade,
    reset_wallet,
    STARTING_BALANCE,
)

st.set_page_config(
    page_title="Analyzr · Paper Trading",
    page_icon="💹",
    layout="wide",
)

init_db()

# ── Auth guard ────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

user_id = st.session_state.get("id")
name    = st.session_state.get("name", "Trader")

if user_id is None:
    st.error("Session expired. Please login again.")
    st.switch_page("app.py")

# ── Global CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Logo ── */
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

/* ── Summary cards ── */
.sum-card {
    background: rgba(15,23,42,0.85);
    border: 1px solid rgba(99,102,241,0.22);
    border-radius: 14px;
    padding: 18px 22px;
    text-align: center;
}
.sum-label  { font-size:11px; letter-spacing:1.5px; color:#64748b; text-transform:uppercase; margin-bottom:4px; }
.sum-value  { font-size:22px; font-weight:700; color:#e2e8f0; }
.sum-pos    { color:#22c55e; }
.sum-neg    { color:#ef4444; }
.sum-neu    { color:#94a3b8; }

/* ── Trade panel ── */
.trade-panel {
    background: rgba(15,23,42,0.85);
    border: 1px solid rgba(99,102,241,0.22);
    border-radius: 14px;
    padding: 22px 24px;
}

/* ── Table rows ── */
.tbl-header {
    color:#64748b; font-size:11px; font-weight:700;
    letter-spacing:1px; text-transform:uppercase;
    padding-bottom:6px;
}
.holding-row {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom:6px;
}

/* ── Badge chips ── */
.badge-buy  { background:rgba(34,197,94,0.15);  color:#22c55e; border-radius:6px; padding:2px 10px; font-size:12px; font-weight:700; }
.badge-sell { background:rgba(239,68,68,0.15);  color:#ef4444; border-radius:6px; padding:2px 10px; font-size:12px; font-weight:700; }

/* ── Input tweaks ── */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background: #0f172a !important;
    border: 1px solid rgba(99,102,241,0.35) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color:#6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.18) !important;
}

/* ── Buttons ── */
div[data-testid="stButton"] > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: #6366f1 !important;
    box-shadow: 0 0 14px rgba(99,102,241,0.4) !important;
}

/* primary-looking BUY button override via container trick */
.buy-btn div[data-testid="stButton"] > button {
    background: linear-gradient(135deg,#22c55e,#16a34a) !important;
    color: white !important;
    border: none !important;
}
.sell-btn div[data-testid="stButton"] > button {
    background: linear-gradient(135deg,#ef4444,#dc2626) !important;
    color: white !important;
    border: none !important;
}

hr { border-color: rgba(255,255,255,0.06) !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def live_price(symbol: str) -> float | None:
    """Return latest price or None on failure."""
    try:
        data = yf.Ticker(symbol).history(period="1d", interval="1m")
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except Exception:
        pass
    return None


def fmt_inr(v: float) -> str:
    return f"₹{v:,.2f}"


def pnl_color(v: float) -> str:
    if v > 0:
        return "sum-pos"
    if v < 0:
        return "sum-neg"
    return "sum-neu"


def pnl_sign(v: float) -> str:
    return "+" if v > 0 else ""


# ── Compute portfolio snapshot ────────────────────────────────────

def portfolio_snapshot(user_id: int):
    """
    Returns:
        cash            : float
        holdings        : list of dicts with live_price, current_value, pnl, pnl_pct added
        invested_value  : float   (total cost of holdings)
        current_value   : float   (mark-to-market)
        total_pnl       : float
        total_pnl_pct   : float
        portfolio_value : float   (cash + current_value)
    """
    cash     = get_or_create_wallet(user_id)
    holdings = get_holdings(user_id)

    invested   = 0.0
    current    = 0.0

    enriched = []
    for h in holdings:
        lp = live_price(h["symbol"])
        cost    = h["qty"] * h["avg_price"]
        cur_val = h["qty"] * lp if lp else cost   # fallback to cost if price unavailable
        pnl     = cur_val - cost
        pnl_pct = (pnl / cost * 100) if cost else 0.0

        invested += cost
        current  += cur_val

        enriched.append({
            **h,
            "live_price"    : lp,
            "cost"          : round(cost,    2),
            "current_value" : round(cur_val, 2),
            "pnl"           : round(pnl,     2),
            "pnl_pct"       : round(pnl_pct, 4),
        })

    total_pnl     = round(current - invested, 2)
    total_pnl_pct = round((total_pnl / invested * 100) if invested else 0.0, 4)
    portfolio_val = round(cash + current, 2)

    return {
        "cash"           : round(cash,     2),
        "invested_value" : round(invested, 2),
        "current_value"  : round(current,  2),
        "total_pnl"      : total_pnl,
        "total_pnl_pct"  : total_pnl_pct,
        "portfolio_value": portfolio_val,
        "holdings"       : enriched,
    }


# ═══════════════════════════════════════════════════════════════════
#  RENDER
# ═══════════════════════════════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────
hcol1, hcol2 = st.columns([8, 2])
with hcol1:
    st.markdown("""
    <div class="logo-container">
        <div class="logo-icon"></div>
        <div>
            <div class="logo-text">Analy<span>zr</span></div>
            <div class="tagline">INSIGHTS • ANALYSIS • GROWTH</div>
        </div>
    </div>""", unsafe_allow_html=True)

with hcol2:
    st.markdown(f"""
    <div style="text-align:right;padding:10px 14px;border-radius:12px;
                background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);">
        <div style="font-size:13px;">👤 <b>{name}</b></div>
    </div>""", unsafe_allow_html=True)

# ── Nav bar ───────────────────────────────────────────────────────
n1, n2, n3, n4 = st.columns([4, 2, 2, 2])
with n2:
    if st.button("📊 Dashboard",  use_container_width=True): st.switch_page("pages/dashboard.py")
with n3:
    if st.button("👁 Watchlist",  use_container_width=True): st.switch_page("pages/watchlist.py")
with n4:
    if st.button("🚪 Logout",     use_container_width=True):
        for k in ["logged_in", "id", "name", "stock_symbol"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")

st.divider()

# ── Page title ────────────────────────────────────────────────────
st.markdown("## 💹 Paper Trading")
st.caption("Practice trading with ₹10,00,000 virtual money. No real money involved.")

st.markdown("")

# ── Load snapshot ─────────────────────────────────────────────────
snap = portfolio_snapshot(user_id)

# ── Summary cards (5 metrics) ─────────────────────────────────────
sc1, sc2, sc3, sc4, sc5 = st.columns(5)
cards = [
    ("💼 Portfolio Value",  fmt_inr(snap["portfolio_value"]), "sum-value"),
    ("💵 Available Cash",   fmt_inr(snap["cash"]),            "sum-value"),
    ("📦 Invested Value",   fmt_inr(snap["invested_value"]),  "sum-value"),
    ("📈 Current Value",    fmt_inr(snap["current_value"]),   "sum-value"),
    ("📊 Unrealised P&L",
     f"{pnl_sign(snap['total_pnl'])}{fmt_inr(snap['total_pnl'])} ({pnl_sign(snap['total_pnl_pct'])}{snap['total_pnl_pct']:.2f}%)",
     pnl_color(snap["total_pnl"])),
]
for col, (label, value, cls) in zip([sc1, sc2, sc3, sc4, sc5], cards):
    col.markdown(f"""
    <div class="sum-card">
        <div class="sum-label">{label}</div>
        <div class="sum-value {cls}">{value}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")
st.divider()

# ─────────────────────────────────────────────────────────────────
#  TWO-COLUMN LAYOUT: Trade Panel (left) | Holdings (right)
# ─────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1.6], gap="large")

# ── LEFT: Trade panel ─────────────────────────────────────────────
with left:
    st.markdown("### 🛒 Place Order")

    with st.container():
        st.markdown('<div class="trade-panel">', unsafe_allow_html=True)

        sym_input = st.text_input(
            "Stock Symbol",
            placeholder="e.g. RELIANCE.NS · TCS.NS · ^NSEI",
            key="trade_sym"
        )
        sym_input = sym_input.strip().upper() if sym_input else ""

        # Auto-suffix .NS if no dot present (and not an index like ^NSEI)
        if sym_input and "." not in sym_input and not sym_input.startswith("^"):
            sym_input += ".NS"

        # Live price fetch
        lp = None
        if sym_input:
            with st.spinner("Fetching live price…"):
                lp = live_price(sym_input)
            if lp:
                st.markdown(f"""
                <div style="background:rgba(34,211,238,0.07);border:1px solid rgba(34,211,238,0.25);
                            border-radius:8px;padding:10px 14px;margin:4px 0 10px;">
                    <span style="color:#64748b;font-size:12px;">Live Price</span><br>
                    <span style="font-size:22px;font-weight:700;color:#22d3ee;">{fmt_inr(lp)}</span>
                    <span style="color:#64748b;font-size:11px;margin-left:6px;">{sym_input}</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.warning("⚠️ Could not fetch price. Check symbol or try again.")

        qty = st.number_input(
            "Quantity (shares)",
            min_value=0.0,
            step=1.0,
            format="%.4f",
            key="trade_qty"
        )

        # Order mode: market (use live price) or limit (user enters price)
        order_mode = st.radio(
            "Order Type",
            ["Market Order", "Limit Order"],
            horizontal=True,
            key="order_mode"
        )

        exec_price = lp  # default to live
        if order_mode == "Limit Order":
            exec_price = st.number_input(
                "Limit Price (₹)",
                min_value=0.01,
                value=float(lp) if lp else 100.0,
                step=0.05,
                format="%.2f",
                key="limit_price"
            )

        # Estimated total
        if exec_price and qty > 0:
            est_total = qty * exec_price
            st.markdown(f"""
            <div style="margin:8px 0 4px;font-size:13px;color:#94a3b8;">
                Estimated Total: <b style="color:#e2e8f0;">{fmt_inr(est_total)}</b>
            </div>""", unsafe_allow_html=True)

        st.markdown("")
        b1, b2 = st.columns(2)
        with b1:
            st.markdown('<div class="buy-btn">', unsafe_allow_html=True)
            buy_clicked = st.button("✅ BUY",  use_container_width=True, key="btn_buy")
            st.markdown('</div>', unsafe_allow_html=True)
        with b2:
            st.markdown('<div class="sell-btn">', unsafe_allow_html=True)
            sell_clicked = st.button("🔴 SELL", use_container_width=True, key="btn_sell")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # close trade-panel

    # ── Execute trade ─────────────────────────────────────────────
    def _do_trade(action: str):
        if not sym_input:
            st.error("Please enter a stock symbol.")
            return
        if qty <= 0:
            st.error("Quantity must be greater than 0.")
            return
        if not exec_price or exec_price <= 0:
            st.error("Could not determine execution price.")
            return
        assert user_id is not None
        uid_int = user_id  # user_id is already verified non-None above; cast for type checker
        ok, msg = execute_trade(uid_int, sym_input, action, qty, exec_price)
        if ok:
            st.success(f"{'🟢' if action=='BUY' else '🔴'} {msg}")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(f"❌ {msg}")

    if buy_clicked:
        _do_trade("BUY")
    if sell_clicked:
        _do_trade("SELL")

    # ── Reset wallet ──────────────────────────────────────────────
    st.markdown("")
    with st.expander("⚠️ Reset Portfolio"):
        st.caption("This will delete all holdings and trades and restore ₹10,00,000 starting balance.")
        if st.button("🔄 Reset Everything", use_container_width=True, type="secondary"):
            reset_wallet(user_id)
            st.cache_data.clear()
            st.success("Portfolio reset to ₹10,00,000!")
            st.rerun()

# ── RIGHT: Holdings ───────────────────────────────────────────────
with right:
    st.markdown("### 📦 Holdings")

    holdings = snap["holdings"]

    if not holdings:
        st.info("No open positions. Place your first trade to get started! 🚀")
    else:
        # Table header
        h_cols = st.columns([2.5, 1.5, 1.5, 1.5, 2, 1])
        for col, label in zip(h_cols, ["Symbol", "Qty", "Avg Price", "LTP", "P&L", "Action"]):
            col.markdown(f"<div class='tbl-header'>{label}</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin:4px 0 10px;border-color:rgba(255,255,255,0.06);'>",
                    unsafe_allow_html=True)

        for h in holdings:
            c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.5, 1.5, 1.5, 2, 1])

            pnl_cls  = "sum-pos" if h["pnl"] >= 0 else "sum-neg"
            lp_str   = fmt_inr(h["live_price"]) if h["live_price"] else "N/A"
            pnl_str  = f"{pnl_sign(h['pnl'])}{fmt_inr(h['pnl'])}"
            ppct_str = f"({pnl_sign(h['pnl_pct'])}{h['pnl_pct']:.2f}%)"

            c1.markdown(
                f"<div style='font-weight:700;color:#e2e8f0;padding-top:8px;font-size:14px;'>{h['symbol']}</div>",
                unsafe_allow_html=True)
            c2.markdown(
                f"<div style='color:#cbd5e1;padding-top:8px;font-size:13px;'>{h['qty']:.4f}</div>",
                unsafe_allow_html=True)
            c3.markdown(
                f"<div style='color:#cbd5e1;padding-top:8px;font-size:13px;'>{fmt_inr(h['avg_price'])}</div>",
                unsafe_allow_html=True)
            c4.markdown(
                f"<div style='color:#22d3ee;padding-top:8px;font-size:13px;font-weight:600;'>{lp_str}</div>",
                unsafe_allow_html=True)
            c5.markdown(
                f"""<div class='{pnl_cls}' style='padding-top:6px;font-size:13px;font-weight:700;'>
                    {pnl_str}<br>
                    <span style='font-size:11px;font-weight:500;'>{ppct_str}</span>
                </div>""",
                unsafe_allow_html=True)

            # Quick chart link
            if c6.button("📈", key=f"hchart_{h['symbol']}", use_container_width=True):
                st.session_state["stock_symbol"] = h["symbol"]
                st.switch_page("pages/dashboard.py")

            st.markdown("<hr style='margin:4px 0 6px;border-color:rgba(255,255,255,0.04);'>",
                        unsafe_allow_html=True)

st.divider()

# ── Trade History ─────────────────────────────────────────────────
st.markdown("### 📋 Trade History")

trades = get_trades(user_id, limit=50)

if not trades:
    st.info("No trades yet. Your executed orders will appear here.")
else:
    th_cols = st.columns([2, 1.2, 1.5, 1.5, 2, 2])
    for col, label in zip(th_cols, ["Symbol", "Action", "Qty", "Price", "Total", "Time"]):
        col.markdown(f"<div class='tbl-header'>{label}</div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:4px 0 10px;border-color:rgba(255,255,255,0.06);'>",
                unsafe_allow_html=True)

    for t in trades:
        tc1, tc2, tc3, tc4, tc5, tc6 = st.columns([2, 1.2, 1.5, 1.5, 2, 2])
        badge = "badge-buy" if t["action"] == "BUY" else "badge-sell"

        tc1.markdown(
            f"<div style='font-weight:600;color:#e2e8f0;padding-top:6px;font-size:13px;'>{t['symbol']}</div>",
            unsafe_allow_html=True)
        tc2.markdown(
            f"<div style='padding-top:6px;'><span class='{badge}'>{t['action']}</span></div>",
            unsafe_allow_html=True)
        tc3.markdown(
            f"<div style='color:#cbd5e1;padding-top:6px;font-size:13px;'>{float(t['qty']):.4f}</div>",
            unsafe_allow_html=True)
        tc4.markdown(
            f"<div style='color:#cbd5e1;padding-top:6px;font-size:13px;'>{fmt_inr(float(t['price']))}</div>",
            unsafe_allow_html=True)
        tc5.markdown(
            f"<div style='color:#e2e8f0;font-weight:600;padding-top:6px;font-size:13px;'>{fmt_inr(float(t['total']))}</div>",
            unsafe_allow_html=True)
        tc6.markdown(
            f"<div style='color:#475569;padding-top:6px;font-size:12px;'>{t['traded_at']}</div>",
            unsafe_allow_html=True)

        st.markdown("<hr style='margin:4px 0 6px;border-color:rgba(255,255,255,0.03);'>",
                    unsafe_allow_html=True)

    st.markdown(
        f"<div style='text-align:right;color:#475569;font-size:12px;margin-top:6px;'>Showing last {len(trades)} trades</div>",
        unsafe_allow_html=True)