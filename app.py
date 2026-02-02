import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui

# Initialize
init_db()
conn = get_connection()

# --- Auth State ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None
if 'user_id' not in st.session_state: st.session_state.user_id = None

apply_styling("Sahil & Arman Platform")

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register New Shop"])
    
    with tab1:
        st.subheader("Login to your Shop")
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
            else: st.error("Invalid Email or Password")

    with tab2:
        st.subheader("Create New Account")
        new_shop = st.text_input("Shop Name")
        new_email = st.text_input("Your Email")
        new_pwd = st.text_input("Choose Password", type="password")
        if st.button("Register & Create Shop"):
            try:
                conn.execute("INSERT INTO users (email, password, shop_name, role) VALUES (?,?,?,?)", 
                             (new_email, new_pwd, new_shop, 'admin'))
                conn.commit()
                st.success("Account Created! Please Login.")
            except: st.error("Email already exists!")

else:
    # --- LOGGED IN AREA ---
    st.sidebar.title(f"👔 {st.session_state.shop_name}")
    st.sidebar.info(f"Role: {st.session_state.user_role.upper()}")

    if st.session_state.user_role == "super_admin":
        menu = st.sidebar.selectbox("🚀 SUPER ADMIN MENU", ["🌍 All Shops Analytics", "👥 Manage Users", "⚙️ System Logs"])
        
        if menu == "🌍 All Shops Analytics":
            st.subheader("Global Platform Reports")
            all_users = pd.read_sql("SELECT id, email, shop_name, role FROM users", conn)
            st.write("### Registered Shops")
            st.dataframe(all_users)
            
            total_rev = pd.read_sql("SELECT SUM(total) FROM clients", conn).iloc[0,0]
            st.metric("Total Platform Revenue", f"Rs.{total_rev or 0}")

    else:
        # Normal Shop Admin Menu
        menu = st.sidebar.selectbox("Shop Menu", ["🏠 Dashboard", "📏 New Order", "📊 Analytics", "👥 Staff"])

        if menu == "🏠 Dashboard":
            st.subheader(f"Dashboard - {st.session_state.shop_name}")
            # Filter data by user_id
            df = pd.read_sql(f"SELECT * FROM clients WHERE user_id={st.session_state.user_id}", conn)
            st.dataframe(df)

        elif menu == "📏 New Order":
            # Pass user_id to add_order function
            st.info("Adding order for your shop...")
            add_order_ui(['Length', 'Shoulder', 'Chest', 'Waist'], st.session_state.user_id)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
