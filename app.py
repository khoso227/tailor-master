import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from translations import get_text
from orders import add_order_ui
import analytics

# --- Session Management ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'reg_success' not in st.session_state: st.session_state.reg_success = False

init_db()
conn = get_connection()

# --- 🖼️ WALLPAPER OPTIONS ---
wallpapers = {
    "Default": None,
    "Classic Workshop": "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?q=80&w=1887",
    "Tailor Fabrics": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?q=80&w=2000",
    "Modern Studio": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=2070",
    "Sewing Aesthetic": "https://images.unsplash.com/photo-1528459801416-a9e53bbf4e17?q=80&w=1912"
}

# --- Sidebar Controls ---
st.sidebar.markdown("### 🎨 Customization")
wp_choice = st.sidebar.selectbox("Wallpaper / وال پیپر", list(wallpapers.keys()))
lang = st.sidebar.selectbox("🌐 Language", ["English", "Urdu"])
theme = st.sidebar.radio("☀️ Theme", ["🌙 Night Mode", "☀️ Day Mode"])

t = get_text(lang)
apply_styling(theme, lang, wallpapers[wp_choice])

# --- 🎉 Registration Success Pop-up ---
if st.session_state.reg_success:
    st.balloons()
    st.toast("🎉 Welcome to Tailor Master Pro! Your account is ready.")
    st.success("✅ Account Created Successfully! Please Login now.")
    st.session_state.reg_success = False # Reset

if not st.session_state.auth:
    st.markdown(f"<h1 style='text-align:center;'>👔 {t['title']}</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs([t['login'], t['register'], t['forgot']])
    
    with tab1: # Login
        le = st.text_input(t['email'], key="login_e").strip().lower()
        lp = st.text_input(t['pass'], type="password", key="login_p").strip()
        if st.button(t['login']):
            user = conn.execute("SELECT id, role, shop_name, email, status FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
            if user:
                if user[4] == 'Blocked': st.error("Account Blocked!")
                else:
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user[0], user[1], user[2], user[3]
                    st.rerun()
            else: st.error("Invalid Login!")

    with tab2: # Register
        st.subheader(t['register'])
        reg_sn = st.text_input(t['shop'])
        reg_ph = st.text_input(t['phone'])
        reg_e = st.text_input(t['email'], key="reg_e").strip().lower()
        reg_p = st.text_input(t['pass'], key="reg_p").strip()
        reg_sq = st.text_input(t['s_q'])
        reg_sa = st.text_input(t['s_a'])
        if st.button("Create My Account"):
            if reg_sn and reg_e and reg_p:
                try:
                    conn.execute("INSERT INTO users (email, password, shop_name, role, phone, security_q, security_a) VALUES (?,?,?,?,?,?,?)", 
                                 (reg_e, reg_p, reg_sn, 'admin', reg_ph, reg_sq, reg_sa))
                    conn.commit()
                    st.session_state.reg_success = True # Trigger Pop-up
                    st.rerun()
                except: st.error("Email already exists!")
            else: st.warning("Please fill all fields!")

    with tab3: # Forgot
        fe = st.text_input("Reset Email").strip().lower()
        if fe:
            f_user = conn.execute("SELECT security_q, security_a, password FROM users WHERE LOWER(email)=?", (fe,)).fetchone()
            if f_user:
                st.info(f"Question: {f_user[0]}")
                ans = st.text_input("Answer")
                if st.button("Show Password"):
                    if ans == f_user[1]: st.success(f"Password: {f_user[2]}")
                    else: st.error("Wrong Answer!")
else:
    # --- LOGGED IN DASHBOARD ---
    st.sidebar.markdown(f"### 🏬 {st.session_state.u_shop}")
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

    elif menu == t['security']:
        st.header("🔐 Account & Security")
        u_data = conn.execute("SELECT shop_name, email, phone, fee_status FROM users WHERE id=?", (st.session_state.u_id,)).fetchone()
        st.info(f"**Shop:** {u_data[0]} | **Email:** {u_data[1]} | **Phone:** {u_data[2]} | **Status:** {u_data[3]}")

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
