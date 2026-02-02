import streamlit as st
import pandas as pd
import urllib.parse
from database import init_db, get_connection
from styling import apply_styling
from translations import get_text  # Yeh line 6 hai
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
        e = st.text_input(t['email'], key="le")
        p = st.text_input(t['pass'], type="password", key="lp")
        if st.button(t['login']):
            user = conn.execute("SELECT id, role, shop_name, email, status FROM users WHERE email=? AND password=?", (e, p)).fetchone()
            if user:
                if user[4] == 'Blocked': st.error("Your account is Blocked! Contact Admin.")
                else:
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user[0], user[1], user[2], user[3]
                    st.rerun()
            else: st.error("Wrong Details!")

    with tab2: # REGISTER
        st.subheader(t['register'])
        sn = st.text_input(t['shop'])
        re = st.text_input(t['email'], key="re")
        rp = st.text_input(t['pass'], type="password", key="rp")
        sq = st.text_input(t['s_q'])
        sa = st.text_input(t['s_a'])
        if st.button("Create My Shop"):
            try:
                conn.execute("INSERT INTO users (email, password, shop_name, role, security_q, security_a) VALUES (?,?,?,?,?,?)", (re, rp, sn, 'admin', sq, sa))
                conn.commit(); st.success("Account Created! Now Login.")
            except: st.error("Email already exists!")

    with tab3: # FORGOT PASSWORD
        fe = st.text_input("Enter Email to Reset")
        f_user = conn.execute("SELECT security_q, security_a, password FROM users WHERE email=?", (fe,)).fetchone()
        if f_user:
            st.info(f"Question: {f_user[0]}")
            ans = st.text_input("Your Answer")
            if st.button("Show My Password"):
                if ans == f_user[1]: st.success(f"Your Password is: {f_user[2]}")
                else: st.error("Wrong Answer!")
else:
    # --- LOGGED IN ---
    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("ADMIN", ["Shop Payments", "Global Stats"])
        if menu == "Shop Payments":
            st.header("💳 Partner Shops & Payments")
            shops = pd.read_sql("SELECT id, shop_name, email, fee_status, status FROM users WHERE role='admin'", conn)
            st.dataframe(shops, use_container_width=True)
            
            sel_id = st.number_input("Enter Shop ID to Manage", step=1)
            c1, c2, c3 = st.columns(3)
            if c1.button("🔔 Send WhatsApp Reminder"):
                s_data = conn.execute("SELECT email, shop_name FROM users WHERE id=?", (sel_id,)).fetchone()
                msg = f"Dear {s_data[1]}, your payment for Tailor Master Pro is pending. Please pay within 24 hours to avoid deletion."
                url = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                st.markdown(f"[Click to Send Reminder on WhatsApp]({url})")
            
            if c2.button("🚫 Block Shop"):
                conn.execute(f"UPDATE users SET status='Blocked' WHERE id={sel_id}")
                conn.commit(); st.warning("Shop Blocked!"); st.rerun()
                
            if c3.button("🗑️ DELETE SHOP PERMANENTLY"):
                conn.execute(f"DELETE FROM users WHERE id={sel_id}")
                conn.commit(); st.error("Shop Deleted!"); st.rerun()
    else:
        # Shopkeeper Dashboard (Same as before)
        st.sidebar.write(f"Welcome {st.session_state.u_shop}")
        menu = st.sidebar.radio("MENU", ["Dashboard", "New Order"])
        if menu == "New Order": add_order_ui(st.session_state.u_id, t)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()

