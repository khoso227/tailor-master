import streamlit as st
import pandas as pd
import urllib.parse
from database import init_db, get_connection
from styling import apply_styling
from translations import get_text
from orders import add_order_ui
import analytics

# --- 1. Session Initialization (Sari settings ek saath) ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'view' not in st.session_state: st.session_state.view = "login"
if 'reg_success' not in st.session_state: st.session_state.reg_success = False
if 'u_id' not in st.session_state: st.session_state.u_id = 0
if 'u_shop' not in st.session_state: st.session_state.u_shop = ""
if 'u_role' not in st.session_state: st.session_state.u_role = ""

init_db()
conn = get_connection()

# --- 2. 🖼️ Dynamic Wallpapers (5 Day, 5 Night) ---
day_wallpapers = {
    "Bright Studio": "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?q=80&w=1887",
    "Luxury Silk": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?q=80&w=2000",
    "Vintage Sewing": "https://images.unsplash.com/photo-1528459801416-a9e53bbf4e17?q=80&w=1912",
    "Minimalist Workshop": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=2070",
    "Pastel Fabrics": "https://images.unsplash.com/photo-1520032484190-e5ef81d87978?q=80&w=2070"
}

night_wallpapers = {
    "Midnight Blue": "https://images.unsplash.com/photo-1517420704952-d9f39e95b43e?q=80&w=2070",
    "Neon Workshop": "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?q=80&w=2070",
    "Dark Wood Antique": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?q=80&w=2069",
    "Moody Tailoring": "https://images.unsplash.com/photo-1489743342057-3448cc7c3bb9?q=80&w=2070",
    "Graphite Tools": "https://images.unsplash.com/photo-1505330622279-bf7d7fc918f4?q=80&w=2070"
}

# --- 3. Sidebar Customization ---
st.sidebar.markdown("### 🎨 Customization")
lang = st.sidebar.selectbox("🌐 Language", ["English", "Urdu"])
theme = st.sidebar.radio("☀️ Theme Mode", ["🌙 Night Mode", "☀️ Day Mode"])

# Wallpaper selection based on theme
wp_list = night_wallpapers if theme == "🌙 Night Mode" else day_wallpapers
wp_choice = st.sidebar.selectbox("Select Wallpaper / وال پیپر", list(wp_list.keys()))

t = get_text(lang)
apply_styling(theme, lang, wp_list[wp_choice])

# --- 4. 🎉 Registration Success Pop-up ---
if st.session_state.reg_success:
    st.balloons()
    st.toast(f"🎉 Welcome to {st.session_state.u_shop}!")
    st.session_state.reg_success = False

# --- 5. 🔓 MAIN LOGIC (Login / Registration / Dashboard) ---
if not st.session_state.auth:
    st.markdown(f"<h1 style='text-align:center;'>👔 {t['title']}</h1>", unsafe_allow_html=True)
    
    # 🟢 LOGIN VIEW
    if st.session_state.view == "login":
        st.subheader(t['login'])
        le = st.text_input(t['email'], key="l_e").strip().lower()
        lp = st.text_input(t['pass'], type="password", key="l_p").strip()
        
        c_l1, c_l2 = st.columns([1, 4])
        if c_l1.button(t['login']):
            user = conn.execute("SELECT id, role, shop_name, email, status FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
            if user:
                if user[4] == 'Blocked': st.error("Account Blocked! Contact Sahil & Arman IT Solutions.")
                else:
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user[0], user[1], user[2], user[3]
                    st.rerun()
            else: st.error("Invalid Details!")
        
        st.markdown("---")
        c_alt1, c_alt2 = st.columns(2)
        if c_alt1.button(t['register']): st.session_state.view = "register"; st.rerun()
        if c_alt2.button(t['forgot']): st.session_state.view = "forgot"; st.rerun()

    # 🟡 REGISTER VIEW (Direct Login Enabled)
    elif st.session_state.view == "register":
        st.subheader(t['register'])
        reg_sn = st.text_input(t['shop'])
        reg_ph = st.text_input(t['phone'])
        reg_e = st.text_input(t['email'], key="r_e").strip().lower()
        reg_p = st.text_input(t['pass'], key="r_p").strip()
        reg_sq = st.text_input(t['s_q'])
        reg_sa = st.text_input(t['s_a'])
        
        c_r1, c_r2 = st.columns([1, 4])
        if c_r1.button("Create Account & Enter"):
            if reg_sn and reg_e and reg_p:
                try:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO users (email, password, shop_name, role, phone, security_q, security_a) VALUES (?,?,?,?,?,?,?)", 
                                 (reg_e, reg_p, reg_sn, 'admin', reg_ph, reg_sq, reg_sa))
                    conn.commit()
                    
                    # 🔥 Auto Login Logic
                    st.session_state.auth = True
                    st.session_state.u_id = cur.lastrowid
                    st.session_state.u_role = 'admin'
                    st.session_state.u_shop = reg_sn
                    st.session_state.u_email = reg_e
                    st.session_state.reg_success = True
                    st.rerun()
                except: st.error("Email already exists!")
            else: st.warning("Please fill essential fields (Shop Name, Email, Password)")
        
        if c_r2.button("← Back to Login"): st.session_state.view = "login"; st.rerun()

    # 🔴 FORGOT PASSWORD VIEW
    elif st.session_state.view == "forgot":
        st.subheader(t['forgot'])
        fe = st.text_input("Recovery Email").strip().lower()
        if fe:
            f_user = conn.execute("SELECT security_q, security_a, password FROM users WHERE LOWER(email)=?", (fe,)).fetchone()
            if f_user:
                st.info(f"Question: {f_user[0]}")
                ans = st.text_input("Your Answer")
                if st.button("Recover Password"):
                    if ans == f_user[1]: st.success(f"Your Password is: {f_user[2]}")
                    else: st.error("Wrong Answer!")
            else: st.error("Email not found.")
        
        if st.button("← Back to Login"): st.session_state.view = "login"; st.rerun()

else:
    # --- 🏠 LOGGED IN DASHBOARD ---
    st.sidebar.markdown(f"### 🏬 {st.session_state.u_shop}")
    
    # Super Admin vs Shopkeeper Menus
    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("ADMIN PANEL", ["Partner Payments", "Global Stats"])
        if menu == "Partner Payments":
            st.header("💳 Partner Management")
            shops = pd.read_sql("SELECT id, shop_name, phone, fee_status FROM users WHERE role='admin'", conn)
            st.dataframe(shops, use_container_width=True)
            sid = st.number_input("Shop ID", step=1)
            if st.button("Send Reminder Link"):
                s_data = conn.execute("SELECT shop_name, phone FROM users WHERE id=?", (sid,)).fetchone()
                msg = f"Reminder: Payment for {s_data[0]} is due."
                url = f"https://wa.me/{s_data[1]}?text={urllib.parse.quote(msg)}"
                st.markdown(f"[Send WhatsApp Reminder]({url})")
        elif menu == "Global Stats": analytics.show_global_stats()
    
    else:
        # Shopkeeper Menus
        menu = st.sidebar.radio("MENU", [t['dash'], t['new_order'], t['reports'], t['security']])
        
        if menu == t['dash']:
            st.header(f"{t['dash']}: {st.session_state.u_shop}")
            stats = pd.read_sql(f"SELECT SUM(total) as t, SUM(advance) as a, SUM(remaining) as r FROM clients WHERE user_id={st.session_state.u_id}", conn)
            c1, c2, c3 = st.columns(3)
            c1.metric("Sales", f"Rs.{stats['t'].iloc[0] or 0:,.0f}")
            c2.metric("Received", f"Rs.{stats['a'].iloc[0] or 0:,.0f}")
            c3.metric("Outstanding", f"Rs.{stats['r'].iloc[0] or 0:,.0f}")
            df = pd.read_sql(f"SELECT name, phone, remaining, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            st.dataframe(df, use_container_width=True)

        elif menu == t['new_order']:
            add_order_ui(st.session_state.u_id, t)

        elif menu == t['reports']:
            analytics.show_shop_reports(st.session_state.u_id)

        elif menu == t['security']:
            st.header(f"🔐 {t['security']}")
            u_data = conn.execute("SELECT shop_name, email, phone, fee_status FROM users WHERE id=?", (st.session_state.u_id,)).fetchone()
            st.markdown(f"**Shop:** {u_data[0]}  \n**Email:** {u_data[1]}  \n**Phone:** {u_data[2]}  \n**Status:** {u_data[3]}")
            # Password reset logic can go here

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.session_state.view = "login"
        st.rerun()
