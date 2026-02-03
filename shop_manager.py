import streamlit as st
import json
import os
import hashlib
from datetime import datetime

class ShopManager:
    def __init__(self):
        self.config_file = 'shop_config.json'
        self.users_file = 'users.json'
        self.init_files()
    
    def init_files(self):
        """Initialize configuration files if they don't exist"""
        if not os.path.exists(self.config_file):
            default_config = {
                'shop_name': 'AZAD TAILOR',
                'currency': '₹ (INR)',
                'date_format': 'YYYY/MM/DD',
                'auto_backup': True,
                'created_at': str(datetime.now())
            }
            self.save_config(default_config)
        
        if not os.path.exists(self.users_file):
            # Create default admin user
            default_users = {
                'users': [
                    {
                        'username': 'admin',
                        'password': self.hash_password('admin123'),
                        'email': 'admin@tailor.com',
                        'full_name': 'Nasir',
                        'role': 'admin',
                        'created_at': str(datetime.now()),
                        'last_login': None
                    }
                ]
            }
            self.save_users(default_users)
    
    def hash_password(self, password):
        """Hash password for security"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def save_config(self, config):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_users(self, users_data):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=4)
    
    def load_users(self):
        """Load users from file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {'users': []}
    
    def get_shop_name(self):
        """Get current shop name"""
        config = self.load_config()
        return config.get('shop_name', 'AZAD TAILOR')
    
    def update_shop_name(self, new_name):
        """Update shop name"""
        config = self.load_config()
        config['shop_name'] = new_name
        config['updated_at'] = str(datetime.now())
        self.save_config(config)
        
        # Update session state immediately
        if 'shop_name' in st.session_state:
            st.session_state.shop_name = new_name
        
        return True
    
    def get_current_user(self):
        """Get current logged in user"""
        return st.session_state.get('current_user', {})
    
    def update_user_profile(self, username, updates):
        """Update user profile information"""
        users_data = self.load_users()
        
        for user in users_data['users']:
            if user['username'] == username:
                user.update(updates)
                user['updated_at'] = str(datetime.now())
                self.save_users(users_data)
                
                # Update session state
                if 'current_user' in st.session_state:
                    st.session_state.current_user.update(updates)
                
                return True
        return False
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        users_data = self.load_users()
        
        for user in users_data['users']:
            if user['username'] == username:
                # Verify old password
                if user['password'] == self.hash_password(old_password):
                    user['password'] = self.hash_password(new_password)
                    user['updated_at'] = str(datetime.now())
                    self.save_users(users_data)
                    return True, "Password changed successfully"
                else:
                    return False, "Old password is incorrect"
        
        return False, "User not found"

# Initialize shop manager
shop_manager = ShopManager()

# ========== SECURITY/SETTINGS PAGE ==========
def security_settings_page():
    """Main security and settings page"""
    
    # Initialize session state
    if 'shop_name' not in st.session_state:
        st.session_state.shop_name = shop_manager.get_shop_name()
    
    if 'current_user' not in st.session_state:
        # Default user (you should implement proper login)
        st.session_state.current_user = {
            'username': 'admin',
            'full_name': 'Nasir',
            'email': 'admin@tailor.com',
            'role': 'admin'
        }
    
    st.title("🔒 Security / Settings")
    
    # Create tabs for different settings
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏪 Shop Settings", 
        "👤 User Profile", 
        "👥 User Management", 
        "⚙️ App Settings"
    ])
    
    # ===== TAB 1: SHOP SETTINGS =====
    with tab1:
        st.subheader("Rename Shop")
        st.markdown("---")
        
        current_shop_name = shop_manager.get_shop_name()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            new_shop_name = st.text_input(
                "Enter New Shop Name",
                value=current_shop_name,
                key="shop_name_input",
                help="Enter the new name for your tailoring shop"
            )
        
        with col2:
            if st.button("🔄 Update Name", use_container_width=True, type="primary"):
                if new_shop_name and new_shop_name.strip() != "":
                    if new_shop_name != current_shop_name:
                        if shop_manager.update_shop_name(new_shop_name):
                            st.success(f"✅ Shop name updated to: **{new_shop_name}**")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update shop name")
                    else:
                        st.warning("⚠️ Please enter a different name")
                else:
                    st.warning("⚠️ Shop name cannot be empty")
        
        st.markdown(f"**Current Shop Name:** `{current_shop_name}`")
        
        # Shop Information
        st.markdown("---")
        st.subheader("📋 Shop Information")
        
        col1, col2 = st.columns(2)
        with col1:
            shop_address = st.text_area(
                "Shop Address",
                value="123 Tailor Street, Fashion City",
                height=100
            )
        
        with col2:
            shop_phone = st.text_input("Phone Number", value="+91 9876543210")
            shop_email = st.text_input("Email", value="contact@azadtailor.com")
        
        if st.button("💾 Save Shop Info", use_container_width=True):
            st.success("✅ Shop information saved!")
    
    # ===== TAB 2: USER PROFILE =====
    with tab2:
        current_user = st.session_state.current_user
        
        st.subheader("👤 Your Profile")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name", 
                value=current_user.get('full_name', 'Nasir'),
                key="profile_name"
            )
            
            email = st.text_input(
                "Email Address",
                value=current_user.get('email', 'admin@tailor.com'),
                key="profile_email"
            )
            
            phone = st.text_input(
                "Phone Number",
                value=current_user.get('phone', ''),
                key="profile_phone"
            )
        
        with col2:
            username = st.text_input(
                "Username",
                value=current_user.get('username', 'admin'),
                disabled=True,
                help="Username cannot be changed"
            )
            
            role = st.text_input(
                "Role",
                value=current_user.get('role', 'admin').title(),
                disabled=True
            )
            
            st.markdown("**Last Login:** " + 
                       (current_user.get('last_login', 'Never') or 'Never'))
        
        # Update Profile Button
        if st.button("📝 Update Profile", use_container_width=True, type="primary"):
            updates = {
                'full_name': full_name,
                'email': email,
                'phone': phone
            }
            
            if shop_manager.update_user_profile(current_user['username'], updates):
                st.success("✅ Profile updated successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to update profile")
        
        # Change Password Section
        st.markdown("---")
        st.subheader("🔐 Change Password")
        
        col1, col2 = st.columns(2)
        with col1:
            old_password = st.text_input(
                "Current Password", 
                type="password",
                key="old_pass"
            )
        
        with col2:
            new_password = st.text_input(
                "New Password", 
                type="password",
                key="new_pass"
            )
        
        confirm_password = st.text_input(
            "Confirm New Password", 
            type="password",
            key="confirm_pass"
        )
        
        if st.button("🔑 Change Password", use_container_width=True):
            if not old_password or not new_password:
                st.warning("⚠️ Please fill all password fields")
            elif new_password != confirm_password:
                st.warning("⚠️ New passwords don't match")
            elif len(new_password) < 6:
                st.warning("⚠️ Password must be at least 6 characters")
            else:
                success, message = shop_manager.change_password(
                    current_user['username'], 
                    old_password, 
                    new_password
                )
                
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
    
    # ===== TAB 3: USER MANAGEMENT =====
    with tab3:
        if current_user.get('role') != 'admin':
            st.warning("⛔ Admin access required to manage users")
        else:
            st.subheader("👥 User Management")
            st.markdown("---")
            
            # List all users
            users_data = shop_manager.load_users()
            
            st.write(f"**Total Users:** {len(users_data['users'])}")
            
            # Display users in a table
            user_list = []
            for user in users_data['users']:
                user_list.append({
                    'Username': user['username'],
                    'Full Name': user.get('full_name', ''),
                    'Email': user.get('email', ''),
                    'Role': user.get('role', 'user').title(),
                    'Created': user.get('created_at', '')[:10]
                })
            
            if user_list:
                st.dataframe(user_list, use_container_width=True)
            else:
                st.info("No users found")
            
            # Add New User
            st.markdown("---")
            st.subheader("➕ Add New User")
            
            with st.form("add_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_username = st.text_input("Username*")
                    new_fullname = st.text_input("Full Name")
                    new_email = st.text_input("Email")
                
                with col2:
                    new_password = st.text_input("Password*", type="password")
                    new_role = st.selectbox("Role", ["user", "tailor", "admin"])
                
                submitted = st.form_submit_button("👥 Add User", type="primary")
                
                if submitted:
                    if new_username and new_password:
                        # Check if username exists
                        users_data = shop_manager.load_users()
                        existing_usernames = [u['username'] for u in users_data['users']]
                        
                        if new_username in existing_usernames:
                            st.error("❌ Username already exists")
                        else:
                            new_user = {
                                'username': new_username,
                                'password': shop_manager.hash_password(new_password),
                                'full_name': new_fullname,
                                'email': new_email,
                                'role': new_role,
                                'created_at': str(datetime.now()),
                                'last_login': None
                            }
                            
                            users_data['users'].append(new_user)
                            shop_manager.save_users(users_data)
                            st.success(f"✅ User '{new_username}' added successfully!")
                            st.rerun()
                    else:
                        st.warning("⚠️ Username and password are required")
    
    # ===== TAB 4: APP SETTINGS =====
    with tab4:
        st.subheader("⚙️ Application Settings")
        st.markdown("---")
        
        config = shop_manager.load_config()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Currency settings
            currency = st.selectbox(
                "💰 Default Currency",
                ["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)", "₨ (PKR)", "৳ (BDT)"],
                index=["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)", "₨ (PKR)", "৳ (BDT)"].index(
                    config.get('currency', '₹ (INR)')
                )
            )
            
            # Date format
            date_format = st.selectbox(
                "📅 Date Format",
                ["YYYY/MM/DD", "DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"],
                index=["YYYY/MM/DD", "DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"].index(
                    config.get('date_format', 'YYYY/MM/DD')
                )
            )
            
            # Auto backup
            auto_backup = st.checkbox(
                "💾 Enable Auto Backup",
                value=config.get('auto_backup', True)
            )
        
        with col2:
            # Measurement units
            units = st.selectbox(
                "📏 Default Measurement Units",
                ["Inches", "Centimeters", "Both"],
                index=0
            )
            
            # Language
            language = st.selectbox(
                "🌐 Language",
                ["English", "Hindi", "Urdu", "Arabic"],
                index=0
            )
            
            # Theme
            theme = st.selectbox(
                "🎨 Theme",
                ["Light", "Dark", "Auto"],
                index=0
            )
        
        # Save all settings
        if st.button("💾 Save All Settings", use_container_width=True, type="primary"):
            config.update({
                'currency': currency,
                'date_format': date_format,
                'auto_backup': auto_backup,
                'units': units,
                'language': language,
                'theme': theme,
                'settings_updated': str(datetime.now())
            })
            
            shop_manager.save_config(config)
            st.success("✅ Settings saved successfully!")

# ========== HELPER FUNCTIONS FOR OTHER PAGES ==========
def get_shop_name():
    """Get current shop name for display"""
    if 'shop_name' not in st.session_state:
        st.session_state.shop_name = shop_manager.get_shop_name()
    return st.session_state.shop_name

def get_current_user():
    """Get current user info"""
    if 'current_user' not in st.session_state:
        # Default user
        st.session_state.current_user = {
            'username': 'admin',
            'full_name': 'Nasir',
            'email': 'admin@tailor.com',
            'role': 'admin'
        }
    return st.session_state.current_user

def display_shop_header():
    """Display shop header in any page"""
    shop_name = get_shop_name()
    current_user = get_current_user()
    
    # Display shop name and user info
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.title(f"{shop_name} - Management System")
    
    with col2:
        st.markdown(f"**👤 User:** {current_user.get('full_name', 'Admin')}")
        st.markdown(f"**🏪 Shop:** {shop_name}")
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session and redirect to login
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    return shop_name, current_user