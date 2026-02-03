import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui

# --- 1. Session & Database Initialization ---
# Session variables ko initialize karna zaroori hai taaki error na aaye
if 'auth' not in st.session_state: st.session_state.auth = False
if 'u_id' not in st.session_state: st.session_state.u_id = 0
if 'u_shop' not in st.session_state: st.session_state.u_shop = "Guest"

init_db()
conn = get_connection()

# --- 2. Apply Theme & Wallpapers ---
# Ye function styling.py se 30 wallpapers aur Navy theme apply karega
apply_styling()

# --- 3. Main Application Logic ---
if not st.session_state.auth:
    # --- LOGIN INTERFACE ---
    st.markdown("<h1 style='text-align:center;'>👔 Tailor Master Pro</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("### Secure Access")
        email = st.text_input("📧 Email Address").strip()
        pwd = st.text_input("🔑 Password", type="password").strip()
        
        if st.button("Login to Dashboard", use_container_width=True):
            # Database se user check karein
            user = conn.execute("SELECT id, shop_name FROM users WHERE email=? AND password=?", (email, pwd)).fetchone()
            if user:
                st.session_state.auth = True
                st.session_state.u_id = user[0]
                st.session_state.u_shop = user[1]
                st.rerun()
            else:
                st.error("Ghalt Email ya Password! Dobara koshish karein.")
else:
    # --- LOGGED IN: SIDEBAR NAVIGATION ---
    st.sidebar.markdown(f"## 🏬 {st.session_state.u_shop}")
    menu = st.sidebar.radio("MAIN MENU", ["🏠 Dashboard", "📏 New Order", "🔐 Security"])

    if menu == "🏠 Dashboard":
        st.header(f"Welcome, {st.session_state.u_shop}")
        
        # 📊 BUSINESS METRICS (Hisab Kitab)
        try:
            stats_query = f"SELECT SUM(total) as t, SUM(remaining) as r FROM clients WHERE user_id={st.session_state.u_id}"
            stats = pd.read_sql(stats_query, conn)
            total_biz = stats['t'].iloc[0] or 0
            pending_bal = stats['r'].iloc[0] or 0
            
            c1, c2 = st.columns(2)
            c1.metric("Total Business (Gross)", f"Rs.{total_biz:,.0f}")
            c2.metric("Pending Recovery (Udhaar)", f"Rs.{pending_bal:,.0f}")
        except Exception as e:
            st.info("Start adding orders to see business summary.")

        st.divider()

        # 📋 ORDERS TABLE
        st.subheader("Recent Client Orders")
        orders_query = f"""
            SELECT order_no as 'Order #', name as 'Client Name', 
            remaining as 'Balance', status as 'Status' 
            FROM clients WHERE user_id={st.session_state.u_id} 
            ORDER BY id DESC
        """
        df = pd.read_sql(orders_query, conn)
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Abhi tak koi order nahi hai. 'New Order' par click karke add karein.")

    elif menu == "📏 New Order":
        # Azad Tailor ki slip wala form yahan load hoga
        add_order_ui(st.session_state.u_id)

    elif menu == "🔐 Security":
        st.header("👤 Profile & Password Security")
        st.info(f"**Shop Name:** {st.session_state.u_shop}")
        
        new_pwd = st.text_input("Change Password", type="password")
        if st.button("Update Password"):
            if len(new_pwd) >= 4:
                conn.execute("UPDATE users SET password=? WHERE id=?", (new_pwd, st.session_state.u_id))
                conn.commit()
                st.success("Password kamyabi se badal diya gaya!")
            else:
                st.error("Password kam se kam 4 characters ka hona chahiye.")

    # SIDEBAR BOTTOM
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout Access"):
        st.session_state.auth = False
        st.rerun()
