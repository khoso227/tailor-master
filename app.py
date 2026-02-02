import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling, sidebar_header
from orders import add_order_ui

init_db()
conn = get_connection()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    apply_styling("Sahil & Arman Platform")
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("🔐 Enterprise Login")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Sign In"):
            user = conn.execute("SELECT id, role, shop_name FROM users WHERE email=? AND password=?", (email, pwd)).fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.user_role = user[1]
                st.session_state.shop_name = user[2]
                st.rerun()
            else: st.error("Invalid Credentials!")
else:
    # APPLY BRANDING
    apply_styling(st.session_state.shop_name)
    
    # CUSTOM SIDEBAR HEADER
    sidebar_header(st.session_state.shop_name, st.session_state.user_role)
    
    # NAVIGATION MENU
    if st.session_state.user_role == "super_admin":
        menu = st.sidebar.radio("🚀 CONTROL PANEL", ["🌍 Global Stats", "➕ New Shop Registration", "👥 All Shops List"])
        
        if menu == "🌍 Global Stats":
            st.subheader("Global Platform Analytics")
            # All global stats logic here...
            
        elif menu == "➕ New Shop Registration":
            st.subheader("Register New Client")
            # Registration form...

    else:
        # SHOP ADMIN MENU
        menu = st.sidebar.radio("💼 SHOP MANAGER", ["🏠 My Dashboard", "📏 New Order", "📊 My Reports", "🔐 Security"])

        if menu == "🏠 My Dashboard":
            st.subheader("Current Orders")
            df = pd.read_sql(f"SELECT name, phone, remaining, status FROM clients WHERE user_id={st.session_state.user_id}", conn)
            st.dataframe(df, use_container_width=True)

        elif menu == "📏 New Order":
            labels = ["Length", "Sleeves", "Shoulder", "Collar", "Chest", "Waist", "Hip", "Bottom"]
            # Calling the fixed function
            add_order_ui(labels, st.session_state.user_id)

    # LOGOUT AT THE BOTTOM
    st.sidebar.markdown("---")
    if st.sidebar.button("🔌 Secure Logout"):
        st.session_state.logged_in = False
        st.rerun()
