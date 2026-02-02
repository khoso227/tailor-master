import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui
import analytics

# --- 1. Robust Initialization (Prevents Errors) ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'u_id' not in st.session_state: st.session_state.u_id = 0
if 'u_role' not in st.session_state: st.session_state.u_role = ""
if 'u_shop' not in st.session_state: st.session_state.u_shop = "Guest"
if 'theme' not in st.session_state: st.session_state.theme = 'Dark'

init_db()
conn = get_connection()

# --- 2. Theme Toggle ---
theme_choice = st.sidebar.toggle("🌙 Night Mode", value=True)
st.session_state.theme = 'Dark' if theme_choice else 'Light'
apply_styling(st.session_state.theme)

# --- 3. Login Logic ---
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h2 style='text-align:center;'>👔 Tailor Master Pro</h2>", unsafe_allow_html=True)
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Login Access"):
            user = conn.execute("SELECT id, role, shop_name FROM users WHERE email=? AND password=?", (email, pwd)).fetchone()
            if user:
                st.session_state.auth = True
                st.session_state.u_id = user[0]
                st.session_state.u_role = user[1]
                st.session_state.u_shop = user[2]
                st.rerun()
            else:
                st.error("Invalid Login Details")
else:
    # Sidebar Header
    st.sidebar.markdown(f"### 🏬 {st.session_state.u_shop}")
    st.sidebar.markdown(f"`Role: {st.session_state.u_role.upper()}`")
    st.sidebar.markdown("---")

    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("🚀 CONTROL PANEL", ["🌍 Global Stats", "➕ Register Shop", "👥 Shop Directory"])
        
        if menu == "🌍 Global Stats":
            analytics.show_global_stats() # Detailed Income & Fees here
        elif menu == "➕ Register Shop":
            st.subheader("Create New Partner Account")
            with st.form("reg_form"):
                n = st.text_input("Shop Name"); e = st.text_input("Email"); p = st.text_input("Password")
                if st.form_submit_button("Register"):
                    conn.execute("INSERT INTO users (email, password, shop_name, role) VALUES (?,?,?,?)", (e,p,n,'admin'))
                    conn.commit(); st.success("Shop Registered!")

    else:
        # Shop Admin Menu
        menu = st.sidebar.radio("💼 MENU", ["🏠 My Dashboard", "📏 New Order", "📊 My Reports", "🔐 Security"])

        if menu == "🏠 My Dashboard":
            st.subheader("Current Active Orders")
            df = pd.read_sql(f"SELECT name, phone, total, remaining, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            st.dataframe(df, use_container_width=True)

        elif menu == "📏 New Order":
            add_order_ui(["Length", "Sleeves", "Shoulder", "Collar", "Chest", "Waist", "Hip", "Bottom"], st.session_state.u_id)

        elif menu == "📊 My Reports":
            analytics.show_shop_reports(st.session_state.u_id)

        elif menu == "🔐 Security":
            st.subheader("Change System Password")
            new_p = st.text_input("New Secure Password", type="password")
            if st.button("Update Now"):
                conn.execute(f"UPDATE users SET password='{new_p}' WHERE id={st.session_state.u_id}")
                conn.commit(); st.success("Security Updated!")

    st.sidebar.markdown("---")
    if st.sidebar.button("🔌 Secure Logout"):
        st.session_state.auth = False
        st.rerun()
