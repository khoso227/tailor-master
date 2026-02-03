import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import sqlite3
from sqlalchemy import create_engine, text
from fpdf import FPDF
import io
import json
import os

# Page configuration
st.set_page_config(
    page_title="Tailor Shop Management",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
def apply_custom_css():
    st.markdown("""
    <style>
    /* Main container */
    .main-container {
        padding: 20px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
        border: 2px solid #45a049;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #2c3e50;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    """, unsafe_allow_html=True)

# Database setup
def setup_database():
    """Initialize database with all required tables"""
    conn = sqlite3.connect('tailor_shop.db', check_same_thread=False)
    
    # Users table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
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
        currency TEXT DEFAULT '₹ (INR)',
        date_format TEXT DEFAULT 'DD/MM/YYYY',
        units TEXT DEFAULT 'Inches',
        theme TEXT DEFAULT 'light',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    
    # Measurements table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        length TEXT,
        sleeves TEXT,
        shoulder TEXT,
        collar TEXT,
        chest TEXT,
        lower_chest TEXT,
        waist TEXT,
        hip_ghera TEXT,
        FOREIGN KEY (order_id) REFERENCES orders (id)
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
    
    # Customers table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        measurements TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Insert demo data if no users exist
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
        
        # Insert sample orders
        sample_orders = [
            (user_id, 'ORD20240101001', 'John Doe', '+91 9876543211', '2024-01-01', '2024-01-10', 2, 5000, 3000, 2000),
            (user_id, 'ORD20240102001', 'Jane Smith', '+91 9876543212', '2024-01-02', '2024-01-12', 1, 2500, 2500, 0),
            (user_id, 'ORD20240103001', 'Robert Johnson', '+91 9876543213', '2024-01-03', '2024-01-15', 3, 7500, 5000, 2500),
        ]
        
        for order in sample_orders:
            conn.execute("""
            INSERT INTO orders (user_id, order_no, client_name, client_phone, booking_date, delivery_date, 
                              no_of_suits, total_bill, paid_amount, balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, order)
        
        conn.commit()
    
    return conn

# Initialize database
conn = setup_database()

# Session state initialization
def init_session_state():
    """Initialize all session state variables"""
    default_states = {
        'authenticated': False,
        'user_id': None,
        'user_email': None,
        'user_name': None,
        'shop_name': 'AZAD TAILOR',
        'current_page': 'login',
        'language': 'English',
        'theme': 'light'
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Shop name management
def get_shop_name():
    """Get current shop name from database"""
    if st.session_state.authenticated:
        result = conn.execute(
            "SELECT shop_name FROM shop_config WHERE user_id=?",
            (st.session_state.user_id,)
        ).fetchone()
        return result[0] if result else "AZAD TAILOR"
    return "AZAD TAILOR"

def update_shop_name(new_name):
    """Update shop name in database"""
    try:
        conn.execute(
            "UPDATE shop_config SET shop_name=?, updated_at=CURRENT_TIMESTAMP WHERE user_id=?",
            (new_name, st.session_state.user_id)
        )
        conn.execute(
            "UPDATE users SET shop_name=? WHERE id=?",
            (new_name, st.session_state.user_id)
        )
        conn.commit()
        st.session_state.shop_name = new_name
        return True
    except Exception as e:
        st.error(f"Error updating shop name: {str(e)}")
        return False

# Authentication functions
def authenticate_user(email, password):
    """Authenticate user credentials"""
    user = conn.execute(
        "SELECT id, email, full_name, shop_name FROM users WHERE email=? AND password=?",
        (email, password)
    ).fetchone()
    
    return user

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

# UI Components
def login_page():
    """Login page UI"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>✂️ Tailor Shop Management</h1>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("### 🔐 Login")
            
            email = st.text_input("📧 Email", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🚪 Login", use_container_width=True, type="primary"):
                    if email and password:
                        user = authenticate_user(email, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user_id = user[0]
                            st.session_state.user_email = user[1]
                            st.session_state.user_name = user[2]
                            st.session_state.shop_name = user[3]
                            st.session_state.current_page = "dashboard"
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password!")
                    else:
                        st.warning("⚠️ Please enter both email and password")
            
            with col_b:
                if st.button("📝 Register", use_container_width=True):
                    st.session_state.current_page = "register"
                    st.rerun()
            
            st.markdown("---")
            st.info("**Demo Account:** admin@tailor.com / admin123")

def register_page():
    """Registration page UI"""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>📝 Create Account</h1>", unsafe_allow_html=True)
        
        with st.form("registration_form"):
            st.markdown("### 🏪 Shop Information")
            shop_name = st.text_input("Shop Name*", placeholder="Enter your shop name")
            
            st.markdown("### 👤 Personal Information")
            full_name = st.text_input("Full Name*", placeholder="Your full name")
            email = st.text_input("Email*", placeholder="your.email@example.com")
            phone = st.text_input("Phone Number", placeholder="+91 9876543210")
            password = st.text_input("Password*", type="password", placeholder="Create a strong password")
            confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Re-enter password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("✅ Create Account", use_container_width=True, type="primary")
            
            with col_b:
                if st.form_submit_button("← Back to Login", use_container_width=True):
                    st.session_state.current_page = "login"
                    st.rerun()
            
            if submit:
                if not all([shop_name, full_name, email, password, confirm_password]):
                    st.error("❌ Please fill all required fields!")
                elif password != confirm_password:
                    st.error("❌ Passwords don't match!")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters!")
                else:
                    user_id = register_user(email, password, full_name, shop_name, phone)
                    if user_id:
                        st.success("✅ Account created successfully! Please login.")
                        st.session_state.current_page = "login"
                        st.rerun()
                    else:
                        st.error("❌ Email already exists!")

def sidebar_navigation():
    """Sidebar navigation"""
    with st.sidebar:
        st.markdown(f"# ✂️ {st.session_state.shop_name}")
        st.markdown(f"**👤 Welcome,** {st.session_state.user_name}")
        st.markdown("---")
        
        # Navigation menu
        menu_options = {
            "📊 Dashboard": "dashboard",
            "📝 New Order": "new_order",
            "👥 Customers": "customers",
            "💰 Cashbook": "cashbook",
            "📈 Reports": "reports",
            "⚙️ Settings": "settings"
        }
        
        selected = st.radio("Navigation", list(menu_options.keys()))
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        return menu_options[selected]

def dashboard_page():
    """Dashboard page"""
    st.title(f"🏠 {st.session_state.shop_name} - Dashboard")
    
    # Get statistics
    today = date.today().strftime('%Y-%m-%d')
    
    # Total statistics
    total_orders = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE user_id=?",
        (st.session_state.user_id,)
    ).fetchone()[0]
    
    total_customers = conn.execute(
        "SELECT COUNT(DISTINCT client_phone) FROM orders WHERE user_id=?",
        (st.session_state.user_id,)
    ).fetchone()[0]
    
    total_income = conn.execute(
        "SELECT COALESCE(SUM(total_bill), 0) FROM orders WHERE user_id=?",
        (st.session_state.user_id,)
    ).fetchone()[0]
    
    total_pending = conn.execute(
        "SELECT COALESCE(SUM(balance), 0) FROM orders WHERE user_id=?",
        (st.session_state.user_id,)
    ).fetchone()[0]
    
    # Today's statistics
    today_orders = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE user_id=? AND DATE(booking_date)=?",
        (st.session_state.user_id, today)
    ).fetchone()[0]
    
    today_income = conn.execute(
        "SELECT COALESCE(SUM(total_bill), 0) FROM orders WHERE user_id=? AND DATE(booking_date)=?",
        (st.session_state.user_id, today)
    ).fetchone()[0]
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Orders", total_orders)
    with col2:
        st.metric("👥 Total Customers", total_customers)
    with col3:
        st.metric("💰 Total Income", f"₹ {total_income:,.2f}")
    with col4:
        st.metric("⏳ Pending Amount", f"₹ {total_pending:,.2f}")
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    with col5:
        st.metric("📅 Today's Orders", today_orders)
    with col6:
        st.metric("💵 Today's Income", f"₹ {today_income:,.2f}")
    
    st.markdown("---")
    
    # Recent orders table
    st.subheader("🆕 Recent Orders")
    recent_orders = conn.execute("""
        SELECT order_no, client_name, client_phone, booking_date, delivery_date, 
               total_bill, paid_amount, balance, status
        FROM orders 
        WHERE user_id=? 
        ORDER BY booking_date DESC 
        LIMIT 10
    """, (st.session_state.user_id,)).fetchall()
    
    if recent_orders:
        df = pd.DataFrame(recent_orders, columns=[
            'Order No', 'Client', 'Phone', 'Booking', 'Delivery', 
            'Total', 'Paid', 'Balance', 'Status'
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No orders found. Create your first order!")
    
    # Monthly income chart
    st.markdown("---")
    st.subheader("📈 Monthly Income Trend")
    
    monthly_data = conn.execute("""
        SELECT strftime('%Y-%m', booking_date) as month, 
               SUM(total_bill) as income
        FROM orders 
        WHERE user_id=? 
        GROUP BY month 
        ORDER BY month DESC 
        LIMIT 6
    """, (st.session_state.user_id,)).fetchall()
    
    if monthly_data:
        months, incomes = zip(*monthly_data)
        chart_data = pd.DataFrame({
            'Month': months,
            'Income': incomes
        })
        
        fig = px.bar(
            chart_data, 
            x='Month', 
            y='Income',
            title='Monthly Income',
            color='Income',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)

def new_order_page():
    """New order page"""
    st.title(f"📝 {st.session_state.shop_name} - New Order")
    
    with st.form("order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate order number
            today = datetime.now()
            order_no = f"ORD{today.strftime('%Y%m%d')}{conn.execute('SELECT COUNT(*) FROM orders WHERE DATE(booking_date)=?', (today.strftime('%Y-%m-%d'),)).fetchone()[0] + 1:03d}"
            
            st.text_input("Order No.", value=order_no, disabled=True)
            client_name = st.text_input("👤 Client Name*", placeholder="Enter client name")
            client_phone = st.text_input("📱 WhatsApp Number", placeholder="+91 9876543210")
            booking_date = st.date_input("📅 Booking Date*", value=today)
        
        with col2:
            delivery_date = st.date_input("📦 Delivery Date*", value=today)
            no_of_suits = st.number_input("👔 No. of Suits*", min_value=1, value=1)
            total_bill = st.number_input("💰 Total Bill (₹)*", min_value=0.0, value=0.0)
            advance_payment = st.number_input("💵 Advance Payment", min_value=0.0, value=0.0, max_value=total_bill)
        
        # Measurements section
        st.markdown("---")
        st.subheader("📏 Measurements (Inches)")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            length = st.text_input("Length", placeholder="e.g., 42 1/2")
        with m_col2:
            sleeves = st.text_input("Sleeves", placeholder="e.g., 25 1/2")
        with m_col3:
            shoulder = st.text_input("Shoulder", placeholder="e.g., 20 1/2")
        with m_col4:
            collar = st.text_input("Collar", placeholder="e.g., 17 1/2")
        
        m_col5, m_col6, m_col7, m_col8 = st.columns(4)
        with m_col5:
            chest = st.text_input("Chest", placeholder="e.g., 48")
        with m_col6:
            lower_chest = st.text_input("Lower Chest", placeholder="e.g., 46")
        with m_col7:
            waist = st.text_input("Waist", placeholder="e.g., 40")
        with m_col8:
            hip_ghera = st.text_input("Hip / Ghera", placeholder="e.g., 28")
        
        notes = st.text_area("📝 Notes", placeholder="Any special instructions...")
        
        submitted = st.form_submit_button("💾 Save Order", type="primary", use_container_width=True)
        
        if submitted:
            if not client_name or not total_bill:
                st.error("❌ Please fill all required fields (marked with *)")
            else:
                try:
                    # Insert order
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO orders (user_id, order_no, client_name, client_phone, 
                                          booking_date, delivery_date, no_of_suits, 
                                          total_bill, paid_amount, balance, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        st.session_state.user_id, order_no, client_name, client_phone,
                        booking_date.strftime('%Y-%m-%d'), delivery_date.strftime('%Y-%m-%d'),
                        no_of_suits, total_bill, advance_payment, total_bill - advance_payment,
                        notes
                    ))
                    
                    order_id = cursor.lastrowid
                    
                    # Insert measurements
                    cursor.execute("""
                        INSERT INTO measurements (order_id, length, sleeves, shoulder, collar, 
                                                chest, lower_chest, waist, hip_ghera)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (order_id, length, sleeves, shoulder, collar, chest, lower_chest, waist, hip_ghera))
                    
                    conn.commit()
                    st.success(f"✅ Order saved successfully! Order No: {order_no}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error saving order: {str(e)}")

def settings_page():
    """Settings page"""
    st.title("⚙️ Settings")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🏪 Shop Settings", "👤 Profile", "🔐 Security"])
    
    with tab1:
        st.subheader("Rename Shop")
        
        current_name = get_shop_name()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            new_name = st.text_input(
                "Enter New Shop Name",
                value=current_name,
                placeholder="e.g., Nasir Tailors"
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
        
        # Shop configuration
        st.markdown("---")
        st.subheader("Shop Configuration")
        
        config = conn.execute(
            "SELECT currency, date_format, units FROM shop_config WHERE user_id=?",
            (st.session_state.user_id,)
        ).fetchone()
        
        if config:
            col3, col4, col5 = st.columns(3)
            
            with col3:
                currency = st.selectbox(
                    "💰 Currency",
                    ["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)"],
                    index=["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)"].index(config[0])
                )
            
            with col4:
                date_fmt = st.selectbox(
                    "📅 Date Format",
                    ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD", "YYYY/MM/DD"],
                    index=["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD", "YYYY/MM/DD"].index(config[1])
                )
            
            with col5:
                units = st.selectbox(
                    "📏 Units",
                    ["Inches", "Centimeters", "Both"],
                    index=["Inches", "Centimeters", "Both"].index(config[2])
                )
            
            if st.button("💾 Save Configuration", type="primary"):
                conn.execute("""
                    UPDATE shop_config 
                    SET currency=?, date_format=?, units=?, updated_at=CURRENT_TIMESTAMP
                    WHERE user_id=?
                """, (currency, date_fmt, units, st.session_state.user_id))
                conn.commit()
                st.success("✅ Configuration saved successfully!")
    
    with tab2:
        st.subheader("User Profile")
        
        # Get current user info
        user_info = conn.execute(
            "SELECT full_name, email, phone FROM users WHERE id=?",
            (st.session_state.user_id,)
        ).fetchone()
        
        if user_info:
            with st.form("profile_form"):
                full_name = st.text_input("Full Name", value=user_info[0])
                email = st.text_input("Email", value=user_info[1], disabled=True)
                phone = st.text_input("Phone", value=user_info[2])
                
                if st.form_submit_button("📝 Update Profile", type="primary"):
                    conn.execute(
                        "UPDATE users SET full_name=?, phone=? WHERE id=?",
                        (full_name, phone, st.session_state.user_id)
                    )
                    conn.commit()
                    st.session_state.user_name = full_name
                    st.success("✅ Profile updated successfully!")
    
    with tab3:
        st.subheader("Change Password")
        
        with st.form("password_form"):
            current_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("🔑 Change Password", type="primary"):
                if not all([current_pass, new_pass, confirm_pass]):
                    st.error("❌ Please fill all fields")
                elif new_pass != confirm_pass:
                    st.error("❌ New passwords don't match")
                elif len(new_pass) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    # Verify current password
                    current_db_pass = conn.execute(
                        "SELECT password FROM users WHERE id=?",
                        (st.session_state.user_id,)
                    ).fetchone()[0]
                    
                    if current_pass == current_db_pass:
                        conn.execute(
                            "UPDATE users SET password=? WHERE id=?",
                            (new_pass, st.session_state.user_id)
                        )
                        conn.commit()
                        st.success("✅ Password changed successfully!")
                    else:
                        st.error("❌ Current password is incorrect")

def main():
    """Main application"""
    # Apply CSS
    apply_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Main app logic
    if not st.session_state.authenticated:
        if st.session_state.current_page == "login":
            login_page()
        elif st.session_state.current_page == "register":
            register_page()
    else:
        # Get current page from sidebar
        current_page = sidebar_navigation()
        
        # Display appropriate page
        if current_page == "dashboard":
            dashboard_page()
        elif current_page == "new_order":
            new_order_page()
        elif current_page == "settings":
            settings_page()
        elif current_page == "customers":
            st.title("👥 Customers")
            st.info("Customers page - Coming Soon!")
        elif current_page == "cashbook":
            st.title("💰 Cashbook")
            st.info("Cashbook page - Coming Soon!")
        elif current_page == "reports":
            st.title("📈 Reports")
            st.info("Reports page - Coming Soon!")

if __name__ == "__main__":
    main()
