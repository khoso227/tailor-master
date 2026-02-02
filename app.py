import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from translations import get_text
from orders import add_order_ui
import analytics

# --- Session Initialization ---
if 'auth' not in st.session_state: st.session_state.auth = False

init_db()
conn = get_connection()

# --- Sidebar Global Settings ---
st.sidebar.markdown("### ⚙️ Settings")
lang = st.sidebar.selectbox("🌐 Language", ["English", "Urdu"])
theme = st.sidebar.radio("🎨 Theme", ["🌙 Night Mode", "☀️ Day Mode"])
t = get_text(lang)
apply_styling(theme, lang)

if not st.session_state.auth:
    # --- Login / Register View ---
    st.markdown(f"<h1 style='text-align:center;'>👔 {t['title']}</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs([t['login'], t['register'], t['forgot']])
    
    with tab1: # Login
        le = st.text_input(t['email'], key="login_e").strip().lower()
        lp = st.text_input(t['pass'], type="password", key="login_p").strip()
        if st.button(t['login'], key="login_btn"):
            user = conn.execute("SELECT id, role, shop_name, email, status FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
            if user:
                if user[4] == 'Blocked': st.error("Account Blocked! Contact Admin.")
                else:
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user[0], user[1], user[2], user[3]
                    st.rerun()
            else: st.error("Invalid Details!")

    with tab2: # Register
        st.subheader(t['register'])
        reg_sn = st.text_input(t['shop'])
        reg_ph = st.text_input(t['phone'])
        reg_e = st.text_input(t['email'], key="reg_e").strip().lower()
        reg_p = st.text_input(t['pass'], key="reg_p").strip()
        reg_sq = st.text_input(t['s_q'])
        reg_sa = st.text_input(t['s_a'])
        if st.button("Register My Shop"):
            try:
                conn.execute("INSERT INTO users (email, password, shop_name, role, phone, security_q, security_a) VALUES (?,?,?,?,?,?,?)", 
                             (reg_e, reg_p, reg_sn, 'admin', reg_ph, reg_sq, reg_sa))
                conn.commit(); st.success("Account Created! Please Login.")
            except: st.error("Email already exists!")

    with tab3: # Forgot Password
        fe = st.text_input("Enter Email").strip().lower()
        if fe:
            f_user = conn.execute("SELECT security_q, security_a, password FROM users WHERE LOWER(email)=?", (fe,)).fetchone()
            if f_user:
                st.info(f"Question: {f_user[0]}")
                ans = st.text_input("Answer")
                if st.button("Show Password"):
                    if ans == f_user[1]: st.success(f"Password: {f_user[2]}")
                    else: st.error("Wrong Answer!")
else:
    # --- LOGGED IN ---
    st.sidebar.markdown(f"### 🏬 {st.session_state.u_shop}")
    
    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("ADMIN MENU", ["Shop Payments", "Global Stats"])
        if menu == "Shop Payments":
            import urllib.parse
            st.header("💳 Partner Management")
            shops = pd.read_sql("SELECT id, shop_name, phone, email, fee_status, status FROM users WHERE role='admin'", conn)
            st.dataframe(shops, use_container_width=True)
            sid = st.number_input("Enter ID", step=1)
            if st.button("Send Payment Link"):
                s_data = conn.execute("SELECT shop_name, phone FROM users WHERE id=?", (sid,)).fetchone()
                msg = f"Payment Reminder for {s_data[0]}."
                url = f"https://wa.me/{s_data[1]}?text={urllib.parse.quote(msg)}"
                st.markdown(f"[Send WhatsApp]({url})")
        elif menu == "Global Stats": analytics.show_global_stats()

    else:
        # Shopkeeper Menu
        menu = st.sidebar.radio("MENU", [t['dash'], t['new_order'], t['reports'], t['security']])
        
        if menu == t['dash']:
            st.header(f"{t['dash']}: {st.session_state.u_shop}")
            stats = pd.read_sql(f"SELECT SUM(total) as t, SUM(advance) as a, SUM(remaining) as r FROM clients WHERE user_id={st.session_state.u_id}", conn)
            c1, c2, c3 = st.columns(3)
            c1.metric("Sales", f"Rs.{stats['t'].iloc[0] or 0:,.0f}")
            c2.metric("Cash", f"Rs.{stats['a'].iloc[0] or 0:,.0f}")
            c3.metric("Pending", f"Rs.{stats['r'].iloc[0] or 0:,.0f}")
            df = pd.read_sql(f"SELECT name, phone, remaining, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            st.dataframe(df, use_container_width=True)

        elif menu == t['new_order']:
            add_order_ui(st.session_state.u_id, t)

        elif menu == t['reports']:
            analytics.show_shop_reports(st.session_state.u_id)

        # --- UPDATED SECURITY SECTION WITH ACCOUNT DETAILS ---
        elif menu == t['security']:
            st.header(f"🔐 {t['security']} & Profile")
            
            # Fetch fresh user data
            u_data = conn.execute("SELECT shop_name, email, phone, fee_status, status FROM users WHERE id=?", (st.session_state.u_id,)).fetchone()
            
            st.markdown("### 📋 Account Details")
            col_a, col_b = st.columns(2)
            with col_a:
                st.info(f"**Shop Name:** {u_data[0]}")
                st.info(f"**Login Email:** {u_data[1]}")
                st.info(f"**Phone No:** {u_data[2] or 'N/A'}")
            with col_b:
                st.warning(f"**Account Status:** {u_data[4]}")
                st.error(f"**Payment Status:** {u_data[3]}")
                st.success("**Role:** Shop Owner (Admin)")

            st.markdown("---")
            st.markdown("### 🔑 Update Password")
            with st.form("pass_form"):
                new_p = st.text_input("New Password", type="password")
                conf_p = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Change Password"):
                    if new_p == conf_p and len(new_p) > 3:
                        conn.execute("UPDATE users SET password=? WHERE id=?", (new_p, st.session_state.u_id))
                        conn.commit()
                        st.success("✅ Password updated successfully!")
                    else: st.error("Passwords do not match or too short!")

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
