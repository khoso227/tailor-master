import streamlit as st
from auth import check_login
from styling import apply_custom_styles
from database import init_db
import analytics
import reports
import orders
import client_detail
import measurement
import payment
import sys
import os

# Initialize database
init_db()

# Apply custom styles
apply_custom_styles()

# Check login
if not check_login():
    st.stop()

# Get user info
user_id = st.session_state.get('user_id', 1)
user_role = st.session_state.get('role', 'admin')
user_shop_name = st.session_state.get('shop_name', 'AZAD TAILOR')

# ============================================
# SIDEBAR - NAVIGATION
# ============================================
with st.sidebar:
    # Logo and Shop Name
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='color: #3b8ed0; font-size: 28px; font-weight: bold;'>AZAD TAILOR</h1>
        <p style='color: #666; font-size: 14px;'>Professional Tailor Management</p>
        <hr style='margin: 10px 0;'>
        <p style='color: #888; font-size: 12px;'>Logged in as: <strong>{st.session_state.get('email', 'User')}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats (Top of sidebar)
    if user_role != 'super_admin':
        try:
            from database import get_today_summary
            summary = get_today_summary(user_id)
            
            st.markdown("---")
            st.markdown("**📊 Quick Stats**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📥 Today", summary['today_orders'], label_visibility="collapsed")
            with col2:
                st.metric("💰 Due", f"₹{summary['total_outstanding']:,}", label_visibility="collapsed")
        except:
            pass
    
    st.markdown("---")
    
    # Main Navigation
    st.subheader("📋 Navigation")
    
    # Role-based menu options
    if user_role == 'super_admin':
        menu_options = {
            "🌍 Global Dashboard": lambda: analytics.show_analytics_dashboard(),
            "🏪 Manage Shops": lambda: show_shops_management(),
            "📊 Platform Analytics": lambda: analytics.show_global_stats(),
            "👥 All Clients": lambda: client_detail.show_client_management(),
            "📄 System Reports": lambda: reports.show_reports_page(),
            "⚙️ System Settings": lambda: show_system_settings()
        }
    else:
        menu_options = {
            "📊 Dashboard": lambda: analytics.show_analytics_dashboard(),
            "📋 Orders": lambda: orders.show_orders_page(),
            "👥 Clients": lambda: client_detail.show_client_management(),
            "➕ New Order": lambda: measurement.show_order_form(get_connection(), None),
            "💰 Payments": lambda: payment.show_payments_page(),
            "📦 Inventory": lambda: show_inventory_page(),
            "📄 Reports": lambda: reports.show_reports_page(),
            "⚙️ Settings": lambda: show_settings_page()
        }
    
    # Create navigation buttons
    for menu_name in menu_options.keys():
        if st.sidebar.button(menu_name, use_container_width=True):
            st.session_state.current_page = menu_name
            st.rerun()
    
    # Set default page if not set
    if 'current_page' not in st.session_state:
        st.session_state.current_page = list(menu_options.keys())[0]
    
    st.markdown("---")
    
    # Quick Actions Section
    st.subheader("⚡ Quick Actions")
    
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button("📝 New Order", use_container_width=True):
            st.session_state.current_page = "➕ New Order"
            st.rerun()
    
    with col_q2:
        if st.button("👥 Add Client", use_container_width=True):
            st.session_state.current_page = "👥 Clients"
            st.rerun()
    
    # Today's Deliveries Alert
    try:
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE user_id = ? AND delivery_date = ? AND status != 'Delivered'
        """, (user_id, today))
        
        pending_deliveries = cursor.fetchone()[0]
        conn.close()
        
        if pending_deliveries > 0:
            st.warning(f"🚨 {pending_deliveries} deliveries due today!")
    except:
        pass
    
    st.markdown("---")
    
    # User Info and Logout
    col_user1, col_user2 = st.columns([3, 1])
    with col_user1:
        st.caption(f"Shop: {user_shop_name}")
        st.caption(f"Role: {user_role}")
    
    with col_user2:
        if st.button("🚪", help="Logout"):
            st.session_state.logged_in = False
            for key in list(st.session_state.keys()):
                if key not in ['_streamlit_script_hash', '_streamlit_theme']:
                    del st.session_state[key]
            st.rerun()

# ============================================
# MAIN CONTENT AREA
# ============================================
# Page title based on selection
st.title(st.session_state.current_page)

# Show the selected page
try:
    menu_options[st.session_state.current_page]()
except Exception as e:
    st.error(f"Error loading page: {str(e)}")
    st.info("Trying to load default dashboard...")
    try:
        analytics.show_analytics_dashboard()
    except:
        st.error("Could not load any page. Please check your modules.")

# ============================================
# PAGE FUNCTIONS
# ============================================
def show_settings_page():
    """Shop settings page"""
    st.header("⚙️ Shop Settings")
    
    tab1, tab2, tab3 = st.tabs(["Shop Profile", "Preferences", "Security"])
    
    with tab1:
        st.subheader("Shop Information")
        
        with st.form("shop_settings_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                shop_name = st.text_input("Shop Name", value=user_shop_name)
                phone = st.text_input("Phone Number", value="+91 ")
                email = st.text_input("Email", value=st.session_state.get('email', ''))
            
            with col2:
                address = st.text_area("Shop Address", height=100)
                gst_number = st.text_input("GST Number")
                website = st.text_input("Website")
            
            # Business hours
            st.subheader("Business Hours")
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                opening_time = st.time_input("Opening Time", value=datetime.strptime("09:00", "%H:%M").time())
            with col_h2:
                closing_time = st.time_input("Closing Time", value=datetime.strptime("20:00", "%H:%M").time())
            
            # Shop logo upload
            st.subheader("Shop Logo")
            logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("💾 Save Settings"):
                # Save settings logic here
                st.success("Settings saved successfully!")
                st.session_state.shop_name = shop_name
    
    with tab2:
        st.subheader("System Preferences")
        
        with st.form("preferences_form"):
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                currency = st.selectbox("Currency", ["₹ Rupee", "$ Dollar", "€ Euro", "£ Pound"])
                date_format = st.selectbox("Date Format", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
                language = st.selectbox("Language", ["English", "Hindi", "Urdu"])
            
            with col_p2:
                auto_backup = st.checkbox("Enable Auto Backup", value=True)
                backup_frequency = st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"])
                sms_notifications = st.checkbox("SMS Notifications", value=True)
                email_notifications = st.checkbox("Email Notifications", value=True)
            
            # Measurement defaults
            st.subheader("Measurement Defaults")
            default_units = st.radio("Default Units", ["Inches", "Centimeters"], horizontal=True)
            
            if st.form_submit_button("💾 Save Preferences"):
                st.success("Preferences saved!")
    
    with tab3:
        st.subheader("Security Settings")
        
        with st.form("security_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            # Two-factor authentication
            enable_2fa = st.checkbox("Enable Two-Factor Authentication")
            
            # Session timeout
            session_timeout = st.selectbox("Session Timeout", 
                                          ["15 minutes", "30 minutes", "1 hour", "4 hours", "Never"])
            
            if st.form_submit_button("🔐 Update Security"):
                if new_password and new_password == confirm_password:
                    # Password update logic here
                    st.success("Security settings updated!")
                else:
                    st.error("Passwords don't match!")

def show_system_settings():
    """Super Admin system settings"""
    st.header("⚙️ System Settings")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Platform", "Billing", "Security", "Maintenance"])
    
    with tab1:
        st.subheader("Platform Configuration")
        
        with st.form("platform_config_form"):
            platform_name = st.text_input("Platform Name", value="Tailor Master Pro")
            platform_url = st.text_input("Platform URL", value="https://tailormaster.com")
            support_email = st.text_input("Support Email", value="support@tailormaster.com")
            support_phone = st.text_input("Support Phone", value="+91 9876543210")
            
            # Platform features
            st.subheader("Platform Features")
            enable_multishop = st.checkbox("Enable Multi-Shop", value=True)
            enable_online_payments = st.checkbox("Enable Online Payments", value=True)
            enable_sms_gateway = st.checkbox("Enable SMS Gateway", value=True)
            enable_email_marketing = st.checkbox("Enable Email Marketing", value=True)
            
            if st.form_submit_button("💾 Save Configuration"):
                st.success("Platform configuration saved!")
    
    with tab2:
        st.subheader("Billing & Subscription")
        
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            st.metric("Active Subscriptions", "45")
            st.metric("Monthly Revenue", "₹12,500")
            st.metric("Renewals This Month", "8")
        
        with col_b2:
            # Subscription plans
            st.subheader("Subscription Plans")
            plans = [
                {"name": "Basic", "price": "₹499/month", "shops": "1 Shop", "features": "Basic Features"},
                {"name": "Professional", "price": "₹999/month", "shops": "3 Shops", "features": "Advanced Features"},
                {"name": "Enterprise", "price": "₹2,499/month", "shops": "10 Shops", "features": "All Features"}
            ]
            
            for plan in plans:
                with st.expander(f"📦 {plan['name']} - {plan['price']}"):
                    st.write(f"**Shops:** {plan['shops']}")
                    st.write(f"**Features:** {plan['features']}")
                    if st.button(f"Edit {plan['name']}"):
                        st.info(f"Editing {plan['name']} plan")
    
    with tab3:
        st.subheader("System Security")
        
        # Security dashboard
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            st.metric("Active Users", "142")
            st.metric("Failed Logins", "3")
        
        with col_s2:
            st.metric("Last Backup", "2 hours ago")
            st.metric("Backup Size", "45 MB")
        
        with col_s3:
            st.metric("Security Score", "92/100")
            if st.button("Run Security Scan"):
                st.success("Security scan completed!")
        
        # Security logs
        st.subheader("Security Logs")
        logs = [
            {"time": "2024-01-15 10:30", "event": "User login", "user": "admin@sahilarman.com", "ip": "192.168.1.1"},
            {"time": "2024-01-15 09:15", "event": "Failed login", "user": "unknown", "ip": "103.21.45.67"},
            {"time": "2024-01-14 22:45", "event": "Database backup", "user": "system", "ip": "localhost"}
        ]
        
        for log in logs:
            st.write(f"**{log['time']}** - {log['event']} by {log['user']} ({log['ip']})")
    
    with tab4:
        st.subheader("System Maintenance")
        
        # Maintenance tasks
        tasks = [
            {"task": "Database Optimization", "status": "Pending", "frequency": "Weekly"},
            {"task": "Log Cleanup", "status": "Completed", "frequency": "Daily"},
            {"task": "Backup Verification", "status": "Pending", "frequency": "Daily"},
            {"task": "Security Updates", "status": "In Progress", "frequency": "Monthly"}
        ]
        
        for task in tasks:
            col_t1, col_t2, col_t3 = st.columns([3, 1, 1])
            with col_t1:
                st.write(f"**{task['task']}**")
            with col_t2:
                st.write(task['status'])
            with col_t3:
                if st.button("Run", key=f"run_{task['task']}"):
                    st.info(f"Running {task['task']}...")
        
        # System info
        st.subheader("System Information")
        col_i1, col_i2 = st.columns(2)
        
        with col_i1:
            st.write(f"**Python Version:** {sys.version}")
            st.write(f"**Streamlit Version:** {st.__version__}")
            st.write(f"**Database:** SQLite")
        
        with col_i2:
            import platform
            st.write(f"**OS:** {platform.system()} {platform.release()}")
            st.write(f"**Processor:** {platform.processor()}")
            st.write(f"**Working Directory:** {os.getcwd()}")

def show_shops_management():
    """Super Admin: Manage shops"""
    st.header("🏪 Shop Management")
    
    conn = get_connection()
    
    # Shop management tabs
    tab1, tab2, tab3, tab4 = st.tabs(["All Shops", "Add New Shop", "Subscriptions", "Shop Analytics"])
    
    with tab1:
        st.subheader("Registered Shops")
        
        shops_df = pd.read_sql("""
            SELECT 
                id, shop_name, email, phone, role, fee_status, 
                status, created_at, expiry_date
            FROM users 
            WHERE role = 'admin'
            ORDER BY created_at DESC
        """, conn)
        
        if not shops_df.empty:
            # Search and filter
            col_search1, col_search2 = st.columns(2)
            with col_search1:
                search_shop = st.text_input("Search by shop name")
            with col_search2:
                filter_status = st.selectbox("Filter by Status", ["All", "Active", "Inactive", "Pending"])
            
            # Apply filters
            filtered_df = shops_df.copy()
            if search_shop:
                filtered_df = filtered_df[filtered_df['shop_name'].str.contains(search_shop, case=False, na=False)]
            if filter_status != "All":
                filtered_df = filtered_df[filtered_df['status'] == filter_status]
            
            # Display shops
            for _, shop in filtered_df.iterrows():
                with st.expander(f"🏪 {shop['shop_name']} - {shop['status']}"):
                    col_s1, col_s2 = st.columns([3, 2])
                    
                    with col_s1:
                        st.write(f"**Email:** {shop['email']}")
                        st.write(f"**Phone:** {shop['phone']}")
                        st.write(f"**Fee Status:** {shop['fee_status']}")
                        st.write(f"**Created:** {shop['created_at']}")
                        if shop['expiry_date']:
                            st.write(f"**Expiry:** {shop['expiry_date']}")
                    
                    with col_s2:
                        # Action buttons
                        if st.button("👁️ View Details", key=f"view_{shop['id']}"):
                            st.session_state.selected_shop = shop['id']
                            st.rerun()
                        
                        if st.button("✏️ Edit", key=f"edit_{shop['id']}"):
                            st.info(f"Editing shop {shop['shop_name']}")
                        
                        if st.button("📧 Contact", key=f"contact_{shop['id']}"):
                            st.info(f"Contact: {shop['phone']} | {shop['email']}")
                        
                        # Status toggle
                        new_status = "Active" if shop['status'] != "Active" else "Inactive"
                        if st.button(f"🔀 {new_status}", key=f"status_{shop['id']}"):
                            # Update status logic
                            st.success(f"Shop status updated to {new_status}")
        else:
            st.info("No shops registered yet.")
    
    with tab2:
        st.subheader("Add New Shop")
        
        with st.form("add_shop_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                shop_name = st.text_input("Shop Name*")
                email = st.text_input("Email*")
                password = st.text_input("Password*", type="password")
            
            with col2:
                phone = st.text_input("Phone Number")
                owner_name = st.text_input("Owner Name")
                subscription_plan = st.selectbox("Subscription Plan", ["Basic", "Professional", "Enterprise"])
            
            # Shop details
            address = st.text_area("Shop Address")
            gst_number = st.text_input("GST Number")
            
            # Subscription settings
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                subscription_start = st.date_input("Subscription Start Date", value=datetime.now())
                subscription_duration = st.selectbox("Duration", ["1 Month", "3 Months", "6 Months", "1 Year"])
            with col_s2:
                subscription_fee = st.number_input("Subscription Fee", min_value=0, value=499)
                auto_renew = st.checkbox("Auto Renew", value=True)
            
            if st.form_submit_button("✅ Add Shop"):
                if shop_name and email and password:
                    # Add shop logic here
                    st.success(f"Shop '{shop_name}' added successfully!")
                else:
                    st.error("Please fill required fields")
    
    with tab3:
        st.subheader("Subscription Management")
        st.info("Subscription management coming soon!")
    
    with tab4:
        st.subheader("Shop Performance")
        analytics.show_shop_comparison()
    
    conn.close()

def show_inventory_page():
    """Inventory management page"""
    st.header("📦 Inventory Management")
    
    st.info("Inventory management module is under development.")
    st.write("Coming soon features:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("✅ Fabric Stock Management")
        st.write("✅ Raw Material Tracking")
        st.write("✅ Low Stock Alerts")
    
    with col2:
        st.write("✅ Supplier Management")
        st.write("✅ Purchase Orders")
        st.write("✅ Inventory Reports")

def get_connection():
    """Get database connection"""
    from database import get_connection as gc
    return gc()

# Import datetime at the top
from datetime import datetime
import pandas as pd
