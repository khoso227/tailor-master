import streamlit as st
import pandas as pd
import plotly.express as px
from modules.database import init_db, get_connection
from modules.styling import apply_styling
from modules.orders import add_order_ui

# Initialize System
init_db()
conn = get_connection()

# Load Shop Settings
settings = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
shop_name, admin_pass, m_labels = settings[1], settings[2], settings[3].split(',')

# Styling
apply_styling(shop_name)

# --- Session Management ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.subheader("🔐 Enterprise Login")
        pwd = st.text_input("Enter Password", type="password")
        if st.button("Sign In"):
            if pwd == admin_pass:
                st.session_state.auth = True
                st.rerun()
            else: st.error("Access Denied")
else:
    # --- Sidebar Navigation ---
    menu = st.sidebar.selectbox("🚀 ERP MENU", 
        ["🏠 Dashboard", "📏 New Order", "📊 Analytics", "👥 Staff", "⚙️ Settings"])
    
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    # --- Dashboard ---
    if menu == "🏠 Dashboard":
        st.subheader("📈 Real-time Business Metrics")
        stats = pd.read_sql("SELECT SUM(total), SUM(advance), SUM(remaining) FROM clients", conn).iloc[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue", f"Rs.{stats[0] or 0}")
        c2.metric("Cash Inflow", f"Rs.{stats[1] or 0}")
        c3.metric("Pending Recovery", f"Rs.{stats[2] or 0}")

        st.markdown("---")
        st.subheader("🔍 Active Orders History")
        df = pd.read_sql("SELECT id, name, phone, status, delivery_date FROM clients", conn)
        st.dataframe(df, use_container_width=True)

    # --- New Order ---
    elif menu == "📏 New Order":
        add_order_ui(m_labels)

    # --- Settings (Modify Measurements) ---
    elif menu == "⚙️ Settings":
        st.subheader("🛠️ System Configuration")
        new_labels = st.text_area("Measurement Labels (Separated by Comma)", ",".join(m_labels))
        if st.button("Update Labels & Shop"):
            conn.execute("UPDATE settings SET m_labels=? WHERE id=1", (new_labels,))
            conn.commit()
            st.success("System updated! Refreshing...")
            st.rerun()

    # --- Staff ---
    elif menu == "👥 Staff":
        st.info("Staff management module is under construction by Sahil & Arman IT Co.")