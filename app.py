import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui
import analytics

# Session Prep
if 'auth' not in st.session_state: st.session_state.auth = False

init_db()
conn = get_connection()

# Theme Switcher
theme_choice = st.sidebar.toggle("🌙 Night Mode", value=True)
apply_styling('Dark' if theme_choice else 'Light')

if not st.session_state.auth:
    # --- LOGIN SCREEN ---
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>👔 Tailor Master</h1>", unsafe_allow_html=True)
        e_in = st.text_input("Email").strip()
        p_in = st.text_input("Password", type="password").strip()
        if st.button("LOGIN"):
            user = conn.execute("SELECT id, role, shop_name, email FROM users WHERE email=? AND password=?", (e_in, p_in)).fetchone()
            if user:
                st.session_state.auth = True
                st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user
                st.rerun()
            else: st.error("Wrong Email or Password!")
else:
    # --- LOGGED IN ---
    st.sidebar.markdown(f"## 🏬 {st.session_state.u_shop}")
    st.sidebar.markdown(f"**Status:** `{st.session_state.u_role.upper()}`")

    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("CONTROL PANEL", ["🌍 Global Stats", "➕ Register Shop", "🗑️ Delete/Manage Shops"])
        
        if menu == "🌍 Global Stats":
            analytics.show_global_stats()
        
        elif menu == "🗑️ Delete/Manage Shops":
            st.header("Manage Registered Shops")
            shops = pd.read_sql("SELECT id, shop_name, email FROM users WHERE role='admin'", conn)
            st.dataframe(shops, use_container_width=True)
            
            # Delete Logic
            target_id = st.number_input("Enter Shop ID to Delete", step=1)
            if st.button("❌ PERMANENTLY DELETE SHOP"):
                conn.execute(f"DELETE FROM users WHERE id={target_id}")
                conn.execute(f"DELETE FROM clients WHERE user_id={target_id}")
                conn.commit()
                st.warning(f"Shop ID {target_id} and its data deleted!")
                st.rerun()

    else:
        # --- SHOP KEEPER VIEW ---
        menu = st.sidebar.radio("MENU", ["🏠 My Dashboard", "📏 New Order", "📊 Reports", "🔐 Security & Profile"])

        if menu == "🏠 My Dashboard":
            st.header(f"Orders: {st.session_state.u_shop}")
            # Hisab Kitab Summary
            stats = pd.read_sql(f"SELECT SUM(total) as t, SUM(advance) as a, SUM(remaining) as r FROM clients WHERE user_id={st.session_state.u_id}", conn)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Work", f"Rs.{stats['t'].iloc[0] or 0:,.0f}")
            c2.metric("Cash Received", f"Rs.{stats['a'].iloc[0] or 0:,.0f}")
            c3.metric("Outstanding", f"Rs.{stats['r'].iloc[0] or 0:,.0f}")
            
            st.markdown("---")
            df = pd.read_sql(f"SELECT name, phone, remaining, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            st.dataframe(df, use_container_width=True)

        elif menu == "📏 New Order":
            add_order_ui(["Length", "Sleeves", "Shoulder", "Collar", "Chest", "Waist", "Hip", "Bottom"], st.session_state.u_id)

        elif menu == "🔐 Security & Profile":
            st.header("👤 Your Profile & Security")
            st.info(f"**Shop Name:** {st.session_state.u_shop}\n\n**Login Email:** {st.session_state.u_email}")
            
            st.markdown("### 🔑 Reset Password")
            with st.form("pass_reset"):
                new_p = st.text_input("New Password", type="password")
                confirm_p = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Update Password"):
                    if new_p == confirm_p and len(new_p) > 3:
                        conn.execute(f"UPDATE users SET password='{new_p}' WHERE id={st.session_state.u_id}")
                        conn.commit()
                        st.success("Password Updated! Use new password next time.")
                    else: st.error("Passwords don't match or too short!")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()
