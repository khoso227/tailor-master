import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui
import analytics

init_db()
conn = get_connection()

# Theme Logic
if 'theme' not in st.session_state: st.session_state.theme = 'Dark'
if 'auth' not in st.session_state: st.session_state.auth = False

# Sidebar Theme Toggle
theme_choice = st.sidebar.toggle("🌙 Night Mode", value=True)
st.session_state.theme = 'Dark' if theme_choice else 'Light'

apply_styling(st.session_state.theme)

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h2 style='text-align:center;'>👔 Tailor Master ERP</h2>", unsafe_allow_html=True)
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            user = conn.execute("SELECT id, role, shop_name FROM users WHERE email=? AND password=?", (email, pwd)).fetchone()
            if user:
                st.session_state.auth = True
                st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = user
                st.rerun()
            else: st.error("Wrong Credentials")
else:
    st.sidebar.title(st.session_state.u_shop)
    
    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("SUPER ADMIN", ["Global Stats", "Manage Shops", "Platform Settings"])
        if menu == "Global Stats":
            analytics.show_global_stats()
        elif menu == "Manage Shops":
            st.subheader("Registered Shops")
            shops = pd.read_sql("SELECT id, shop_name, email, fee_status FROM users WHERE role='admin'", conn)
            st.dataframe(shops)
            with st.expander("Update Shop Fee Status"):
                sid = st.number_input("Shop ID", step=1)
                status = st.selectbox("Status", ["Paid", "Unpaid"])
                if st.button("Update Status"):
                    conn.execute(f"UPDATE users SET fee_status='{status}' WHERE id={sid}")
                    conn.commit(); st.success("Updated!")

    else:
        menu = st.sidebar.radio("MENU", ["🏠 Dashboard", "📏 New Order", "📊 My Reports", "🔐 Security"])
        
        if menu == "🏠 Dashboard":
            st.subheader("My Shop Records")
            df = pd.read_sql(f"SELECT name, phone, total, remaining, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            st.dataframe(df, use_container_width=True)
            
        elif menu == "📏 New Order":
            add_order_ui(["Length", "Sleeves", "Shoulder", "Collar", "Chest", "Waist", "Hip", "Bottom"], st.session_state.u_id)

        elif menu == "📊 My Reports":
            analytics.show_shop_reports(st.session_state.u_id)

        elif menu == "🔐 Security":
            st.subheader("Change Password")
            new_p = st.text_input("New Password", type="password")
            if st.button("Update"):
                conn.execute(f"UPDATE users SET password='{new_p}' WHERE id={st.session_state.u_id}")
                conn.commit(); st.success("Password Changed!")

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
