import streamlit as st
import pandas as pd
from database import init_db, get_connection
from styling import apply_styling
from orders import add_order_ui

# Initialize System
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
        st.subheader("🔐 Professional Login")
        email = st.text_input("Email Address (e.g. admin@sahilarman.com)")
        pwd = st.text_input("Password", type="password")
        
        if st.button("Sign In"):
            # Check for Super Admin or Shop Admin
            user = conn.execute("SELECT id, role, shop_name FROM users WHERE email=? AND password=?", (email, pwd)).fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.user_role = user[1]
                st.session_state.shop_name = user[2]
                st.success(f"Welcome {user[2]}")
                st.rerun()
            else:
                st.error("Invalid Email or Password!")
        
        st.info("💡 Super Admin Login: admin@sahilarman.com / sahilarman2026")
# --- SUPER ADMIN MENU LOGIC ---
if st.session_state.user_role == "super_admin":
    menu = st.sidebar.selectbox("🚀 SUPER ADMIN PANEL", 
        ["🌍 Global Dashboard", "➕ Register New Shop", "👥 All Registered Shops", "📊 Platform Analytics"])

    if menu == "🌍 Global Dashboard":
        st.subheader("🌎 Global Overview (All Shops Combined)")
        all_clients = pd.read_sql("""
            SELECT clients.id, users.shop_name as Shop, clients.name as Customer, clients.total, clients.remaining, clients.status 
            FROM clients JOIN users ON clients.user_id = users.id
        """, conn)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Platform Shops", conn.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0])
        c2.metric("Total Global Revenue", f"Rs.{all_clients['total'].sum():,.0f}")
        c3.metric("Total Recovery Pending", f"Rs.{all_clients['remaining'].sum():,.0f}")
        
        st.write("### 📜 Recent Orders Across Platform")
        st.dataframe(all_clients.tail(10), use_container_width=True)

    elif menu == "👥 All Registered Shops":
        st.subheader("👥 Registered Shops List")
        shops_df = pd.read_sql("SELECT id, shop_name, email FROM users WHERE role='admin'", conn)
        st.dataframe(shops_df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🔍 Inspect Specific Shop Data")
        selected_shop_id = st.selectbox("Select Shop to View Details", shops_df['id'].tolist(), format_func=lambda x: shops_df[shops_df['id']==x]['shop_name'].values[0])
        
        if selected_shop_id:
            shop_name = shops_df[shops_df['id']==selected_shop_id]['shop_name'].values[0]
            st.info(f"Viewing Data for: **{shop_name}**")
            
            # Drill down into selected shop's customers
            shop_data = pd.read_sql(f"SELECT name, phone, total, advance, remaining, status FROM clients WHERE user_id={selected_shop_id}", conn)
            
            if not shop_data.empty:
                st.dataframe(shop_data, use_container_width=True)
                # Shop-specific metrics
                sc1, sc2 = st.columns(2)
                sc1.metric(f"{shop_name} Sales", f"Rs.{shop_data['total'].sum():,.0f}")
                sc2.metric(f"{shop_name} Pending", f"Rs.{shop_data['remaining'].sum():,.0f}")
            else:
                st.warning("Is shop ne abhi tak koi order record nahi kiya.")

    elif menu == "➕ Register New Shop":
        # ... (Vahi purana registration code)
        st.subheader("📝 Register New Client Shop")
        with st.form("reg_form"):
            s_name = st.text_input("New Shop Name")
            s_email = st.text_input("Admin Email")
            s_pass = st.text_input("Password")
            if st.form_submit_button("Register & Activate Shop"):
                try:
                    conn.execute("INSERT INTO users (email, password, shop_name, role) VALUES (?,?,?,?)", (s_email, s_pass, s_name, 'admin'))
                    conn.commit()
                    st.success(f"{s_name} register ho gayi hai!")
                except: st.error("Email pehle se maujood hai.")
# --- LOGGED IN AREA ---
else:
    # Sidebar
    st.sidebar.title(f"👔 {st.session_state.shop_name}")
    st.sidebar.markdown(f"**Status:** {st.session_state.user_role.upper()}")
    
    # 👑 SUPER ADMIN MENU
    if st.session_state.user_role == "super_admin":
        menu = st.sidebar.selectbox("🚀 SUPER ADMIN PANEL", 
            ["🌍 Global Dashboard", "➕ Register New Shop", "👥 All Registered Shops", "📊 Platform Analytics"])

        if menu == "🌍 Global Dashboard":
            st.subheader("🌎 All Shops Global Data")
            # Super Admin sees ALL clients from ALL shops
            all_clients = pd.read_sql("""
                SELECT clients.id, users.shop_name as Shop, clients.name as Customer, clients.phone, clients.total, clients.remaining, clients.status 
                FROM clients 
                JOIN users ON clients.user_id = users.id
            """, conn)
            st.dataframe(all_clients, use_container_width=True)
            
            # Global Stats
            c1, c2 = st.columns(2)
            total_rev = all_clients['total'].sum()
            total_shops = conn.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]
            c1.metric("Total Platform Revenue", f"Rs.{total_rev:,.0f}")
            c2.metric("Total Active Shops", total_shops)

        elif menu == "➕ Register New Shop":
            st.subheader("📝 Create New Shop Account")
            with st.form("reg_form"):
                s_name = st.text_input("Shop Name")
                s_email = st.text_input("Login Email")
                s_pass = st.text_input("Assign Password")
                if st.form_submit_button("Register Shop Now"):
                    try:
                        conn.execute("INSERT INTO users (email, password, shop_name, role) VALUES (?,?,?,?)", 
                                     (s_email, s_pass, s_name, 'admin'))
                        conn.commit()
                        st.success(f"Success! {s_name} has been registered.")
                    except:
                        st.error("Error: This Email is already registered!")

    # 👔 SHOP ADMIN MENU
    else:
        menu = st.sidebar.selectbox("Shop Menu", ["🏠 My Dashboard", "📏 New Order", "📊 My Analytics", "👥 My Staff"])

        if menu == "🏠 My Dashboard":
            st.subheader(f"Dashboard - {st.session_state.shop_name}")
            # Individual Shop Admin sees ONLY their own clients
            my_clients = pd.read_sql(f"SELECT id, name, phone, total, remaining, status, delivery_date FROM clients WHERE user_id={st.session_state.user_id}", conn)
            st.dataframe(my_clients, use_container_width=True)

        elif menu == "📏 New Order":
            # Get measurement labels from settings (simplified for now)
            labels = ["Length", "Sleeves", "Shoulder", "Collar", "Chest", "Waist", "Hip", "Bottom"]
            add_order_ui(labels, st.session_state.user_id)

    # Global Logout
    st.sidebar.markdown("---")
    if st.sidebar.button("🔌 Secure Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.rerun()

