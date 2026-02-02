import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui

# Initialize
init_db()
conn = get_connection()

# Auth States
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'shop_name' not in st.session_state: st.session_state.shop_name = ""

apply_styling("Sahil & Arman Platform")

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.subheader("🔐 Enterprise Login")
        email = st.text_input("Email Address")
        pwd = st.text_input("Password", type="password")
        
        if st.button("Sign In"):
            user = conn.execute("SELECT id, role, shop_name FROM users WHERE email=? AND password=?", (email, pwd)).fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.user_role = user[1]
                st.session_state.shop_name = user[2]
                st.rerun()
            else: st.error("Invalid Email or Password!")
        st.info("💡 Hint: admin@sahilarman.com / sahilarman2026")

# --- LOGGED IN AREA ---
else:
    st.sidebar.title(f"👔 {st.session_state.shop_name}")
    
    # 👑 SUPER ADMIN MENU
    if st.session_state.user_role == "super_admin":
        menu = st.sidebar.selectbox("🚀 SUPER ADMIN PANEL", ["🌍 Global Dashboard", "➕ Register New Shop", "👥 All Registered Shops"])

        if menu == "🌍 Global Dashboard":
            st.subheader("🌎 Global Platform Overview")
            # Logic here... (same as before)

        elif menu == "👥 All Registered Shops":
            # Logic here... (same as before)
            st.subheader("Registered Shops")
            shops = pd.read_sql("SELECT id, shop_name, email FROM users WHERE role='admin'", conn)
            st.dataframe(shops)

        elif menu == "➕ Register New Shop":
            st.subheader("📝 Register New Shop")
            with st.form("reg"):
                sn = st.text_input("Shop Name"); se = st.text_input("Email"); sp = st.text_input("Initial Password")
                if st.form_submit_button("Create Account"):
                    conn.execute("INSERT INTO users (email, password, shop_name, role) VALUES (?,?,?,?)", (se, sp, sn, 'admin'))
                    conn.commit(); st.success("Account Created!")

    # 👔 SHOP ADMIN (LOCAL ADMIN) MENU
    else:
        menu = st.sidebar.selectbox("Shop Menu", ["🏠 My Dashboard", "📏 New Order", "📊 Analytics", "🔐 Security Settings"])

        if menu == "🏠 My Dashboard":
            st.subheader(f"Dashboard - {st.session_state.shop_name}")
            df = pd.read_sql(f"SELECT name, phone, total, remaining, status FROM clients WHERE user_id={st.session_state.user_id}", conn)
            st.dataframe(df, use_container_width=True)

        elif menu == "📏 New Order":
            labels = ["Length", "Sleeves", "Shoulder", "Collar", "Chest", "Waist", "Hip", "Bottom"]
            add_order_ui(labels, st.session_state.user_id)

        # NEW FEATURE: CHANGE PASSWORD FOR SHOP KEEPERS
        elif menu == "🔐 Security Settings":
            st.subheader("🔐 Change Your Password")
            st.warning("Apna password kisi ko mat batayein.")
            with st.form("change_pass"):
                new_p = st.text_input("Enter New Password", type="password")
                confirm_p = st.text_input("Confirm New Password", type="password")
                if st.form_submit_button("Update Password"):
                    if new_p == confirm_p and len(new_p) > 3:
                        conn.execute(f"UPDATE users SET password='{new_p}' WHERE id={st.session_state.user_id}")
                        conn.commit()
                        st.success("Password updated successfully!")
                    else: st.error("Passwords do not match or too short!")

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
