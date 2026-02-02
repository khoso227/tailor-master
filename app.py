import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui
import analytics

# Session Initialization
if 'auth' not in st.session_state: st.session_state.auth = False
if 'u_shop' not in st.session_state: st.session_state.u_shop = "Guest"
if 'u_id' not in st.session_state: st.session_state.u_id = 0
if 'u_role' not in st.session_state: st.session_state.u_role = ""

init_db()
conn = get_connection()

apply_styling('Dark')

if not st.session_state.auth:
    # --- LOGIN SCREEN ---
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>👔 Tailor Master Pro</h1>", unsafe_allow_html=True)
        e = st.text_input("Login Email").strip()
        p = st.text_input("Password", type="password").strip()
        if st.button("Unlock Dashboard"):
            user = conn.execute("SELECT id, role, shop_name, email FROM users WHERE email=? AND password=?", (e, p)).fetchone()
            if user:
                st.session_state.auth = True
                st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user
                st.rerun()
            else: st.error("Email ya Password ghalat hai!")
else:
    # --- LOGGED IN ---
    st.sidebar.markdown(f"## 🏬 {st.session_state.u_shop}")
    st.sidebar.markdown(f"**ROLE:** {st.session_state.u_role.upper()}")

    # --- 🌍 SUPER ADMIN VIEW ---
    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("SUPER ADMIN CONTROL", ["Global Stats", "Register New Shop", "Delete/Manage Shops"])
        
        if menu == "Global Stats":
            analytics.show_global_stats()
            
        elif menu == "Register New Shop":
            st.header("➕ Register New Partner Shop")
            with st.form("reg_form"):
                sn = st.text_input("Shop Name")
                se = st.text_input("Login Email")
                sp = st.text_input("Password")
                if st.form_submit_button("Create Account"):
                    try:
                        conn.execute("INSERT INTO users (email, password, shop_name, role) VALUES (?,?,?,?)", (se, sp, sn, 'admin'))
                        conn.commit()
                        st.success(f"Shop '{sn}' has been registered!")
                    except: st.error("Ye Email pehle se maujood hai!")

        elif menu == "Delete/Manage Shops":
            st.header("🗑️ Delete/Manage Registered Shops")
            shops_df = pd.read_sql("SELECT id, shop_name, email FROM users WHERE role='admin'", conn)
            st.dataframe(shops_df, use_container_width=True)
            
            del_id = st.number_input("Enter Shop ID to Delete", step=1, min_value=1)
            if st.button("❌ PERMANENTLY DELETE SHOP"):
                conn.execute(f"DELETE FROM users WHERE id={del_id}")
                conn.execute(f"DELETE FROM clients WHERE user_id={del_id}")
                conn.commit()
                st.warning(f"Shop ID {del_id} aur uske saare orders delete kar diye gaye hain!")
                st.rerun()

    # --- 🏠 SHOP KEEPER (ADMIN) VIEW ---
    else:
        menu = st.sidebar.radio("SHOP MENU", ["Dashboard", "New Order", "Reports", "Security"])
        
        if menu == "Dashboard":
            st.header(f"Dashboard: {st.session_state.u_shop}")
            # Quick Stats
            stats = pd.read_sql(f"SELECT SUM(total) as t, SUM(advance) as a, SUM(remaining) as r FROM clients WHERE user_id={st.session_state.u_id}", conn)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Sales", f"Rs.{stats['t'].iloc[0] or 0:,.0f}")
            c2.metric("Cash Received", f"Rs.{stats['a'].iloc[0] or 0:,.0f}")
            c3.metric("Outstanding", f"Rs.{stats['r'].iloc[0] or 0:,.0f}")
            
            st.markdown("---")
            orders = pd.read_sql(f"SELECT name, phone, remaining, pay_method, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            if not orders.empty:
                st.dataframe(orders, use_container_width=True)
            else:
                st.info("Abhi tak koi orders nahi hain.")

        elif menu == "New Order":
            add_order_ui(st.session_state.u_id)

        elif menu == "Reports":
            analytics.show_shop_reports(st.session_state.u_id)

        elif menu == "Security":
            st.header("🔐 Security & Profile")
            st.info(f"**Shop Name:** {st.session_state.u_shop}\n\n**Email:** {st.session_state.u_email}")
            with st.form("reset_p"):
                new_pass = st.text_input("Update Password", type="password")
                if st.form_submit_button("Save New Password"):
                    conn.execute(f"UPDATE users SET password='{new_pass}' WHERE id={st.session_state.u_id}")
                    conn.commit()
                    st.success("Password kamyabi se update ho gaya!")

    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Logout System"):
        st.session_state.auth = False
        st.rerun()
