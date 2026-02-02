import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from translations import get_text
from orders import add_order_ui
import analytics

# --- Session Initialization ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'u_id' not in st.session_state: st.session_state.u_id = 0
if 'u_shop' not in st.session_state: st.session_state.u_shop = ""
if 'u_role' not in st.session_state: st.session_state.u_role = ""

init_db()
conn = get_connection()

# --- Sidebar Settings ---
lang = st.sidebar.selectbox("🌐 Language", ["English", "Urdu"])
theme = st.sidebar.radio("🎨 Theme", ["🌙 Night Mode", "☀️ Day Mode"])
t = get_text(lang)
apply_styling(theme, lang)

if not st.session_state.auth:
    # --- LOGIN / REGISTER / FORGOT TABS ---
    st.markdown(f"<h1 style='text-align:center;'>👔 {t['title']}</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs([t['login'], t['register'], t['forgot']])
    
    with tab1: # LOGIN
        le = st.text_input(t['email'], key="login_e").strip().lower()
        lp = st.text_input(t['pass'], type="password", key="login_p").strip()
        if st.button(t['login'], key="login_btn"):
            user = conn.execute("SELECT id, role, shop_name, email, status FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
            if user:
                if user[4] == 'Blocked': st.error("Account Blocked!")
                else:
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user[0], user[1], user[2], user[3]
                    st.rerun()
            else: st.error("Wrong Details!")

    with tab2: # REGISTER
        st.subheader(t['register'])
        reg_sn = st.text_input(t['shop'])
        reg_e = st.text_input(t['email'], key="reg_e").strip().lower()
        reg_p = st.text_input(t['pass'], key="reg_p").strip()
        reg_sq = st.text_input(t['s_q'])
        reg_sa = st.text_input(t['s_a'])
        if st.button("Register My Shop"):
            try:
                conn.execute("INSERT INTO users (email, password, shop_name, role, security_q, security_a) VALUES (?,?,?,?,?,?)", (reg_e, reg_p, reg_sn, 'admin', reg_sq, reg_sa))
                conn.commit(); st.success("Success! Now Login.")
            except: st.error("Email already exists!")

    with tab3: # FORGOT
        fe = st.text_input("Recovery Email").strip().lower()
        if fe:
            f_user = conn.execute("SELECT security_q, security_a, password FROM users WHERE LOWER(email)=?", (fe,)).fetchone()
            if f_user:
                st.info(f"Question: {f_user[0]}")
                ans = st.text_input("Answer")
                if st.button("Recover"):
                    if ans == f_user[1]: st.success(f"Password: {f_user[2]}")
                    else: st.error("Wrong Answer!")
else:
    # --- LOGGED IN AREA ---
    st.sidebar.markdown(f"### 🏬 {st.session_state.u_shop}")
    
    # Super Admin Logic
    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("ADMIN MENU", ["Shop Payments", "Global Stats"])
        if menu == "Shop Payments":
            import urllib.parse
            st.header("Partner Management")
            shops = pd.read_sql("SELECT id, shop_name, email, fee_status FROM users WHERE role='admin'", conn)
            st.dataframe(shops, use_container_width=True)
            sel_id = st.number_input("Shop ID", step=1)
            if st.button("Send Reminder"):
                s_data = conn.execute("SELECT shop_name FROM users WHERE id=?", (sel_id,)).fetchone()
                msg = f"Payment Reminder for {s_data[0]}."
                st.markdown(f"[Send WhatsApp](https://wa.me/?text={urllib.parse.quote(msg)})")
        elif menu == "Global Stats":
            analytics.show_global_stats()
            
    # Shopkeeper Logic (Fixing the NameError here)
    else:
        # Defining 'menu' variable correctly for Shopkeepers
        menu = st.sidebar.radio("MENU", ["Dashboard", "New Order", "Reports", "Security"])
        
        if menu == "Dashboard":
            st.header(f"Orders for {st.session_state.u_shop}")
            # Summary Metrics
            stats = pd.read_sql(f"SELECT SUM(total) as t, SUM(advance) as a, SUM(remaining) as r FROM clients WHERE user_id={st.session_state.u_id}", conn)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Sales", f"Rs.{stats['t'].iloc[0] or 0:,.0f}")
            c2.metric("Received", f"Rs.{stats['a'].iloc[0] or 0:,.0f}")
            c3.metric("Outstanding", f"Rs.{stats['r'].iloc[0] or 0:,.0f}")
            
            st.markdown("---")
            df = pd.read_sql(f"SELECT name, phone, remaining, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            if not df.empty: st.dataframe(df, use_container_width=True)
            else: st.info("No data found.")

        elif menu == "New Order":
            # Passing the correct language dictionary 't'
            add_order_ui(st.session_state.u_id, t)
            
        elif menu == "Reports":
            analytics.show_shop_reports(st.session_state.u_id)

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
