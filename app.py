# python3 -m streamlit run app.py
import streamlit as st
from auth import register_user, login_user

st.set_page_config(page_title="Analyzr", page_icon="📈", layout="centered")

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Card wrapper */
.auth-card {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 18px;
    padding: 36px 40px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5);
    backdrop-filter: blur(8px);
}

/* Logo */
.logo-container { display:flex; align-items:center; gap:16px; padding:16px 0 28px; }
.logo-icon {
    width:52px; height:52px;
    background: linear-gradient(135deg,#22d3ee,#6366f1,#a855f7);
    clip-path: polygon(10% 90%,40% 10%,55% 40%,75% 25%,90% 10%,90% 90%);
}
.logo-text { font-size:36px; font-weight:700; color:#e5e7eb; }
.logo-text span {
    background: linear-gradient(135deg,#22d3ee,#6366f1,#a855f7);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.tagline {
    font-size:11px; letter-spacing:3px; margin-top:-6px;
    background: linear-gradient(90deg,#22d3ee,#6366f1,#a855f7);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}

/* Inputs */
div[data-testid="stTextInput"] input {
    background: #0f172a !important;
    border: 1px solid rgba(99,102,241,0.4) !important;
    border-radius: 10px !important;
    color: #e5e7eb !important;
    padding: 10px 14px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
}

/* Primary button */
div[data-testid="stFormSubmitButton"] > button {
    width: 100%;
    background: linear-gradient(135deg,#6366f1,#a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    margin-top: 8px;
    transition: opacity 0.2s;
}
div[data-testid="stFormSubmitButton"] > button:hover { opacity: 0.88 !important; }

/* Tabs */
div[data-testid="stTabs"] button { font-weight: 600; font-size: 14px; }
</style>
""", unsafe_allow_html=True)


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


# ── Session init ─────────────────────────────────────────────────────────────
for key, default in [("logged_in", False), ("id", None), ("name", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

# Redirect if already logged in
if st.session_state["logged_in"]:
    st.switch_page("pages/dashboard.py")

show_logo()

tab_login, tab_signup = st.tabs(["🔐  Login", "🆕  Sign Up"])

# ── LOGIN ─────────────────────────────────────────────────────────────────────
with tab_login:
    with st.form("login_form"):
        email    = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Login")

    if submitted:
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            user_id, name = login_user(email, password)
            if user_id:
                st.session_state.update(logged_in=True, id=user_id, name=name)
                st.success(f"Welcome back, {name}! 👋")
                st.switch_page("pages/dashboard.py")
            else:
                st.error("Invalid email or password.")

# ── SIGN UP ───────────────────────────────────────────────────────────────────
with tab_signup:
    with st.form("signup_form"):
        s_name     = st.text_input("Full Name",  placeholder="John Doe")
        s_mobile   = st.text_input("Mobile",     placeholder="+91 98765 43210")
        s_email    = st.text_input("Email",      placeholder="you@example.com")
        s_password = st.text_input("Password",   type="password", placeholder="Min 6 characters")
        s_confirm  = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
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
                st.success("Account created! You can now log in. ✅")
            else:
                st.error("An account with this email already exists.")
