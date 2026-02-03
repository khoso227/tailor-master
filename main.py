import streamlit as st
from auth import check_login
from styling import apply_custom_styles
from database import init_db, get_connection
from datetime import datetime
import pandas as pd

# Import all your modules
try:
    import analytics
    import reports
    import orders
    import client_detail
    import measurement
    import payment
except ImportError as e:
    st.error(f"Module import error: {e}")
    st.info("Please make sure all module files exist")

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
            "🌍 Global Dashboard": "global_dashboard",
            "🏪 Manage Shops": "manage_shops",
            "📊 Platform Analytics": "platform_analytics",
            "👥 All Clients": "all_clients",
            "📄 System Reports": "system_reports",
            "⚙️ System Settings": "system_settings"
        }
    else:
        menu_options = {
            "📊 Dashboard": "dashboard",
            "📋 Orders": "orders",
            "👥 Clients": "clients",
            "➕ New Order": "new_order",
            "💰 Payments": "payments",
            "📦 Inventory": "inventory",
            "📄 Reports": "reports",
            "⚙️ Settings": "settings"
        }
    
    # Create navigation buttons
    for menu_name, menu_id in menu_options.items():
        if st.button(menu_name, use_container_width=True, key=f"nav_{menu_id}"):
            st.session_state.current_page = menu_id
            st.rerun()
    
    # Set default page if not set
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard" if user_role != 'super_admin' else "global_dashboard"
    
    st.markdown("---")
    
    # Quick Actions Section
    st.subheader("⚡ Quick Actions")
    
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button("📝 New Order", use_container_width=True, key="quick_new_order"):
            st.session_state.current_page = "new_order"
            st.rerun()
    
    with col_q2:
        if st.button("👥 Add Client", use_container_width=True, key="quick_add_client"):
            st.session_state.current_page = "clients"
            st.rerun()
    
    # Today's Deliveries Alert
    try:
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
        if st.button("🚪", help="Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.rerun()

# ============================================
# MAIN CONTENT AREA
# ============================================
# Page Router
current_page = st.session_state.get('current_page', 'dashboard')

try:
    if user_role == 'super_admin':
        # Super Admin Pages
        if current_page == "global_dashboard":
            st.title("🌍 Global Dashboard")
            analytics.show_analytics_dashboard()
        
        elif current_page == "manage_shops":
            st.title("🏪 Manage Shops")
            show_shops_management()
        
        elif current_page == "platform_analytics":
            st.title("📊 Platform Analytics")
            analytics.show_global_stats()
        
        elif current_page == "all_clients":
            st.title("👥 All Clients")
            client_detail.show_client_management()
        
        elif current_page == "system_reports":
            st.title("📄 System Reports")
            reports.show_reports_page()
        
        elif current_page == "system_settings":
            st.title("⚙️ System Settings")
            show_system_settings()
        
        else:
            analytics.show_analytics_dashboard()
    
    else:
        # Regular Shopkeeper Pages
        if current_page == "dashboard":
            st.title("📊 Dashboard")
            analytics.show_analytics_dashboard()
        
        elif current_page == "orders":
            st.title("📋 Orders Management")
            orders.show_orders_page()
        
        elif current_page == "clients":
            st.title("👥 Client Management")
            client_detail.show_client_management()
        
        elif current_page == "new_order":
            st.title("➕ New Order")
            conn = get_connection()
            measurement.show_order_form(conn, None)
            conn.close()
        
        elif current_page == "payments":
            st.title("💰 Payments")
            payment.show_payments_page()
        
        elif current_page == "inventory":
            st.title("📦 Inventory")
            show_inventory_page()
        
        elif current_page == "reports":
            st.title("📄 Reports")
            reports.show_reports_page()
        
        elif current_page == "settings":
            st.title("⚙️ Settings")
            show_settings_page()
        
        else:
            analytics.show_analytics_dashboard()

except Exception as e:
    st.error(f"Error loading page: {str(e)}")
    st.info("Loading dashboard as fallback...")
    try:
        analytics.show_analytics_dashboard()
    except:
        st.error("Please check if all modules are properly installed.")

# ============================================
# PAGE FUNCTIONS (Define these functions)
# ============================================
def show_shops_management():
    """Super Admin: Manage shops"""
    st.info("Shop management module coming soon!")
    st.write("Features:")
    st.write("✅ View all registered shops")
    st.write("✅ Add new shops")
    st.write("✅ Manage subscriptions")
    st.write("✅ Shop performance analytics")

def show_system_settings():
    """Super Admin system settings"""
    st.info("System settings module coming soon!")
    st.write("Features:")
    st.write("✅ Platform configuration")
    st.write("✅ Subscription plans")
    st.write("✅ System security")
    st.write("✅ Maintenance tools")

def show_settings_page():
    """Shop settings page"""
    st.info("Shop settings module coming soon!")
    st.write("Features:")
    st.write("✅ Shop profile management")
    st.write("✅ System preferences")
    st.write("✅ Security settings")
    st.write("✅ User management")

def show_inventory_page():
    """Inventory management page"""
    st.info("Inventory management module coming soon!")
    st.write("Features:")
    st.write("✅ Fabric stock management")
    st.write("✅ Raw material tracking")
    st.write("✅ Low stock alerts")
    st.write("✅ Purchase orders")
