import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui
import analytics

# Session Fix
if 'auth' not in st.session_state: st.session_state.auth = False
if 'u_shop' not in st.session_state: st.session_state.u_shop = "Guest"
if 'u_id' not in st.session_state: st.session_state.u_id = 0

init_db()
conn = get_connection()

# Theme Control
apply_styling('Dark') # Default to Navy Dark for professional look

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>👔 Tailor Master Pro</h1>", unsafe_allow_html=True)
        e = st.text_input("Login Email").strip()
        p = st.text_input("Password", type="password").strip()
        if st.button("Unlock Dashboard"):
            user = conn.execute("SELECT id, role, shop_name, email FROM users WHERE email=? AND password=?", (e, p)).fetchone()
            if user:
                st.session_state.auth = True
                st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user
                st.rerun()
            else: st.error("Inavlid Email/Password!")
else:
    # --- Sidebar Fixing ---
    st.sidebar.markdown(f"## 🏬 {st.session_state.u_shop}")
    
    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("ADMIN PANEL", ["Global Analytics", "Add New Shop", "Delete Shop"])
        if menu == "Global Analytics": analytics.show_global_stats()
        # ... Other admin functions ...
    else:
        menu = st.sidebar.radio("MENU", ["🏠 Dashboard", "📏 New Order", "📊 Reports", "🔐 Security"])
        
        if menu == "🏠 Dashboard":
            st.header(f"Orders: {st.session_state.u_shop}")
            
            # Metrics
            stats = pd.read_sql(f"SELECT SUM(total) as t, SUM(advance) as a, SUM(remaining) as r FROM clients WHERE user_id={st.session_state.u_id}", conn)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Sales", f"Rs.{stats['t'].iloc[0] or 0:,.0f}")
            c2.metric("Received", f"Rs.{stats['a'].iloc[0] or 0:,.0f}")
            c3.metric("Pending", f"Rs.{stats['r'].iloc[0] or 0:,.0f}")
            
            st.markdown("---")
            # FIX: Selecting exact columns from v11
            df = pd.read_sql(f"SELECT name, phone, remaining, pay_method, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Abhi koi orders nahi hain. 'New Order' se add karein.")

        elif menu == "📏 New Order":
            add_order_ui(st.session_state.u_id)

        elif menu == "📊 Reports":
            analytics.show_shop_reports(st.session_state.u_id)

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
