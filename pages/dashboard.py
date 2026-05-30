# pages/dashboard.py
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Analyzer · Market", page_icon="📈", layout="wide")

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

name = st.session_state.get("name", "User")
uid  = st.session_state.get("id", "—")

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

/* Top bar */
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

/* Index cards */
.idx-card {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 16px 18px;
}
.idx-label { font-size: 10px; font-weight: 700; color: #9ca3af; letter-spacing: 0.5px; text-transform: uppercase; }
.idx-name  { font-size: 14px; font-weight: 700; color: #111827; margin: 2px 0; }
.idx-val   { font-size: 20px; font-weight: 800; color: #111827; }
.idx-chg   { font-size: 12px; color: #6b7280; }
.idx-pct-pos { color: #16a34a; font-size: 14px; font-weight: 700; float: right; }
.idx-pct-neg { color: #ef4444; font-size: 14px; font-weight: 700; float: right; }

/* Sector heatmap */
.heatmap-card {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 18px 18px;
}
.heatmap-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 4px;
}
.hm-cell {
    border-radius: 6px; padding: 14px 10px;
    display: flex; flex-direction: column; justify-content: flex-end;
}
.hm-cell.pos { background: #16a34a; }
.hm-cell.pos-lt { background: #4ade80; }
.hm-cell.pos-xs { background: #86efac; }
.hm-cell.neg { background: #dc2626; }
.hm-cell.neg-lt { background: #f87171; }
.hm-cell.neg-xs { background: #fca5a5; }
.hm-name { font-size: 9px; font-weight: 700; color: rgba(255,255,255,0.75); letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 4px; }
.hm-pct  { font-size: 14px; font-weight: 800; color: #fff; }

/* Movers */
.movers-card {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 14px 16px;
}
.movers-title {
    font-size: 12px; font-weight: 700; color: #374151;
    margin-bottom: 12px; display: flex; align-items: center; gap: 6px;
}
.mover-row {
    display: flex; justify-content: space-between;
    align-items: center; padding: 7px 0;
    border-bottom: 1px solid #f3f4f6; font-size: 13px;
}
.mover-row:last-child { border-bottom: none; }
.mover-sym { font-weight: 700; color: #111827; }
.mover-pos { font-weight: 700; color: #16a34a; }
.mover-neg { font-weight: 700; color: #ef4444; }
.mover-vol { color: #6b7280; }

/* News card */
.news-card {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 16px;
}
.news-title { font-size: 14px; font-weight: 700; color: #111827; margin-bottom: 14px; }
.news-item  { padding: 12px 0; border-bottom: 1px solid #f3f4f6; }
.news-item:last-child { border-bottom: none; }
.news-tag {
    display: inline-block;
    padding: 2px 8px; border-radius: 4px;
    font-size: 10px; font-weight: 700; letter-spacing: 0.5px;
    text-transform: uppercase; margin-bottom: 6px;
}
.tag-breaking { background: #fee2e2; color: #dc2626; }
.tag-markets  { background: #dbeafe; color: #2563eb; }
.tag-commodities { background: #fef3c7; color: #d97706; }
.news-headline { font-size: 13px; font-weight: 700; color: #111827; line-height: 1.4; margin-bottom: 4px; }
.news-body     { font-size: 12px; color: #6b7280; line-height: 1.5; }
.news-time     { font-size: 11px; color: #9ca3af; margin-bottom: 4px; }
.news-img      { width: 100%; height: 80px; background: #f3f4f6; border-radius: 6px; margin: 8px 0; object-fit: cover; }

/* Buttons */
div[data-testid="stButton"] > button {
    border-radius: 7px !important; font-weight: 600 !important;
    font-size: 13px !important; transition: all 0.15s !important;
}
div[data-testid="stSelectbox"] > div { border-radius: 8px !important; }
div[data-testid="stTextInput"] input {
    background: #f3f4f6 !important; border: 1.5px solid #e5e7eb !important;
    border-radius: 8px !important; color: #111827 !important; font-size: 13px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #16a34a !important;
    box-shadow: 0 0 0 3px rgba(22,163,74,0.1) !important;
    background: #fff !important;
}
div[data-testid="stAlert"] { border-radius: 8px !important; font-size: 13px !important; }
div[data-testid="metric-container"] {
    background: #fff !important; border: 1px solid #e5e7eb !important;
    border-radius: 10px !important; padding: 14px 16px !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #111827 !important; font-size: 18px !important; font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
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

def calculate_macd(close: pd.Series):
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

INTERVAL_MAP = {
    "1D": ("1d",  "5m"),
    "1W": ("5d",  "15m"),
    "1M": ("1mo", "30m"),
    "1Y": ("1y",  "1d"),
    "ALL":("5y",  "1wk"),
}

# ── TOP BAR ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="top-bar">
    <div>
        <div class="tb-logo">Analyzer</div>
        <div class="tb-sub">Terminal v1.0</div>
    </div>
    <div style="flex:1;max-width:300px;background:#f3f4f6;border:1px solid #e5e7eb;border-radius:8px;
                padding:7px 14px;font-size:13px;color:#9ca3af;">
        🔍 &nbsp;Search markets...
    </div>
    <div style="display:flex;gap:4px;">
        <span style="font-size:13px;font-weight:600;color:#16a34a;padding:6px 12px;border-bottom:2px solid #16a34a;">Markets</span>
        <span style="font-size:13px;font-weight:500;color:#374151;padding:6px 12px;">Indices</span>
        <span style="font-size:13px;font-weight:500;color:#374151;padding:6px 12px;">Sectors</span>
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

# ── Sidebar + Main ────────────────────────────────────────────────────────────
sidebar_col, main_col, right_col = st.columns([1, 3.8, 1.6], gap="small")

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
        pass  # already here
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
    if st.button("🚪  Logout",    key="nav_logout", use_container_width=True):
        for k in ["logged_in", "id", "name", "stock_symbol"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────
with main_col:
    # ── Stock symbol state ────────────────────────────────────────────────────
    if "stock_symbol"   not in st.session_state: st.session_state["stock_symbol"]   = "^GSPC"
    if "chart_period"   not in st.session_state: st.session_state["chart_period"]   = "1M"
    if "show_chart"     not in st.session_state: st.session_state["show_chart"]     = False

    # ── Index cards ───────────────────────────────────────────────────────────
    ic1, ic2, ic3 = st.columns(3)

    @st.cache_data(ttl=120, show_spinner=False)
    def idx_bars(symbol: str):
        df = yf.Ticker(symbol).history(period="5d", interval="1d")
        return df["Close"].tolist() if not df.empty else []

    def bar_chart_svg(vals: list, positive: bool) -> str:
        if not vals: return ""
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx != mn else 1
        bars = ""
        w = 14
        gap = 4
        for i, v in enumerate(vals[-8:]):
            h = max(4, int(((v - mn) / rng) * 50))
            x = i * (w + gap)
            is_last = (i == len(vals[-8:]) - 1)
            color = "#16a34a" if (positive and is_last) else ("#ef4444" if (not positive and is_last) else ("#dcfce7" if positive else "#fecaca"))
            bars += f'<rect x="{x}" y="{60-h}" width="{w}" height="{h}" fill="{color}" rx="2"/>'
        total_w = len(vals[-8:]) * (w + gap)
        return f'<svg viewBox="0 0 {total_w} 62" style="width:100%;height:55px;">{bars}</svg>'

    idx_data = [
        ("^GSPC", "S&P 500", True),
        ("^IXIC", "Nasdaq 100", True),
        ("^DJI",  "Dow Jones",  False),
    ]

    for col, (sym, label, default_pos) in zip([ic1, ic2, ic3], idx_data):
        with col:
            bars = idx_bars(sym)
            positive = default_pos
            pct_str = "+1.24%"
            val_str = "5,248.12"
            chg_str = "+64.12"
            pct_class = "idx-pct-pos"

            if bars and len(bars) >= 2:
                chg_val = bars[-1] - bars[-2]
                pct_val = (chg_val / bars[-2]) * 100 if bars[-2] else 0
                positive = chg_val >= 0
                sign     = "+" if positive else ""
                pct_str  = f"{sign}{pct_val:.2f}%"
                val_str  = f"{bars[-1]:,.2f}"
                chg_str  = f"{sign}{chg_val:.2f}"
                pct_class = "idx-pct-pos" if positive else "idx-pct-neg"

            st.markdown(f"""
            <div class="idx-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <div class="idx-label">INDEX</div>
                        <div class="idx-name">{label}</div>
                        <div class="idx-val">{val_str} <span class="idx-chg">{chg_str}</span></div>
                    </div>
                    <div class="{pct_class}">{pct_str}</div>
                </div>
                {bar_chart_svg(bars, positive)}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── Sector Heatmap ────────────────────────────────────────────────────────
    hm_col, hm_ctrl = st.columns([5, 1])
    with hm_col:
        st.markdown("<div style='font-size:15px;font-weight:700;color:#111827;margin-bottom:8px;'>Sector Performance</div>", unsafe_allow_html=True)
    with hm_ctrl:
        st.markdown("<div style='font-size:12px;color:#6b7280;padding-top:6px;text-align:right;'>Daily Heatmap</div>", unsafe_allow_html=True)

    sectors = [
        ("TECH",    "+3.4%", "pos"),
        ("COMM",    "+1.8%", "pos-lt"),
        ("HEALTH",  "+0.4%", "pos-xs"),
        ("FINAN",   "-0.2%", "neg-xs"),
        ("ENERGY",  "-1.9%", "neg"),
        ("CONS D",  "+2.1%", "pos"),
        ("UTIL",    "+0.1%", "pos-xs"),
        ("INDUST",  "-0.8%", "neg-xs"),
        ("MATER",   "+1.1%", "pos-lt"),
        ("REAL E",  "-3.2%", "neg"),
    ]
    cells = "".join([
        f'<div class="hm-cell {cls}"><div class="hm-name">{name_}</div><div class="hm-pct">{pct}</div></div>'
        for name_, pct, cls in sectors
    ])
    st.markdown(f'<div class="heatmap-card"><div class="heatmap-grid">{cells}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── Movers ────────────────────────────────────────────────────────────────
    mv1, mv2, mv3 = st.columns(3)

    movers_data = {
        "Top Gainers": [("NVDA","+8.42%","pos"),("TSLA","+4.12%","pos"),("AMD","+3.89%","pos"),("COIN","+3.21%","pos")],
        "Top Losers":  [("INTC","-5.21%","neg"),("PYPL","-3.42%","neg"),("BA","-2.98%","neg"),("PFE","-2.11%","neg")],
        "Most Active": [("AAPL","84.2M","vol"),("MSFT","62.1M","vol"),("GOOGL","54.8M","vol"),("AMZN","41.2M","vol")],
    }
    icons = {"Top Gainers": "↗", "Top Losers": "↘", "Most Active": "▐▐"}

    for col, (title, rows) in zip([mv1, mv2, mv3], movers_data.items()):
        with col:
            rows_html = ""
            for sym, val, cls in rows:
                val_class = "mover-pos" if cls == "pos" else ("mover-neg" if cls == "neg" else "mover-vol")
                rows_html += f'<div class="mover-row"><span class="mover-sym">{sym}</span><span class="{val_class}">{val}</span></div>'
            st.markdown(f"""
            <div class="movers-card">
                <div class="movers-title">{title} <span style="font-size:14px;">{icons[title]}</span></div>
                {rows_html}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── Stock Chart Section ───────────────────────────────────────────────────
    st.markdown("<div style='font-size:15px;font-weight:700;color:#111827;margin-bottom:12px;'>📈 Stock Chart</div>",
                unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns([4, 2, 1])
    with sc1:
        stock_input = st.text_input("sym", label_visibility="collapsed",
                                    placeholder="Search symbol e.g. AAPL · TSLA · RELIANCE.NS",
                                    key="dash_sym")
    with sc2:
        tf_choice = st.selectbox("tf", list(INTERVAL_MAP.keys()), label_visibility="collapsed", key="tf_sel")
    with sc3:
        if st.button("Search 🔎", use_container_width=True):
            if stock_input.strip():
                st.session_state["stock_symbol"] = stock_input.strip().upper()
                st.session_state["chart_period"] = tf_choice
                st.session_state["show_chart"] = True

    if st.session_state.get("show_chart") or st.session_state["stock_symbol"] != "^GSPC":
        symbol   = st.session_state["stock_symbol"]
        period_key = st.session_state.get("chart_period", "1M")
        period, interval = INTERVAL_MAP.get(period_key, ("1mo", "30m"))

        with st.spinner(f"Loading {symbol}…"):
            try:
                df = load_stock_data(symbol, period, interval)
            except Exception as e:
                st.error(f"Failed to fetch: {e}")
                df = pd.DataFrame()

        if not df.empty:
            # Stock header info
            try:
                info = yf.Ticker(symbol).info
                price_now = df["Close"].iloc[-1]
                price_prev = df["Close"].iloc[-2] if len(df) > 1 else price_now
                chg = price_now - price_prev
                pct = (chg / price_prev * 100) if price_prev else 0
                sign = "+" if chg >= 0 else ""
                pct_color = "#16a34a" if chg >= 0 else "#ef4444"
                mkt_cap = info.get("marketCap", 0)
                mc_str  = f"${mkt_cap/1e12:.2f}T" if mkt_cap > 1e12 else (f"${mkt_cap/1e9:.1f}B" if mkt_cap else "N/A")
                pe_str  = f"{info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'), float) else "N/A"
                dy_str  = f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "0.00%"
                exch    = info.get("exchange", "NASDAQ")
                sector  = info.get("sector", "Technology")
                currency = info.get("currency", "USD")
                long_name = info.get("longName", symbol)

                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:18px 20px;margin-bottom:12px;">
                    <div style="display:flex;align-items:center;gap:14px;margin-bottom:10px;">
                        <div style="width:44px;height:44px;background:#dcfce7;border-radius:10px;
                                    display:flex;align-items:center;justify-content:center;font-size:18px;">📊</div>
                        <div>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:18px;font-weight:800;color:#111827;">{long_name}</span>
                                <span style="background:#f3f4f6;color:#374151;font-size:11px;font-weight:700;
                                             padding:3px 8px;border-radius:4px;">{symbol}</span>
                            </div>
                            <div style="font-size:12px;color:#9ca3af;">{exch} · {sector} · {currency}</div>
                        </div>
                        <div style="margin-left:auto;text-align:right;">
                            <div style="display:flex;align-items:center;gap:12px;">
                                <span style="font-size:11px;color:#6b7280;">MARKET CAP <b style="color:#111827;">{mc_str}</b></span>
                                <span style="font-size:11px;color:#6b7280;">P/E RATIO <b style="color:#111827;">{pe_str}</b></span>
                                <span style="font-size:11px;color:#6b7280;">DIV YIELD <b style="color:#111827;">{dy_str}</b></span>
                            </div>
                        </div>
                    </div>
                    <div style="display:flex;align-items:baseline;gap:12px;">
                        <span style="font-size:28px;font-weight:800;color:#111827;">${price_now:,.2f}</span>
                        <span style="font-size:14px;font-weight:600;color:{pct_color};">▲ {sign}{pct:.1f}% ({sign}${abs(chg):.2f})</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                pass

            # Candlestick
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
                increasing_line_color="#16a34a", decreasing_line_color="#ef4444",
                name=symbol,
            ))
            fig.update_layout(
                template="plotly_white",
                xaxis_title="", yaxis_title="Price",
                xaxis_rangeslider_visible=False,
                hovermode="x unified",
                height=380,
                margin=dict(l=0, r=0, t=10, b=10),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(family="Inter", size=11, color="#374151"),
                xaxis=dict(showgrid=True, gridcolor="#f3f4f6", linecolor="#e5e7eb"),
                yaxis=dict(showgrid=True, gridcolor="#f3f4f6", linecolor="#e5e7eb"),
            )
            fig.update_xaxes(showspikes=True, spikemode="across", spikesnap="cursor",
                             spikethickness=0.8, spikedash="dot", spikecolor="#9ca3af")
            fig.update_yaxes(showspikes=True, spikemode="across", spikesnap="cursor",
                             spikethickness=0.8, spikedash="dot", spikecolor="#9ca3af")
            st.plotly_chart(fig, use_container_width=True)

            # RSI + MACD
            df["RSI"]  = calculate_rsi(df["Close"])
            macd, signal = calculate_macd(df["Close"])

            r1, r2 = st.columns(2)
            with r1:
                rsi_fig = go.Figure()
                rsi_fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines",
                                             line=dict(color="#6366f1", width=1.5), name="RSI"))
                rsi_fig.add_hline(y=70, line_dash="dash", line_color="rgba(239,68,68,0.5)", line_width=1)
                rsi_fig.add_hline(y=30, line_dash="dash", line_color="rgba(34,197,94,0.5)", line_width=1)
                rsi_fig.add_hline(y=50, line_dash="dot",  line_color="rgba(148,163,184,0.4)", line_width=1)
                rsi_fig.update_layout(template="plotly_white", height=160,
                                      margin=dict(l=0,r=0,t=20,b=10), paper_bgcolor="#fff",
                                      plot_bgcolor="#fff", title=dict(text="RSI", font=dict(size=11)),
                                      yaxis=dict(range=[0,100], showgrid=True, gridcolor="#f3f4f6"),
                                      xaxis=dict(showgrid=True, gridcolor="#f3f4f6"))
                st.plotly_chart(rsi_fig, use_container_width=True)

            with r2:
                macd_fig = go.Figure()
                macd_fig.add_trace(go.Scatter(x=df.index, y=macd,   mode="lines",
                                              line=dict(color="#16a34a", width=1.5), name="MACD"))
                macd_fig.add_trace(go.Scatter(x=df.index, y=signal, mode="lines",
                                              line=dict(color="#ef4444", width=1),   name="Signal"))
                macd_fig.add_hline(y=0, line_color="#9ca3af", line_width=0.8)
                macd_fig.update_layout(template="plotly_white", height=160,
                                       margin=dict(l=0,r=0,t=20,b=10), paper_bgcolor="#fff",
                                       plot_bgcolor="#fff", title=dict(text="MACD", font=dict(size=11)),
                                       yaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
                                       xaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
                                       showlegend=False)
                st.plotly_chart(macd_fig, use_container_width=True)

# ── RIGHT PANEL: News ─────────────────────────────────────────────────────────
with right_col:
    st.markdown("""
    <div class="news-card">
        <div class="news-title">Market News</div>

        <div class="news-item">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <span class="news-tag tag-breaking">BREAKING</span>
                <span class="news-time">12m ago</span>
            </div>
            <div class="news-headline">Fed Signals Potential Rate Cut in Q3 Amid Cooling Inflation Data</div>
            <div class="news-body">Chairman Powell's latest remarks suggest a more dovish stance than...</div>
        </div>

        <div class="news-item">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <span class="news-tag tag-markets">MARKETS</span>
                <span class="news-time">45m ago</span>
            </div>
            <div class="news-headline">Tech Stocks Surge as AI Demand Continues to Outpace Supply</div>
            <div style="background:#f3f4f6;height:70px;border-radius:6px;margin:8px 0;display:flex;
                        align-items:center;justify-content:center;font-size:20px;">📊</div>
            <div class="news-body">Semiconductor leaders report record-breaking quarterly revenu...</div>
        </div>

        <div class="news-item">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <span class="news-tag tag-commodities">COMMODITIES</span>
                <span class="news-time">2h ago</span>
            </div>
            <div class="news-headline">Oil Prices Stabilize After Brief Spike on Geopolitical Tensions</div>
            <div class="news-body">Supply chain disruptions were less severe than feared, leading to...</div>
        </div>

        <div style="text-align:center;margin-top:14px;">
            <a href="#" style="font-size:12px;font-weight:600;color:#16a34a;text-decoration:none;">View All News</a>
        </div>
    </div>
    """, unsafe_allow_html=True)