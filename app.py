import streamlit as st
import pandas as pd
import urllib.parse
from database import init_db, get_connection
from styling import apply_styling
from translations import get_text
from orders import add_order_ui
import analytics

if 'auth' not in st.session_state: st.session_state.auth = False

init_db()
conn = get_connection()
lang = st.sidebar.selectbox("🌐 Language", ["English", "Urdu"])
theme = st.sidebar.radio("🎨 Theme", ["🌙 Night Mode", "☀️ Day Mode"])
t = get_text(lang)
apply_styling(theme, lang)

if not st.session_state.auth:
    tab1, tab2, tab3 = st.tabs([t['login'], t['register'], t['forgot']])
    
    with tab1: # LOGIN
        e = st.text_input(t['email'], key="le").strip().lower()
        p = st.text_input(t['pass'], type="password", key="lp")
        if st.button(t['login']):
            user = conn.execute("SELECT id, role, shop_name, email, status FROM users WHERE LOWER(email)=? AND password=?", (e, p)).fetchone()
            if user:
                if user[4] == 'Blocked': st.error("Account Blocked!")
                else:
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user[0], user[1], user[2], user[3]
                    st.rerun()
            else: st.error("Wrong Details!")

    with tab2: # REGISTER (New Phone Input Added)
        st.subheader(t['register'])
        sn = st.text_input(t['shop'])
        sph = st.text_input(t['phone']) # Mobile number mangne ka option
        re = st.text_input(t['email'], key="re").strip().lower()
        rp = st.text_input(t['pass'], type="password", key="rp")
        sq = st.text_input(t['s_q'])
        sa = st.text_input(t['s_a'])
        if st.button("Create My Account"):
            try:
                conn.execute("INSERT INTO users (email, password, shop_name, role, phone, security_q, security_a) VALUES (?,?,?,?,?,?,?)", (re, rp, sn, 'admin', sph, sq, sa))
                conn.commit(); st.success("Account Created! Now Login.")
            except: st.error("Error! Email may exist.")

    with tab3: # FORGOT
        fe = st.text_input("Recovery Email").strip().lower()
        # ... Forgot password logic same ...
else:
    # --- LOGGED IN ---
    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("ADMIN", ["Shop Payments", "Global Stats"])
        if menu == "Shop Payments":
            st.header("💳 Partner Shops & Payments")
            # Phone number ab Super Admin ko nazar ayega
            shops = pd.read_sql("SELECT id, shop_name, phone, email, fee_status, status FROM users WHERE role='admin'", conn)
            st.dataframe(shops, use_container_width=True)
            
            sel_id = st.number_input("Enter Shop ID to Manage", step=1)
            if st.button("🔔 Send WhatsApp Reminder"):
                s_data = conn.execute("SELECT phone, shop_name FROM users WHERE id=?", (sel_id,)).fetchone()
                if s_data and s_data[0]:
                    msg = f"Dear {s_data[1]}, your payment for Tailor Master Pro is pending. Contact Sahil & Arman IT Solutions."
                    url = f"https://wa.me/{s_data[0]}?text={urllib.parse.quote(msg)}"
                    st.markdown(f"[Click to Message: {s_data[0]}]({url})")
                else: st.error("Mobile number not found!")
            # ... Block/Delete logic ...
    else:
        # Shopkeeper Dashboard
        menu = st.sidebar.radio("MENU", ["Dashboard", "New Order", "Reports", "Security"])
        if menu == "Dashboard":
            st.header(f"Orders: {st.session_state.u_shop}")
            # Dashboard Error Fix: Sahi columns select kiye gaye hain v13 database se
            df = pd.read_sql(f"SELECT name, phone, remaining, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            st.dataframe(df, use_container_width=True)
        elif menu == "New Order":
            add_order_ui(st.session_state.u_id, t)
    
    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()
