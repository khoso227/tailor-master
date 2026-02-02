import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui
import analytics

# --- SESSION FIX (Khatam AttributeError) ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'u_shop' not in st.session_state: st.session_state.u_shop = "Guest"
if 'u_email' not in st.session_state: st.session_state.u_email = ""
if 'u_id' not in st.session_state: st.session_state.u_id = 0
if 'u_role' not in st.session_state: st.session_state.u_role = ""

init_db()
conn = get_connection()

theme_choice = st.sidebar.toggle("🌙 Night Mode", value=True)
apply_styling('Dark' if theme_choice else 'Light')

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>👔 Tailor Master Pro</h1>", unsafe_allow_html=True)
        e = st.text_input("Email").strip()
        p = st.text_input("Password", type="password").strip()
        if st.button("Access Dashboard"):
            user = conn.execute("SELECT id, role, shop_name, email FROM users WHERE email=? AND password=?", (e, p)).fetchone()
            if user:
                st.session_state.auth = True
                st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user
                st.rerun()
            else: st.error("Wrong Details!")
else:
    # --- Professional Sidebar with Icons ---
    st.sidebar.markdown(f"## 🏬 {st.session_state.u_shop}")
    
    if st.session_state.u_role == "super_admin":
        menu = st.sidebar.radio("CONTROL PANEL", ["🌍 Global Stats", "➕ Register Shop", "🗑️ Delete Shop"])
        if menu == "🌍 Global Stats": analytics.show_global_stats()
        elif menu == "🗑️ Delete Shop":
            st.header("Manage Shops")
            df = pd.read_sql("SELECT id, shop_name, email FROM users WHERE role='admin'", conn)
            st.dataframe(df, use_container_width=True)
            did = st.number_input("Shop ID to Delete", step=1)
            if st.button("Confirm Delete"):
                conn.execute(f"DELETE FROM users WHERE id={did}")
                conn.commit(); st.rerun()
    else:
        menu = st.sidebar.radio("SHOP MENU", ["🏠 Dashboard", "📏 New Order", "📊 Reports", "🔐 Security"])
        
        if menu == "🏠 Dashboard":
            st.header(f"Orders for {st.session_state.u_shop}")
            # Hisab Kitab metrics yahan payment methods ke sath show honge
            df = pd.read_sql(f"SELECT name, phone, remaining, pay_method, status FROM clients WHERE user_id={st.session_state.u_id}", conn)
            st.dataframe(df, use_container_width=True)
            
        elif menu == "📏 New Order":
            add_order_ui(["Length", "Sleeves", "Shoulder", "Collar", "Chest", "Waist", "Hip", "Bottom"], st.session_state.u_id)

        elif menu == "🔐 Security":
            st.header("👤 Profile & Reset")
            st.info(f"**Shop:** {st.session_state.u_shop}\n\n**Email:** {st.session_state.u_email}")
            np = st.text_input("New Password", type="password")
            if st.button("Save New Password"):
                conn.execute(f"UPDATE users SET password='{np}' WHERE id={st.session_state.u_id}")
                conn.commit(); st.success("Updated!")

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
