import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Import directly from the files you uploaded (No modules folder)
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui

# Initialize Database
init_db()
conn = get_connection()

# Load Shop Settings
settings = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
shop_name = settings[1]
admin_pass = settings[2]
m_labels = settings[3].split(',')

# Apply Sahil & Arman IT Branding
apply_styling(shop_name)

# --- Authentication ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.subheader("🔐 Enterprise Login")
        pwd = st.text_input("Enter Password", type="password")
        if st.button("Sign In"):
            if pwd == admin_pass:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid Password!")
        
        with st.expander("Forgot Password?"):
            st.info("Master Key: MASTER2026")
            m_key = st.text_input("Master Key", type="password")
            if st.button("Recover"):
                if m_key == "MASTER2026": st.warning(f"Pass: {admin_pass}")

else:
    # --- Sidebar ---
    st.sidebar.markdown(f"### 👔 {shop_name}")
    menu = st.sidebar.selectbox("🚀 ERP MENU", 
        ["🏠 Dashboard", "📏 New Order", "📊 Analytics", "👥 Staff", "⚙️ Settings"])
    
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    # --- 🏠 Dashboard ---
    if menu == "🏠 Dashboard":
        st.subheader("📈 Business Metrics")
        stats = pd.read_sql("SELECT SUM(total), SUM(advance), SUM(remaining) FROM clients", conn).iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Sales", f"Rs.{stats[0] or 0}")
        c2.metric("Received", f"Rs.{stats[1] or 0}")
        c3.metric("Outstanding", f"Rs.{stats[2] or 0}")

        st.markdown("---")
        st.subheader("🔍 Search Customer")
        search = st.text_input("Name / Phone")
        query = "SELECT id, name, phone, status, delivery_date FROM clients"
        if search: query += f" WHERE name LIKE '%{search}%' OR phone LIKE '%{search}%'"
        st.dataframe(pd.read_sql(query, conn), use_container_width=True)

    # --- 📏 New Order ---
    elif menu == "📏 New Order":
        add_order_ui(m_labels)

    # --- 📊 Analytics ---
    elif menu == "📊 Analytics":
        import analytics
        analytics.show_reports()

    # --- 👥 Staff ---
    elif menu == "👥 Staff":
        st.subheader("👥 Staff Management")
        with st.form("staff_add"):
            s_name = st.text_input("Name"); s_role = st.text_input("Role")
            if st.form_submit_button("Add Staff"):
                conn.execute("INSERT INTO staff (name, role) VALUES (?,?)", (s_name, s_role))
                conn.commit()
                st.success("Staff Added!")
        st.table(pd.read_sql("SELECT * FROM staff", conn))

    # --- ⚙️ Settings ---
    elif menu == "⚙️ Settings":
        st.subheader("⚙️ System Settings")
        new_shop = st.text_input("Shop Name", shop_name)
        new_labels = st.text_area("Measurement Labels", ",".join(m_labels))
        if st.button("Save Settings"):
            conn.execute("UPDATE settings SET shop_name=?, m_labels=? WHERE id=1", (new_shop, new_labels))
            conn.commit()
            st.success("Settings Saved! Restarting...")
            st.rerun()
