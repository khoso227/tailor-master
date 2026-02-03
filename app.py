import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import sqlite3
import os

# Page configuration
st.set_page_config(
    page_title="Tailor Shop Management",
    page_icon="✂️",
    layout="wide"
)

# Database setup with error handling
def setup_database():
    """Initialize database with all required tables"""
    conn = sqlite3.connect('tailor_shop.db', check_same_thread=False)
    
    # First, check if tables exist and handle migration
    try:
        # Try to get table info
        users_exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
        
        if users_exists:
            # Check if full_name column exists
            columns = conn.execute("PRAGMA table_info(users)").fetchall()
            column_names = [col[1] for col in columns]
            
            if 'full_name' not in column_names:
                # Add the missing column
                conn.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
                conn.commit()
    except:
        pass
    
    # Now create or update tables
    # Users table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        shop_name TEXT NOT NULL,
        phone TEXT,
        role TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Shop configuration table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS shop_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        shop_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Orders table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        order_no TEXT UNIQUE NOT NULL,
        client_name TEXT NOT NULL,
        client_phone TEXT,
        booking_date DATE NOT NULL,
        delivery_date DATE NOT NULL,
        no_of_suits INTEGER DEFAULT 1,
        total_bill REAL NOT NULL,
        paid_amount REAL DEFAULT 0,
        balance REAL DEFAULT 0,
        status TEXT DEFAULT 'pending',
        measurements TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Expenses table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT DEFAULT 'other',
        expense_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Insert demo data if no users exist
    try:
        user_check = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_check == 0:
            conn.execute("""
            INSERT INTO users (email, password, full_name, shop_name, phone, role)
            VALUES ('admin@tailor.com', 'admin123', 'Nasir', 'AZAD TAILOR', '+91 9876543210', 'admin')
            """)
            
            # Get the user ID
            user_id = conn.execute("SELECT id FROM users WHERE email='admin@tailor.com'").fetchone()[0]
            
            # Insert shop config
            conn.execute("""
            INSERT INTO shop_config (user_id, shop_name)
            VALUES (?, ?)
            """, (user_id, 'AZAD TAILOR'))
            
            conn.commit()
    except Exception as e:
        print(f"Error inserting demo data: {e}")
        conn.rollback()
    
    return conn

# Initialize database
conn = setup_database()

# Custom CSS
def apply_custom_css():
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
    }
    
    .shop-name-display {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Shop name management
def get_shop_name():
    """Get current shop name from database"""
    if 'user_id' in st.session_state and st.session_state.user_id:
        result = conn.execute(
            "SELECT shop_name FROM shop_config WHERE user_id=?",
            (st.session_state.user_id,)
        ).fetchone()
        return result[0] if result else "AZAD TAILOR"
    return "AZAD TAILOR"

def update_shop_name(new_name):
    """Update shop name in database"""
    try:
        if 'user_id' in st.session_state and st.session_state.user_id:
            conn.execute(
                "UPDATE shop_config SET shop_name=? WHERE user_id=?",
                (new_name, st.session_state.user_id)
            )
            conn.execute(
                "UPDATE users SET shop_name=? WHERE id=?",
                (new_name, st.session_state.user_id)
            )
            conn.commit()
            
            # Update session state
            if 'shop_name' in st.session_state:
                st.session_state.shop_name = new_name
            return True
    except Exception as e:
        st.error(f"Error updating shop name: {str(e)}")
    return False

# Authentication functions
def authenticate_user(email, password):
    """Authenticate user credentials"""
    try:
        user = conn.execute(
            "SELECT id, email, full_name, shop_name FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        return user
    except:
        return None

def register_user(email, password, full_name, shop_name, phone):
    """Register new user"""
    try:
        conn.execute("""
        INSERT INTO users (email, password, full_name, shop_name, phone)
        VALUES (?, ?, ?, ?, ?)
        """, (email, password, full_name, shop_name, phone))
        
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        conn.execute("""
        INSERT INTO shop_config (user_id, shop_name)
        VALUES (?, ?)
        """, (user_id, shop_name))
        
        conn.commit()
        return user_id
    except Exception as e:
        return None

# Login Page
def login_page():
    """Login page UI"""
    st.title("✂️ Tailor Shop Management")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        email = st.text_input("📧 Email", placeholder="admin@tailor.com")
        password = st.text_input("🔒 Password", type="password", placeholder="admin123")
        
        login_col1, login_col2 = st.columns(2)
        
        with login_col1:
            if st.button("🚪 Login", use_container_width=True, type="primary"):
                if email and password:
                    user = authenticate_user(email, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user[0]
                        st.session_state.user_email = user[1]
                        st.session_state.user_name = user[2] or "User"
                        st.session_state.shop_name = user[3]
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password!")
                else:
                    st.warning("⚠️ Please enter both email and password")
        
        with login_col2:
            if st.button("📝 Register", use_container_width=True):
                st.session_state.current_page = "register"
                st.rerun()
    
    with col2:
        st.markdown("### Quick Demo")
        if st.button("Try Demo Account", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_id = 1
            st.session_state.user_email = "admin@tailor.com"
            st.session_state.user_name = "Nasir"
            st.session_state.shop_name = "AZAD TAILOR"
            st.rerun()
        
        st.markdown("---")
        st.info("**Demo Credentials:**")
        st.info("Email: admin@tailor.com")
        st.info("Password: admin123")

# Register Page
def register_page():
    """Registration page UI"""
    st.title("📝 Create New Account")
    st.markdown("---")
    
    with st.form("register_form"):
        shop_name = st.text_input("🏪 Shop Name*", placeholder="e.g., AZAD TAILOR")
        full_name = st.text_input("👤 Full Name*", placeholder="Your Name")
        email = st.text_input("📧 Email*", placeholder="your@email.com")
        phone = st.text_input("📱 Phone", placeholder="+91 9876543210")
        password = st.text_input("🔒 Password*", type="password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit = st.form_submit_button("✅ Create Account", use_container_width=True, type="primary")
        
        with col2:
            if st.form_submit_button("← Back to Login"):
                st.session_state.current_page = "login"
                st.rerun()
        
        if submit:
            if not all([shop_name, full_name, email, password]):
                st.error("❌ Please fill all required fields (*)")
            else:
                user_id = register_user(email, password, full_name, shop_name, phone)
                if user_id:
                    st.success("✅ Account created! Please login.")
                    st.session_state.current_page = "login"
                    st.rerun()
                else:
                    st.error("❌ Email already exists!")

# Sidebar Navigation
def sidebar_navigation():
    """Sidebar navigation menu"""
    with st.sidebar:
        st.markdown(f"# ✂️ {st.session_state.shop_name}")
        st.markdown(f"**👤 Welcome,** {st.session_state.user_name}")
        st.markdown("---")
        
        # Navigation options
        menu = st.radio(
            "Navigation",
            ["📊 Dashboard", "📝 New Order", "💰 Cashbook", "📈 Reports", "⚙️ Settings"]
        )
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session
            for key in ['authenticated', 'user_id', 'user_email', 'user_name', 'shop_name']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        return menu

# Dashboard Page
def dashboard_page():
    """Dashboard page with statistics"""
    shop_name = get_shop_name()
    st.title(f"🏠 {shop_name} - Dashboard")
    
    # Get statistics
    today = date.today().strftime('%Y-%m-%d')
    
    # Calculate metrics
    total_orders = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE user_id=?",
        (st.session_state.user_id,)
    ).fetchone()[0] or 0
    
    today_orders = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE user_id=? AND booking_date=?",
        (st.session_state.user_id, today)
    ).fetchone()[0] or 0
    
    total_income = conn.execute(
        "SELECT COALESCE(SUM(total_bill), 0) FROM orders WHERE user_id=?",
        (st.session_state.user_id,)
    ).fetchone()[0] or 0
    
    pending_amount = conn.execute(
        "SELECT COALESCE(SUM(balance), 0) FROM orders WHERE user_id=?",
        (st.session_state.user_id,)
    ).fetchone()[0] or 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Orders", total_orders)
    
    with col2:
        st.metric("📅 Today's Orders", today_orders)
    
    with col3:
        st.metric("💰 Total Income", f"₹ {total_income:,.2f}")
    
    with col4:
        st.metric("⏳ Pending Amount", f"₹ {pending_amount:,.2f}")
    
    st.markdown("---")
    
    # Recent Orders
    st.subheader("📋 Recent Orders")
    
    recent_orders = conn.execute("""
        SELECT order_no, client_name, client_phone, booking_date, 
               total_bill, paid_amount, balance 
        FROM orders 
        WHERE user_id=? 
        ORDER BY booking_date DESC 
        LIMIT 10
    """, (st.session_state.user_id,)).fetchall()
    
    if recent_orders:
        df = pd.DataFrame(recent_orders, columns=[
            'Order No', 'Client', 'Phone', 'Booking Date', 'Total', 'Paid', 'Balance'
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("📭 No orders found. Create your first order!")

# New Order Page
def new_order_page():
    """New order form"""
    shop_name = get_shop_name()
    st.title(f"📝 {shop_name} - New Order")
    
    with st.form("order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate order number
            today_str = datetime.now().strftime('%Y%m%d')
            order_count = conn.execute(
                "SELECT COUNT(*) FROM orders WHERE user_id=? AND DATE(created_at)=DATE('now')",
                (st.session_state.user_id,)
            ).fetchone()[0] or 0
            
            order_no = f"ORD{today_str}{order_count + 1:03d}"
            
            st.text_input("Order No.", value=order_no, disabled=True)
            client_name = st.text_input("👤 Client Name*", placeholder="Enter client name")
            client_phone = st.text_input("📱 WhatsApp Number", placeholder="+91 9876543210")
            booking_date = st.date_input("📅 Booking Date*", value=date.today())
        
        with col2:
            delivery_date = st.date_input("📦 Delivery Date*", value=date.today())
            no_of_suits = st.number_input("👔 No. of Suits*", min_value=1, value=1)
            total_bill = st.number_input("💰 Total Bill (₹)*", min_value=0.0, value=0.0)
            advance_payment = st.number_input("💵 Advance Payment", min_value=0.0, value=0.0, max_value=total_bill)
        
        # Measurements
        st.markdown("---")
        st.subheader("📏 Measurements (Inches)")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            length = st.text_input("Length", placeholder="42 1/2")
        with m_col2:
            sleeves = st.text_input("Sleeves", placeholder="25 1/2")
        with m_col3:
            shoulder = st.text_input("Shoulder", placeholder="20 1/2")
        with m_col4:
            collar = st.text_input("Collar", placeholder="17 1/2")
        
        m_col5, m_col6, m_col7, m_col8 = st.columns(4)
        with m_col5:
            chest = st.text_input("Chest", placeholder="48")
        with m_col6:
            lower_chest = st.text_input("Lower Chest", placeholder="46")
        with m_col7:
            waist = st.text_input("Waist", placeholder="40")
        with m_col8:
            hip_ghera = st.text_input("Hip / Ghera", placeholder="28")
        
        notes = st.text_area("📝 Notes", placeholder="Any special instructions...")
        
        submitted = st.form_submit_button("💾 Save Order", type="primary", use_container_width=True)
        
        if submitted:
            if not client_name or total_bill <= 0:
                st.error("❌ Please fill all required fields (*)")
            else:
                try:
                    # Create measurements dictionary
                    measurements = {
                        'length': length,
                        'sleeves': sleeves,
                        'shoulder': shoulder,
                        'collar': collar,
                        'chest': chest,
                        'lower_chest': lower_chest,
                        'waist': waist,
                        'hip_ghera': hip_ghera
                    }
                    
                    # Insert order
                    conn.execute("""
                        INSERT INTO orders (
                            user_id, order_no, client_name, client_phone,
                            booking_date, delivery_date, no_of_suits,
                            total_bill, paid_amount, balance, measurements, notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        st.session_state.user_id, order_no, client_name, client_phone,
                        booking_date.strftime('%Y-%m-%d'), delivery_date.strftime('%Y-%m-%d'),
                        no_of_suits, total_bill, advance_payment, total_bill - advance_payment,
                        json.dumps(measurements), notes
                    ))
                    
                    conn.commit()
                    st.success(f"✅ Order saved successfully! Order No: {order_no}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error saving order: {str(e)}")

# Settings Page
def settings_page():
    """Settings page with shop name change"""
    st.title("⚙️ Settings")
    
    # Shop Name Change
    st.subheader("🏪 Rename Shop")
    
    current_name = get_shop_name()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_name = st.text_input(
            "Enter New Shop Name",
            value=current_name,
            key="shop_name_input"
        )
    
    with col2:
        if st.button("🔄 Update", type="primary", use_container_width=True):
            if new_name and new_name.strip():
                if update_shop_name(new_name.strip()):
                    st.success(f"✅ Shop name updated to: **{new_name.strip()}**")
                    st.rerun()
                else:
                    st.error("❌ Failed to update shop name")
            else:
                st.warning("⚠️ Please enter a valid shop name")
    
    st.markdown(f"**Current Shop Name:** `{current_name}`")
    
    # User Profile
    st.markdown("---")
    st.subheader("👤 User Profile")
    
    # Get current user info
    user_info = conn.execute(
        "SELECT full_name, email, phone FROM users WHERE id=?",
        (st.session_state.user_id,)
    ).fetchone()
    
    if user_info:
        with st.form("profile_form"):
            full_name = st.text_input("Full Name", value=user_info[0] or "")
            email = st.text_input("Email", value=user_info[1], disabled=True)
            phone = st.text_input("Phone", value=user_info[2] or "")
            
            if st.form_submit_button("📝 Update Profile", type="primary"):
                conn.execute(
                    "UPDATE users SET full_name=?, phone=? WHERE id=?",
                    (full_name, phone, st.session_state.user_id)
                )
                conn.commit()
                st.session_state.user_name = full_name
                st.success("✅ Profile updated successfully!")

# Cashbook Page
def cashbook_page():
    """Cashbook page"""
    shop_name = get_shop_name()
    st.title(f"💰 {shop_name} - Cashbook")
    
    today = date.today().strftime('%Y-%m-%d')
    
    # Today's stats
    today_income = conn.execute(
        "SELECT COALESCE(SUM(total_bill), 0) FROM orders WHERE user_id=? AND booking_date=?",
        (st.session_state.user_id, today)
    ).fetchone()[0] or 0
    
    today_expenses = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id=? AND expense_date=?",
        (st.session_state.user_id, today)
    ).fetchone()[0] or 0
    
    net_balance = today_income - today_expenses
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📈 Today's Income", f"₹ {today_income:,.2f}")
    col2.metric("📉 Today's Expenses", f"₹ {today_expenses:,.2f}")
    col3.metric("💰 Net Balance", f"₹ {net_balance:,.2f}")
    
    # Add Expense
    st.markdown("---")
    st.subheader("➕ Add Expense")
    
    with st.form("expense_form"):
        desc = st.text_input("Description", placeholder="e.g., Fabric purchase")
        amount = st.number_input("Amount (₹)", min_value=0.0, value=0.0)
        category = st.selectbox("Category", ["Material", "Labor", "Rent", "Utilities", "Other"])
        
        if st.form_submit_button("💾 Save Expense", type="primary"):
            if desc and amount > 0:
                conn.execute("""
                    INSERT INTO expenses (user_id, description, amount, category, expense_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (st.session_state.user_id, desc, amount, category, today))
                conn.commit()
                st.success("✅ Expense saved!")
                st.rerun()
            else:
                st.warning("⚠️ Please fill all fields")

# Reports Page
def reports_page():
    """Reports page"""
    shop_name = get_shop_name()
    st.title(f"📈 {shop_name} - Reports")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", value=date.today().replace(day=1))
    with col2:
        end_date = st.date_input("To Date", value=date.today())
    
    if st.button("Generate Report", type="primary"):
        # Sales report
        sales_data = conn.execute("""
            SELECT booking_date, COUNT(*) as orders, SUM(total_bill) as income
            FROM orders 
            WHERE user_id=? AND booking_date BETWEEN ? AND ?
            GROUP BY booking_date
            ORDER BY booking_date
        """, (st.session_state.user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))).fetchall()
        
        if sales_data:
            dates, orders, income = zip(*sales_data)
            
            # Create DataFrame
            report_df = pd.DataFrame({
                'Date': dates,
                'Orders': orders,
                'Income': income
            })
            
            st.subheader("📊 Sales Report")
            st.dataframe(report_df, use_container_width=True)
            
            # Chart
            fig = px.bar(report_df, x='Date', y='Income', title='Daily Income')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data found for selected period")

# Main App
def main():
    """Main application function"""
    # Apply CSS
    apply_custom_css()
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "login"
    
    # Main app logic
    if not st.session_state.authenticated:
        if st.session_state.current_page == "login":
            login_page()
        elif st.session_state.current_page == "register":
            register_page()
    else:
        # Get navigation
        menu = sidebar_navigation()
        
        # Display appropriate page
        if menu == "📊 Dashboard":
            dashboard_page()
        elif menu == "📝 New Order":
            new_order_page()
        elif menu == "💰 Cashbook":
            cashbook_page()
        elif menu == "📈 Reports":
            reports_page()
        elif menu == "⚙️ Settings":
            settings_page()

# Run the app
if __name__ == "__main__":
    main()
