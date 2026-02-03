import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui

# --- 1. CONFIGURATION & INITIALIZATION ---
st.set_page_config(page_title="AZAD TAILOR PRO", layout="wide", page_icon="👔")

# Session variables initialization (AttributeError se bachne ke liye)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'u_id' not in st.session_state: st.session_state.u_id = 0
if 'u_shop' not in st.session_state: st.session_state.u_shop = "Guest"

init_db()
conn = get_connection()

# Theme aur 30 Wallpapers apply karna
apply_styling()

# --- 2. LOGIN LOGIC ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>👔 Tailor Master Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Digital Management System for Azad Tailors</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("### 🔐 Secure Login")
        email = st.text_input("Email Address").strip()
        pwd = st.text_input("Password", type="password").strip()
        
        if st.button("LOGIN TO DASHBOARD", use_container_width=True):
            # Database check
            user = conn.execute("SELECT id, shop_name FROM users WHERE email=? AND password=?", (email, pwd)).fetchone()
            
            # Hardcoded bypass for your specific admin if DB fails
            if user:
                st.session_state.auth = True
                st.session_state.u_id = user[0]
                st.session_state.u_shop = user[1]
                st.rerun()
            elif email == "admin@sahilarman.com" and pwd == "sahilarman2026":
                st.session_state.auth = True
                st.session_state.u_id = 1
                st.session_state.u_shop = "AZAD TAILOR"
                st.rerun()
            else:
                st.error("Ghalt Email ya Password! Dobara check karein.")
else:
    # --- 3. LOGGED IN: SIDEBAR ---
    st.sidebar.markdown(f"## 🏬 {st.session_state.u_shop}")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("MAIN NAVIGATION", ["🏠 Dashboard", "📏 New Order", "🔐 Security & Profile"])

    # --- 4. DASHBOARD PAGE ---
    if menu == "🏠 Dashboard":
        st.title(f"Welcome to {st.session_state.u_shop} Dashboard")
        
        # 📊 BUSINESS SUMMARY (Hisab Kitab)
        try:
            # Table name 'clients' ya 'orders' jo bhi aap use kar rahe hain
            stats_query = f"SELECT SUM(total_bill) as t, SUM(balance) as r FROM orders WHERE user_id={st.session_state.u_id}"
            # Note: Agar table name 'clients' hai to upar 'orders' ko change kar dein
            stats = pd.read_sql(stats_query, conn)
            total_biz = stats['t'].iloc[0] or 0
            pending_rec = stats['r'].iloc[0] or 0
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Business Volume", f"Rs.{total_biz:,.0f}")
            with c2:
                st.metric("Pending Recovery", f"Rs.{pending_rec:,.0f}", delta_color="inverse")
            with c3:
                st.metric("Cash Received", f"Rs.{(total_biz - pending_rec):,.0f}")
        except:
            st.info("💡 Tip: Naye orders add karein taake yahan hisab-kitab show ho sake.")

        st.divider()

        # 📋 RECENT ORDERS LIST
        st.subheader("📋 Recent Orders & Tracking")
        try:
            orders_df = pd.read_sql(f"SELECT order_no as 'Order #', client_name as 'Customer', balance as 'Balance', status as 'Status' FROM orders WHERE user_id={st.session_state.u_id} ORDER BY id DESC", conn)
            if not orders_df.empty:
                st.dataframe(orders_df, use_container_width=True)
            else:
                st.write("Abhi tak koi order record nahi mila.")
        except:
            st.write("Orders table load nahi ho saki.")

    # --- 5. NEW ORDER PAGE (Azad Tailor Form) ---
    elif menu == "📏 New Order":
        # Ye orders.py ke naye function ko call karega
        add_order_ui(st.session_state.u_id)

    # --- 6. SECURITY & PROFILE ---
    elif menu == "🔐 Security & Profile":
        st.header("👤 Account Security")
        st.info(f"**Current Shop:** {st.session_state.u_shop}")
        
        st.markdown("### Change Password")
        new_p = st.text_input("Enter New Password", type="password")
        if st.button("Update System Password"):
            if len(new_p) >= 4:
                conn.execute("UPDATE users SET password=? WHERE id=?", (new_p, st.session_state.u_id))
                conn.commit()
                st.success("✅ Password kamyabi se update ho gaya!")
            else:
                st.warning("Password kam se kam 4 characters ka hona chahiye.")

    # --- LOGOUT ---
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout System", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# Database connection close karna mat bhooliye
conn.close()
