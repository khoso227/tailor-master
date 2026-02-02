import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui
import analytics

# Session Initialization
if 'auth' not in st.session_state: st.session_state.auth = False
if 'u_role' not in st.session_state: st.session_state.u_role = ""

init_db()
conn = get_connection()

# Theme Setup
theme_choice = st.sidebar.toggle("🌙 Night Mode", value=True)
apply_styling('Dark' if theme_choice else 'Light')

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h2 style='text-align:center;'>👔 Tailor Master Pro</h2>", unsafe_allow_html=True)
        # .strip() se extra space khatam ho jayenge
        e_input = st.text_input("Email").strip()
        p_input = st.text_input("Password", type="password").strip()
        
        if st.button("Login Access"):
            user = conn.execute("SELECT id, role, shop_name FROM users WHERE email=? AND password=?", (e_input, p_input)).fetchone()
            if user:
                st.session_state.auth = True
                st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = user
                st.rerun()
            else:
                st.error("Invalid Login Details! Check spelling carefully.")
else:
    st.sidebar.markdown(f"### 🏬 {st.session_state.u_shop}")
    st.sidebar.markdown(f"**Role:** {st.session_state.u_role}")

    # --- Role Based View ---
    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("SUPER ADMIN CONTROL", ["🌍 Global Stats", "➕ Register New Shop", "👥 All Shops List"])
        
        if menu == "🌍 Global Stats":
            analytics.show_global_stats() # Idher srf summary dikhegi
        elif menu == "➕ Register New Shop":
            st.subheader("Add New Shopkeeper Account")
            with st.form("reg"):
                sn = st.text_input("Shop Name"); se = st.text_input("Email (Login ID)"); sp = st.text_input("Password")
                if st.form_submit_button("Create Partner Account"):
                    try:
                        conn.execute("INSERT INTO users (email, password, shop_name, role) VALUES (?,?,?,?)", (se, sp, sn, 'admin'))
                        conn.commit(); st.success("New Shopkeeper Registered!")
                    except: st.error("Email already exists!")

    else:
        # Shopkeepers Menu
        menu = st.sidebar.radio("SHOP MENU", ["🏠 My Dashboard", "📏 New Order", "📊 My Reports", "🔐 Security"])
        
        if menu == "🏠 My Dashboard":
            st.subheader(f"Orders for {st.session_state.u_shop}")
            # Yahan srf is dukan ka data nazar ayega (Filtering by user_id)
            df = pd.read_sql(f"SELECT name, phone, total, remaining, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            st.dataframe(df, use_container_width=True)

        elif menu == "📏 New Order":
            add_order_ui(["Length", "Sleeves", "Shoulder", "Collar", "Chest", "Waist", "Hip", "Bottom"], st.session_state.u_id)

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
