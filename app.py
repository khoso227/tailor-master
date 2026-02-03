import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui

# --- 1. Session Setup ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'u_id' not in st.session_state: st.session_state.u_id = 0

init_db()
conn = get_connection()

# --- 2. Styling ---
apply_styling('Dark')

# --- 3. Login Interface ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>👔 Tailor Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        email = st.text_input("📧 Email").strip()
        pwd = st.text_input("🔑 Password", type="password").strip()
        
        if st.button("Login Access"):
            user = conn.execute("SELECT id, shop_name FROM users WHERE email=? AND password=?", (email, pwd)).fetchone()
            if user:
                st.session_state.auth = True
                st.session_state.u_id = user[0]
                st.session_state.u_shop = user[1]
                st.rerun()
            else:
                st.error("Wrong Credentials!")
else:
    # --- Sidebar Navigation ---
    st.sidebar.title(f"🏬 {st.session_state.u_shop}")
    menu = st.sidebar.radio("Main Menu", ["📊 Dashboard", "📏 New Order", "🔐 Security"])

    if menu == "📊 Dashboard":
        st.header(f"Orders: {st.session_state.u_shop}")
        # Summary Metrics
        stats = pd.read_sql(f"SELECT SUM(total) as t, SUM(remaining) as r FROM clients WHERE user_id={st.session_state.u_id}", conn)
        c1, c2 = st.columns(2)
        c1.metric("Total Business", f"Rs.{stats['t'].iloc[0] or 0:,.0f}")
        c2.metric("Pending Balance", f"Rs.{stats['r'].iloc[0] or 0:,.0f}")
        
        st.divider()
        df = pd.read_sql(f"SELECT order_no, name, remaining, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
        st.dataframe(df, use_container_width=True)

    elif menu == "📏 New Order":
        add_order_ui(st.session_state.u_id)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
