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

if not st.session_state.auth:
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
