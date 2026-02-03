import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# Initialize database connection
def get_connection():
    conn = sqlite3.connect('tailor_shop.db', check_same_thread=False)
    
    # Create tables if they don't exist
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        shop_name TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        phone TEXT,
        security_q TEXT,
        security_a TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        client_name TEXT NOT NULL,
        client_phone TEXT,
        total_bill REAL NOT NULL,
        paid_amount REAL DEFAULT 0,
        balance REAL DEFAULT 0,
        order_date DATE NOT NULL,
        delivery_date DATE,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        exp_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    return conn

# Initialize connection
conn = get_connection()

# Simple translations
TRANSLATIONS = {
    "English": {
        'title': 'Tailor Shop Management',
        'email': 'Email',
        'pass': 'Password',
        'login_btn': 'Login',
        'reg_btn': 'Register',
        'forgot_btn': 'Forgot Password',
        'shop': 'Shop Name',
        'phone': 'Phone',
        's_q': 'Security Question',
        's_a': 'Security Answer',
        'dash': 'Dashboard',
        'order': 'New Order',
        'cashbook': 'Cashbook',
        'report': 'Reports',
        'sec': 'Security/Settings',
        'logout': 'Logout',
        'today_inc': "Today's Income",
        'today_exp': "Today's Expenses",
        'savings': 'Net Savings',
        'add_exp': 'Add Expense',
        'exp_desc': 'Description',
        'amount': 'Amount',
        'rename_shop': 'Rename Shop',
        'update': 'Update'
    }
}

# Simple styling function
def apply_style():
    """Apply basic CSS styles"""
    st.markdown("""
    <style>
    .main-container {
        padding: 20px;
    }
    
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Simple measurement form
def show_order_form(conn, ln):
    """Show order form"""
    st.subheader("📝 New Order Form")
    
    with st.form("order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input("Client Name*")
            client_phone = st.text_input("WhatsApp Number")
            order_date = st.date_input("Booking Date")
            
        with col2:
            delivery_date = st.date_input("Delivery Date")
            no_of_suits = st.number_input("No. of Suits", min_value=1, value=1)
            total_bill = st.number_input("Total Bill (Rs.)", min_value=0.0)
            
        measurements = st.text_area("Measurements (optional)")
        
        if st.form_submit_button("💾 Save Order"):
            if client_name:
                conn.execute("""
                    INSERT INTO orders (user_id, client_name, client_phone, total_bill, order_date, delivery_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (st.session_state.u_id, client_name, client_phone, total_bill, 
                      order_date.strftime("%Y-%m-%d"), delivery_date.strftime("%Y-%m-%d")))
                conn.commit()
                st.success("✅ Order saved successfully!")
                st.rerun()
            else:
                st.error("❌ Client Name is required!")

# Shop manager functions
def get_shop_name():
    """Get current shop name"""
    if 'shop_name' not in st.session_state:
        if 'u_shop' in st.session_state:
            st.session_state.shop_name = st.session_state.u_shop
        else:
            st.session_state.shop_name = "AZAD TAILOR"
    return st.session_state.shop_name

def set_shop_name(new_name):
    """Set shop name"""
    st.session_state.shop_name = new_name
    if 'u_shop' in st.session_state:
        st.session_state.u_shop = new_name
    
    # Update in database
    if 'u_id' in st.session_state:
        conn.execute("UPDATE users SET shop_name=? WHERE id=?", 
                    (new_name, st.session_state.u_id))
        conn.commit()

def security_settings_page():
    """Security and settings page"""
    st.title("🔒 Security / Settings")
    
    # Shop Name Section
    st.markdown("---")
    st.subheader("🏪 Rename Shop")
    
    current_name = get_shop_name()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        new_name = st.text_input(
            "Enter New Shop Name",
            value=current_name,
            key="shop_name_input",
            placeholder="e.g., Nasir Tailors"
        )
    
    with col2:
        if st.button("🔄 Update Name", use_container_width=True):
            if new_name and new_name.strip() != "":
                if new_name != current_name:
                    set_shop_name(new_name)
                    st.success(f"✅ Shop name updated to: **{new_name}**")
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a different name")
            else:
                st.warning("⚠️ Shop name cannot be empty")
    
    st.markdown(f"**Current Shop Name:** `{current_name}`")
    
    # User Profile Section
    st.markdown("---")
    st.subheader("👤 User Profile")
    
    if 'current_user' not in st.session_state:
        st.session_state.current_user = {
            'username': 'admin',
            'full_name': 'Nasir',
            'email': 'admin@tailor.com',
            'role': 'admin'
        }
    
    current_user = st.session_state.current_user
    
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name", value=current_user.get('full_name', 'Nasir'))
        email = st.text_input("Email", value=current_user.get('email', ''))
    
    with col2:
        username = st.text_input("Username", value=current_user.get('username', 'admin'), disabled=True)
        phone = st.text_input("Phone", value=current_user.get('phone', ''))
    
    if st.button("📝 Update Profile", use_container_width=True):
        st.session_state.current_user.update({
            'full_name': full_name,
            'email': email,
            'phone': phone
        })
        st.success("✅ Profile updated!")

# Main App Logic
def main():
    # Apply basic styles
    apply_style()
    
    # Initialize session states
    if 'lang' not in st.session_state: 
        st.session_state.lang = "English"
    if 'auth' not in st.session_state: 
        st.session_state.auth = False
    if 'view' not in st.session_state: 
        st.session_state.view = "login"
    
    # Get translations
    ln = TRANSLATIONS[st.session_state.lang]
    
    # Main content container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # --- AUTHENTICATION ---
    if not st.session_state.auth:
        
        # LOGIN VIEW
        if st.session_state.view == "login":
            st.title("✂️ Tailor Shop Management")
            st.markdown("---")
            
            le = st.text_input("📧 Email", key="l_e").strip().lower()
            lp = st.text_input("🔒 Password", type="password", key="l_p").strip()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🚪 Login", use_container_width=True, type="primary"):
                    if le and lp:
                        # Check for demo account or real database
                        if le == "admin@tailor.com" and lp == "admin123":
                            # Demo account
                            st.session_state.auth = True
                            st.session_state.u_id = 1
                            st.session_state.u_role = 'admin'
                            st.session_state.u_shop = "AZAD TAILOR"
                            st.session_state.current_user = {
                                'username': 'admin',
                                'full_name': 'Nasir',
                                'email': 'admin@tailor.com',
                                'role': 'admin'
                            }
                            st.rerun()
                        else:
                            # Check database
                            user = conn.execute(
                                "SELECT id, role, shop_name FROM users WHERE LOWER(email)=? AND password=?", 
                                (le, lp)
                            ).fetchone()
                            
                            if user:
                                st.session_state.auth = True
                                st.session_state.u_id = user[0]
                                st.session_state.u_role = user[1]
                                st.session_state.u_shop = user[2]
                                st.session_state.current_user = {
                                    'username': le.split('@')[0],
                                    'full_name': 'User',
                                    'email': le,
                                    'role': user[1]
                                }
                                st.rerun()
                            else:
                                st.error("❌ Invalid email or password!")
                    else:
                        st.warning("⚠️ Please enter both email and password!")
            
            with col2:
                if st.button("📝 Register", use_container_width=True):
                    st.session_state.view = "register"
                    st.rerun()
            
            # Demo login button
            st.markdown("---")
            if st.button("Try Demo Account (admin@tailor.com / admin123)", use_container_width=True):
                st.session_state.auth = True
                st.session_state.u_id = 1
                st.session_state.u_role = 'admin'
                st.session_state.u_shop = "AZAD TAILOR"
                st.session_state.current_user = {
                    'username': 'admin',
                    'full_name': 'Nasir',
                    'email': 'admin@tailor.com',
                    'role': 'admin'
                }
                st.rerun()
        
        # REGISTER VIEW
        elif st.session_state.view == "register":
            st.title("📝 Create New Account")
            st.markdown("---")
            
            r_sn = st.text_input("🏪 Shop Name*")
            r_ph = st.text_input("📱 Phone Number")
            r_e = st.text_input("📧 Email*").strip().lower()
            r_p = st.text_input("🔒 Password*", type="password")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Create Account", use_container_width=True, type="primary"):
                    if r_sn and r_e and r_p:
                        try:
                            cur = conn.cursor()
                            cur.execute("""
                                INSERT INTO users (email, password, shop_name, role, phone) 
                                VALUES (?,?,?,?,?)
                            """, (r_e, r_p, r_sn, 'admin', r_ph))
                            conn.commit()
                            
                            st.session_state.auth = True
                            st.session_state.u_id = cur.lastrowid
                            st.session_state.u_role = 'admin'
                            st.session_state.u_shop = r_sn
                            st.session_state.current_user = {
                                'username': r_e.split('@')[0],
                                'full_name': 'Owner',
                                'email': r_e,
                                'role': 'admin'
                            }
                            st.success("✅ Account created successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"⚠️ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Please fill all required fields!")
            
            with col2:
                if st.button("← Back to Login", use_container_width=True):
                    st.session_state.view = "login"
                    st.rerun()
    
    # --- AUTHENTICATED AREA ---
    else:
        # Get shop name
        shop_name = get_shop_name()
        
        # Sidebar
        with st.sidebar:
            st.markdown(f"## ✂️ {shop_name}")
            st.markdown(f"**👤 Welcome,** {st.session_state.current_user.get('full_name', 'User')}")
            st.markdown("---")
            
            # Navigation
            menu_options = ["Dashboard", "New Order", "Cashbook", "Reports", "Security/Settings"]
            menu = st.radio("📌 Navigation", menu_options)
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                # Clear session state
                for key in ['auth', 'u_id', 'u_role', 'u_shop', 'current_user']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.view = "login"
                st.rerun()
        
        # Main Content Area
        
        # DASHBOARD
        if menu == "Dashboard":
            st.title(f"🏠 {shop_name} - Dashboard")
            
            # Today's stats
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Total Orders
            total_orders = conn.execute(
                "SELECT COUNT(*) FROM orders WHERE user_id=?",
                (st.session_state.u_id,)
            ).fetchone()[0]
            
            # Today's Orders
            today_orders = conn.execute(
                "SELECT COUNT(*) FROM orders WHERE user_id=? AND order_date=?",
                (st.session_state.u_id, today)
            ).fetchone()[0]
            
            # Today's Income
            today_income = conn.execute(
                "SELECT SUM(total_bill) FROM orders WHERE user_id=? AND order_date=?",
                (st.session_state.u_id, today)
            ).fetchone()[0] or 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Orders", total_orders)
            with col2:
                st.metric("📅 Today's Orders", today_orders)
            with col3:
                st.metric("💰 Today's Income", f"Rs. {today_income}")
            
            # Recent Orders
            st.markdown("---")
            st.subheader("📋 Recent Orders")
            
            recent_orders = conn.execute("""
                SELECT client_name, client_phone, total_bill, order_date 
                FROM orders 
                WHERE user_id=? 
                ORDER BY order_date DESC 
                LIMIT 10
            """, (st.session_state.u_id,)).fetchall()
            
            if recent_orders:
                df = pd.DataFrame(recent_orders, columns=['Client', 'Phone', 'Amount', 'Date'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("📭 No orders found. Create your first order!")
        
        # NEW ORDER
        elif menu == "New Order":
            st.title(f"📝 {shop_name} - New Order")
            show_order_form(conn, ln)
        
        # CASHBOOK
        elif menu == "Cashbook":
            st.title(f"💰 {shop_name} - Cashbook")
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Today's Income
            today_income = conn.execute(
                "SELECT SUM(total_bill) FROM orders WHERE user_id=? AND order_date=?",
                (st.session_state.u_id, today)
            ).fetchone()[0] or 0
            
            # Today's Expenses
            today_expense = conn.execute(
                "SELECT SUM(amount) FROM expenses WHERE user_id=? AND exp_date=?",
                (st.session_state.u_id, today)
            ).fetchone()[0] or 0
            
            net_balance = today_income - today_expense
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📈 Income", f"Rs. {today_income}")
            col2.metric("📉 Expenses", f"Rs. {today_expense}")
            col3.metric("💰 Net Balance", f"Rs. {net_balance}")
            
            # Add Expense
            st.markdown("---")
            st.subheader("➕ Add Expense")
            
            with st.form("expense_form"):
                e_desc = st.text_input("Description")
                e_amount = st.number_input("Amount (Rs.)", min_value=0.0, value=0.0)
                
                if st.form_submit_button("💾 Save Expense"):
                    if e_desc and e_amount > 0:
                        conn.execute("""
                            INSERT INTO expenses (user_id, description, amount, exp_date)
                            VALUES (?, ?, ?, ?)
                        """, (st.session_state.u_id, e_desc, e_amount, today))
                        conn.commit()
                        st.success("✅ Expense saved!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Please fill all fields!")
            
            # Expense History
            st.markdown("---")
            st.subheader("📜 Expense History")
            
            expenses = conn.execute("""
                SELECT description, amount, exp_date 
                FROM expenses 
                WHERE user_id=? 
                ORDER BY exp_date DESC 
                LIMIT 20
            """, (st.session_state.u_id,)).fetchall()
            
            if expenses:
                exp_df = pd.DataFrame(expenses, columns=['Description', 'Amount', 'Date'])
                st.dataframe(exp_df, use_container_width=True)
        
        # REPORTS
        elif menu == "Reports":
            st.title(f"📊 {shop_name} - Reports")
            
            # Date range selector
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From Date", datetime.now().replace(day=1))
            with col2:
                end_date = st.date_input("To Date", datetime.now())
            
            if st.button("Generate Report"):
                # Sales Report
                sales_report = conn.execute("""
                    SELECT order_date, COUNT(*) as orders, SUM(total_bill) as total_income
                    FROM orders 
                    WHERE user_id=? AND order_date BETWEEN ? AND ?
                    GROUP BY order_date
                    ORDER BY order_date DESC
                """, (st.session_state.u_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))).fetchall()
                
                if sales_report:
                    sales_df = pd.DataFrame(sales_report, columns=['Date', 'Orders', 'Income'])
                    st.subheader("📈 Sales Report")
                    st.dataframe(sales_df, use_container_width=True)
                    st.bar_chart(sales_df.set_index('Date')['Income'])
                else:
                    st.info("📭 No data found for selected period")
        
        # SECURITY/SETTINGS
        elif menu == "Security/Settings":
            security_settings_page()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
