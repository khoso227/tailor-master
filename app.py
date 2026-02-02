import streamlit as st
import pandas as pd
from database import get_connection
from translations import TRANSLATIONS
from styling import apply_style
from measurment import show_order_form

conn = get_connection()
if 'lang' not in st.session_state: st.session_state.lang = "English"
ln = TRANSLATIONS[st.session_state.lang]

apply_style(ln) # Styling & Wallpapers

if 'auth' not in st.session_state: st.session_state.auth = False
st.markdown('<div class="main-container">', unsafe_allow_html=True)

if not st.session_state.auth:# --- 4. AUTH & VIEW STATE ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'view' not in st.session_state: st.session_state.view = "login"

st.markdown('<div class="main-container">', unsafe_allow_html=True)

if not st.session_state.auth:
    # --- 🟢 LOGIN VIEW ---
    if st.session_state.view == "login":
        st.title(ln['title'])
        le = st.text_input(ln['email'], key="l_e").strip().lower()
        lp = st.text_input(ln['pass'], type="password", key="l_p").strip()
        
        c1, c2 = st.columns(2)
        if c1.button(ln['login_btn'], use_container_width=True):
            user = conn.execute("SELECT id, role, shop_name FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
            if user:
                st.session_state.auth, st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = True, user[0], user[1], user[2]
                st.rerun()
            else: st.error("❌ Invalid Login!")
            
        if c2.button(ln['reg_btn'], use_container_width=True):
            st.session_state.view = "register"
            st.rerun()
            
        if st.button(ln['forgot_btn'], variant="ghost"):
            st.session_state.view = "forgot"
            st.rerun()

    # --- 🟡 REGISTER VIEW (New Shop) ---
    elif st.session_state.view == "register":
        st.title(ln['reg_btn'])
        r_sn = st.text_input(ln['shop'], placeholder="Enter Shop Name")
        r_ph = st.text_input(ln['phone'], placeholder="Mobile Number")
        r_e = st.text_input(ln['email'], key="r_e").strip().lower()
        r_p = st.text_input(ln['pass'], key="r_p", type="password")
        r_sq = st.text_input(ln['s_q'], placeholder="e.g. Best Friend Name?")
        r_sa = st.text_input(ln['s_a'], placeholder="Answer")

        cr1, cr2 = st.columns(2)
        if cr1.button("Create Account ✅", use_container_width=True):
            if r_sn and r_e and r_p:
                try:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO users (email, password, shop_name, role, phone, security_q, security_a) VALUES (?,?,?,?,?,?,?)", 
                                 (r_e, r_p, r_sn, 'admin', r_ph, r_sq, r_sa))
                    conn.commit()
                    # Auto Login after registration
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = cur.lastrowid, 'admin', r_sn
                    st.success("Account Created! Redirecting...")
                    st.rerun()
                except Exception as e:
                    st.error("⚠️ Email already exists or Database Error!")
            else:
                st.warning("Please fill all essential fields (Shop Name, Email, Password)")

        if cr2.button("← Back to Login", use_container_width=True):
            st.session_state.view = "login"
            st.rerun()

    # --- 🔴 FORGOT PASSWORD VIEW ---
    elif st.session_state.view == "forgot":
        st.title(ln['forgot_btn'])
        fe = st.text_input("Enter Recovery Email").strip().lower()
        if fe:
            u = conn.execute("SELECT security_q, security_a, password FROM users WHERE LOWER(email)=?", (fe,)).fetchone()
            if u:
                st.info(f"Question: {u[0]}")
                ans = st.text_input("Your Answer")
                if st.button("Recover Password"):
                    if ans.lower() == u[1].lower(): st.success(f"Password: {u[2]}")
                    else: st.error("Wrong Answer!")
        if st.button("← Back"):
            st.session_state.view = "login"
            st.rerun()
    # Login Logic
    st.title(ln['title'])
    le = st.text_input(ln['email']).strip().lower()
    lp = st.text_input(ln['pass'], type="password").strip()
    if st.button(ln['login_btn']):
        user = conn.execute("SELECT id, role, shop_name FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
        if user:
            st.session_state.auth, st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = True, user[0], user[1], user[2]
            st.rerun()
        else: st.error("Invalid Details!")
    if st.button(ln['reg_btn']): st.info("Registration logic is modular. Click to start.")
else:
    with st.sidebar:
        st.markdown(f"🏪 **{st.session_state.u_shop}**")
        menu = st.radio("Navigation", [ln['dash'], ln['order'], ln['report'], ln['sec']])
        if st.button(ln['logout']): st.session_state.auth = False; st.rerun()

    if menu == ln['order']:
        show_order_form(conn, ln)
    elif menu == ln['dash'] or menu == ln['report']:
        st.header(menu)
        df = pd.read_sql(f"SELECT client_name, client_phone, total_bill, order_date, status FROM orders WHERE user_id={st.session_state.u_id}", conn)
        st.dataframe(df, use_container_width=True)
    elif menu == ln['sec']:
        st.header(ln['sec'])
        new_sn = st.text_input(ln['rename'], value=st.session_state.u_shop)
        if st.button(ln['update']):
            conn.execute("UPDATE users SET shop_name=? WHERE id=?", (new_sn, st.session_state.u_id))
            conn.commit()
            st.session_state.u_shop = new_sn
            st.success("Shop Renamed! ✅")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

