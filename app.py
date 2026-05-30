# python3 -m streamlit run app.py
import streamlit as st
from auth import register_user, login_user

st.set_page_config(page_title="Analyzer", page_icon="📈", layout="wide")

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f0f2f0 !important;
    color: #1a1a1a;
}

#MainMenu, footer, header { visibility: hidden; }

/* ── Full page layout ── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Top nav bar ── */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 40px;
    background: #fff;
    border-bottom: 1px solid #e5e7eb;
    position: sticky;
    top: 0;
    z-index: 100;
}
.top-nav-logo {
    font-size: 20px;
    font-weight: 800;
    color: #16a34a;
    letter-spacing: -0.5px;
}
.top-nav-links {
    display: flex;
    gap: 32px;
    font-size: 14px;
    color: #374151;
}
.top-nav-links a {
    color: #374151;
    text-decoration: none;
    font-weight: 500;
}
.top-nav-right {
    display: flex;
    gap: 16px;
    align-items: center;
}
.btn-signin {
    background: none;
    border: none;
    font-size: 14px;
    font-weight: 500;
    color: #374151;
    cursor: pointer;
}
.btn-open {
    background: #16a34a;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
}

/* ── Auth split card ── */
.auth-outer {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 40px 24px;
    min-height: calc(100vh - 130px);
    background: #f0f2f0;
}
.auth-card {
    display: flex;
    width: 100%;
    max-width: 900px;
    min-height: 600px;
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.07);
}
.auth-left {
    flex: 1;
    padding: 48px 44px;
    border-right: 1px solid #e5e7eb;
}
.auth-right {
    flex: 1;
    padding: 48px 44px;
    background: #fafafa;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.auth-title {
    font-size: 26px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 6px;
}
.auth-subtitle {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 28px;
}

/* Form labels */
.form-label {
    font-size: 13px;
    font-weight: 500;
    color: #374151;
    margin-bottom: 6px;
    display: block;
}

/* Input overrides */
div[data-testid="stTextInput"] label { display: none !important; }
div[data-testid="stTextInput"] input {
    background: #fff !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 8px !important;
    color: #111827 !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    box-shadow: none !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #16a34a !important;
    box-shadow: 0 0 0 3px rgba(22,163,74,0.12) !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #9ca3af !important; }

/* Submit button */
div[data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    background: #16a34a !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 11px 0 !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    margin-top: 6px !important;
    letter-spacing: 0.1px !important;
    transition: background 0.2s !important;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    background: #15803d !important;
}

/* Tabs */
div[data-testid="stTabs"] {
    background: transparent !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #f3f4f6 !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 2px !important;
    margin-bottom: 22px !important;
    border: none !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 6px !important;
    color: #6b7280 !important;
    padding: 7px 20px !important;
    border: none !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    background: #fff !important;
    color: #111827 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }
div[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

/* Right panel feature items */
.feat-item {
    display: flex;
    gap: 14px;
    align-items: flex-start;
    margin-bottom: 22px;
}
.feat-icon {
    width: 40px; height: 40px;
    background: #dcfce7;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}
.feat-text h4 {
    font-size: 14px;
    font-weight: 700;
    color: #111827;
    margin: 0 0 3px;
}
.feat-text p {
    font-size: 13px;
    color: #6b7280;
    margin: 0;
    line-height: 1.5;
}

/* Create Account button */
.btn-create {
    display: block;
    width: 100%;
    border: 1.5px solid #16a34a;
    background: transparent;
    color: #16a34a;
    border-radius: 8px;
    padding: 11px 0;
    font-size: 14px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 24px;
    cursor: pointer;
}

/* Mini chart bars */
.mini-chart {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 16px 20px;
}
.bars {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    height: 60px;
}
.bar {
    flex: 1;
    background: #bbf7d0;
    border-radius: 4px 4px 0 0;
}
.bar.dark { background: #16a34a; }
.bar-label {
    display: flex;
    justify-content: space-around;
    font-size: 11px;
    color: #9ca3af;
    margin-top: 6px;
    font-weight: 500;
}

/* Footer */
.page-footer {
    background: #fff;
    border-top: 1px solid #e5e7eb;
    padding: 20px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    color: #6b7280;
}
.footer-logo { font-weight: 800; color: #16a34a; font-size: 15px; }
.footer-links { display: flex; gap: 20px; }
.footer-links a { color: #6b7280; text-decoration: none; }

/* Streamlit column gap fix */
div[data-testid="column"] { padding: 0 !important; }

/* Alert styling */
div[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session init ──────────────────────────────────────────────────────────────
for key, default in [("logged_in", False), ("id", None), ("name", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state["logged_in"]:
    st.switch_page("pages/dashboard.py")

# ── Top Nav ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-nav">
    <div class="top-nav-logo">Analyzer</div>
    <div class="top-nav-links">
        <a href="#">Markets</a>
        <a href="#">Pricing</a>
        <a href="#">Docs</a>
        <a href="#">Support</a>
    </div>
    <div class="top-nav-right">
        <span class="btn-signin">Sign In</span>
        <button class="btn-open">Open Account</button>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Auth card layout ──────────────────────────────────────────────────────────
st.markdown('<div class="auth-outer">', unsafe_allow_html=True)
st.markdown('<div class="auth-card">', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="small")

# ── LEFT: Login / Signup forms ────────────────────────────────────────────────
with col_left:
    st.markdown('<div class="auth-left">', unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        st.markdown('<div class="auth-title">Welcome Back</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-subtitle">Log in to your professional terminal.</div>', unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown('<span class="form-label">Email / Username</span>', unsafe_allow_html=True)
            email    = st.text_input("Email", placeholder="Enter your identifier", key="li_email")
            st.markdown('<span class="form-label">Password</span>', unsafe_allow_html=True)
            password = st.text_input("Password", type="password", placeholder="••••••••", key="li_pw")
            submitted = st.form_submit_button("Sign In")

        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin:10px 0 16px;font-size:13px;">
            <label style="color:#374151;display:flex;align-items:center;gap:6px;cursor:pointer;">
                <input type="checkbox"> Remember Me
            </label>
            <a href="#" style="color:#16a34a;text-decoration:none;font-weight:500;">Forgot Password?</a>
        </div>
        <div style="display:flex;align-items:center;gap:12px;margin:16px 0;color:#9ca3af;font-size:12px;font-weight:500;letter-spacing:0.5px;">
            <div style="flex:1;height:1px;background:#e5e7eb;"></div>
            OR CONTINUE WITH
            <div style="flex:1;height:1px;background:#e5e7eb;"></div>
        </div>
        <div style="display:flex;gap:10px;">
            <button style="flex:1;border:1.5px solid #d1d5db;border-radius:8px;padding:9px;background:#fff;font-size:13px;font-weight:500;color:#374151;cursor:pointer;">
                ⊙ Google
            </button>
            <button style="flex:1;border:1.5px solid #d1d5db;border-radius:8px;padding:9px;background:#fff;font-size:13px;font-weight:500;color:#374151;cursor:pointer;">
                iOS Apple
            </button>
        </div>
        """, unsafe_allow_html=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                user_id, uname = login_user(email, password)
                if user_id:
                    st.session_state.update(logged_in=True, id=user_id, name=uname)
                    st.success(f"Welcome back, {uname}!")
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error("Invalid email or password.")

    with tab_signup:
        st.markdown('<div class="auth-title">Create Account</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-subtitle">Start trading with a free account.</div>', unsafe_allow_html=True)

        with st.form("signup_form"):
            st.markdown('<span class="form-label">Full Name</span>', unsafe_allow_html=True)
            s_name     = st.text_input("Full Name",  placeholder="John Doe", key="su_name")
            st.markdown('<span class="form-label">Mobile</span>', unsafe_allow_html=True)
            s_mobile   = st.text_input("Mobile",     placeholder="+91 98765 43210", key="su_mob")
            st.markdown('<span class="form-label">Email</span>', unsafe_allow_html=True)
            s_email    = st.text_input("Email",      placeholder="you@example.com", key="su_email")
            st.markdown('<span class="form-label">Password</span>', unsafe_allow_html=True)
            s_password = st.text_input("Password",   type="password", placeholder="Min 6 characters", key="su_pw")
            st.markdown('<span class="form-label">Confirm Password</span>', unsafe_allow_html=True)
            s_confirm  = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="su_cpw")
            submitted  = st.form_submit_button("Create Account")

        if submitted:
            if not all([s_name, s_email, s_password, s_confirm]):
                st.error("Please fill in all required fields.")
            elif len(s_password) < 6:
                st.error("Password must be at least 6 characters.")
            elif s_password != s_confirm:
                st.error("Passwords do not match.")
            else:
                if register_user(s_name, s_mobile, s_email, s_password):
                    st.success("Account created! You can now sign in. ✅")
                else:
                    st.error("An account with this email already exists.")

    st.markdown('</div>', unsafe_allow_html=True)

# ── RIGHT: Feature list + mini chart ─────────────────────────────────────────
with col_right:
    st.markdown("""
    <div class="auth-right">
        <div>
            <div style="font-size:22px;font-weight:700;color:#111827;margin-bottom:24px;">Join Analyzer</div>

            <div class="feat-item">
                <div class="feat-icon">📊</div>
                <div class="feat-text">
                    <h4>Real-time Market Data</h4>
                    <p>Low-latency feeds directly from global exchanges for millisecond precision.</p>
                </div>
            </div>

            <div class="feat-item">
                <div class="feat-icon">📉</div>
                <div class="feat-text">
                    <h4>Pro-level Technical Analysis</h4>
                    <p>Advanced charting tools with 100+ technical indicators and drawing layers.</p>
                </div>
            </div>

            <div class="feat-item">
                <div class="feat-icon">🧾</div>
                <div class="feat-text">
                    <h4>Paper Trading Simulation</h4>
                    <p>Refine your strategies in a risk-free environment with real market conditions.</p>
                </div>
            </div>

            <button class="btn-create">Create Account →</button>
        </div>

        <div class="mini-chart">
            <div class="bars">
                <div class="bar" style="height:40%;"></div>
                <div class="bar" style="height:55%;"></div>
                <div class="bar" style="height:38%;"></div>
                <div class="bar" style="height:70%;"></div>
                <div class="bar dark" style="height:88%;"></div>
                <div class="bar" style="height:65%;"></div>
                <div class="bar dark" style="height:95%;"></div>
            </div>
            <div class="bar-label">
                <span>MON</span><span>TUE</span><span>WED</span><span>THU</span><span>FRI</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close auth-card
st.markdown('</div>', unsafe_allow_html=True)  # close auth-outer

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-footer">
    <div class="footer-logo">Analyzer</div>
    <div class="footer-links">
        <a href="#">Privacy Policy</a>
        <a href="#">Terms of Service</a>
        <a href="#">Risk Disclosure</a>
        <a href="#">Cookie Settings</a>
    </div>
    <div>© 2024 Analyzer Terminal. Professional Grade Market Analysis.</div>
</div>
""", unsafe_allow_html=True)