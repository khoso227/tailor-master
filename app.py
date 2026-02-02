import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui
import analytics

# Session Management
if 'auth' not in st.session_state: st.session_state.auth = False

init_db()
conn = get_connection()

# --- TOP SIDEBAR TOGGLE (Day/Night) ---
theme_choice = st.sidebar.radio("🎨 Select Theme", ["🌙 Night Mode", "☀️ Day Mode"], horizontal=True)
apply_styling(theme_choice)

if not st.session_state.auth:
    # --- LOGIN ---
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>👔 Tailor Master Pro</h1>", unsafe_allow_html=True)
        e = st.text_input("Login Email").strip()
        p = st.text_input("Password", type="password").strip()
        if st.button("Access Account"):
            user = conn.execute("SELECT id, role, shop_name, email FROM users WHERE email=? AND password=?", (e, p)).fetchone()
            if user:
                st.session_state.auth = True
                st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user
                st.rerun()
            else: st.error("Wrong Email/Password!")
else:
    # --- LOGGED IN VIEW ---
    st.sidebar.markdown(f"### 🏬 {st.session_state.u_shop}")
    
    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("ADMIN CONTROL", ["Global Stats", "Register Shop", "Delete Shop"])
        
        if menu == "Global Stats":
            analytics.show_global_stats() # Fixed function call
        elif menu == "Register Shop":
            st.header("➕ Add New Partner")
            sn = st.text_input("Shop Name")
            se = st.text_input("Email")
            sp = st.text_input("Password")
            if st.button("Create Account"):
                conn.execute("INSERT INTO users (email, password, shop_name, role) VALUES (?,?,?,?)", (se, sp, sn, 'admin'))
                conn.commit(); st.success("Partner Added!")
        elif menu == "Delete Shop":
            st.header("🗑️ Delete Shop")
            df = pd.read_sql("SELECT id, shop_name, email FROM users WHERE role='admin'", conn)
            st.dataframe(df, use_container_width=True)
            did = st.number_input("Enter ID to Delete", step=1)
            if st.button("Delete"):
                conn.execute(f"DELETE FROM users WHERE id={did}")
                conn.commit(); st.rerun()

    else:
        # Shop Menu
        menu = st.sidebar.radio("MENU", ["Dashboard", "New Order", "Reports", "Security"])
        
        if menu == "Dashboard":
            st.header(f"Orders: {st.session_state.u_shop}")
            df = pd.read_sql(f"SELECT name, phone, remaining, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            st.dataframe(df, use_container_width=True)
        elif menu == "New Order":
            add_order_ui(st.session_state.u_id)
        elif menu == "Reports":
            analytics.show_shop_reports(st.session_state.u_id)
        elif menu == "Security":
            st.header("🔐 Profile Settings")
            st.info(f"Shop: {st.session_state.u_shop}\nEmail: {st.session_state.u_email}")

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
