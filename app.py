import streamlit as st
from database import init_db, get_connection
from styling import apply_styling
from translations import get_text
from orders import add_order_ui
import analytics

# Session
if 'auth' not in st.session_state: st.session_state.auth = False

# --- SIDEBAR SETTINGS ---
st.sidebar.title("⚙️ Settings")
lang = st.sidebar.selectbox("🌐 Language / زبان", ["English", "Urdu"])
theme = st.sidebar.radio("🎨 Theme", ["🌙 Night Mode", "☀️ Day Mode"])

t = get_text(lang) # Load translations
apply_styling(theme, lang) # Apply visual style

init_db()
conn = get_connection()

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center;'>👔 {t['title']}</h1>", unsafe_allow_html=True)
        e = st.text_input(t['email']).strip()
        p = st.text_input(t['pass'], type="password").strip()
        if st.button(t['login']):
            user = conn.execute("SELECT id, role, shop_name, email FROM users WHERE email=? AND password=?", (e, p)).fetchone()
            if user:
                st.session_state.auth = True
                st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user
                st.rerun()
            else: st.error("Invalid Login!")
else:
    # --- MAIN NAVIGATION ---
    st.sidebar.markdown(f"### 🏬 {st.session_state.u_shop}")
    menu_options = [t['dash'], t['new_order'], t['reports'], t['security']]
    choice = st.sidebar.radio("MENU", menu_options)

    if choice == t['dash']:
        st.header(f"{t['dash']}: {st.session_state.u_shop}")
        # Metrics and Table logic here (Translated labels)
        
    elif choice == t['new_order']:
        add_order_ui(st.session_state.u_id, t)

    elif choice == t['reports']:
        analytics.show_shop_reports(st.session_state.u_id)

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
