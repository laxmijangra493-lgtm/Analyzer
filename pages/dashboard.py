# pages/dashboard.py
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

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
    text-align:right; padding:10px 14px;
    border-radius:12px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
}

.feature-card {
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 14px;
    padding: 18px 20px;
    height: 100%;
    transition: border-color 0.2s;
}
.feature-card:hover { border-color: rgba(99,102,241,0.5); }

/* Metric cards */
div[data-testid="metric-container"] {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 14px 18px;
}

/* Buttons */
div[data-testid="stButton"] > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: #6366f1 !important;
    box-shadow: 0 0 14px rgba(99,102,241,0.4) !important;
}

div[data-testid="stSelectbox"] > div { border-radius: 10px !important; }
div[data-testid="stTextInput"] input { border-radius: 10px !important; }

hr { border-color: rgba(255,255,255,0.06) !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
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


@st.cache_data(ttl=300, show_spinner=False)
def load_stock_data(symbol: str, period: str, interval: str) -> pd.DataFrame:
    """Cached stock fetch — refreshes every 5 minutes."""
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
    timeframe = st.selectbox(
        "Timeframe", INTERVAL_MAP.keys(), label_visibility="collapsed"
    )
with sc3:
    search_btn = st.button("Search 🔎", use_container_width=True)

if "stock_symbol" not in st.session_state:
    st.session_state["stock_symbol"] = "^NSEI"

if search_btn and stock_input:
    st.session_state["stock_symbol"] = stock_input.strip().upper()

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
    # Candlestick
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
        hovermode="x unified",
        height=480,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(
        showspikes=True, spikemode="across", spikesnap="cursor", spikethickness=0.5, spikedash="dot" ,        
        rangebreaks=[
            dict(bounds=["sat", "mon"]),
            dict(bounds=[15.5, 9.25], pattern="hour"),
        ]
    )
    fig.update_yaxes(showspikes=True, spikemode="across", spikesnap="cursor",  spikethickness=0.5, spikedash="dot")
    st.plotly_chart(fig, use_container_width=True)

    # ── Stock info metrics ────────────────────────────────────────────────────
    try:
        info = yf.Ticker(symbol).info
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("P/E Ratio",  info.get("trailingPE",  "N/A"))
        with m2: st.metric("EPS",        info.get("trailingEps", "N/A"))
        with m3:
            mc = info.get("marketCap")
            mc_str = f"₹{mc/1e7:.1f} Cr" if isinstance(mc, (int, float)) else "N/A"
            st.metric("Market Cap", mc_str)
        with m4: st.metric("52W High",   info.get("fiftyTwoWeekHigh", "N/A"))
    except Exception:
        pass  # Info fetch failures are non-critical

    st.divider()

    # ── RSI ───────────────────────────────────────────────────────────────────
    df["RSI"] = calculate_rsi(df["Close"])
    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        mode="lines", name="RSI",
        line=dict(color="#22d3ee", width=2)
    ))
    rsi_fig.add_hrect(y0=70, y1=100, fillcolor="red",   opacity=0.08, line_width=0)
    rsi_fig.add_hrect(y0=0,  y1=30,  fillcolor="green", opacity=0.08, line_width=0)
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="rgba(239,68,68,0.6)")
    rsi_fig.add_hline(y=50, line_dash="dot",  line_color="rgba(148,163,184,0.4)")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="rgba(34,197,94,0.6)")
    rsi_fig.update_layout(
        title=dict(text=f"{symbol} — RSI (14)", font=dict(size=13)),
        template="plotly_dark",
        height=230,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, 100]),
    )
    st.plotly_chart(rsi_fig, use_container_width=True)