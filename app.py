import streamlit as st
import pandas as pd
from database import get_connection
from translations import TRANSLATIONS
from styling import apply_style
from measurment import show_order_form # Spelling corrected as per your file structure

# 1. Database Connection & Initial Configuration
conn = get_connection()

# 2. Session States Initialization
# Ensure these session states are initialized at the very start
if 'lang' not in st.session_state: st.session_state.lang = "English"
if 'auth' not in st.session_state: st.session_state.auth = False
if 'view' not in st.session_state: st.session_state.view = "login"

# Get Current Language Dictionary from translations.py
ln = TRANSLATIONS[st.session_state.lang]

# 3. Apply Styling (Wallpapers and Sidebar Language/Theme controls)
# This function also handles the language and mood selection in the sidebar
apply_style(ln)

# Main Content Container Start
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# --- 4. AUTHENTICATION LOGIC (Login, Register, Forgot Password Views) ---
if not st.session_state.auth:
    
    # --- 🟢 LOGIN VIEW ---
    if st.session_state.view == "login":
        st.title(ln['title'])
        le = st.text_input(ln['email'], key="l_e").strip().lower()
        lp = st.text_input(ln['pass'], type="password", key="l_p").strip()
        
        c1, c2 = st.columns(2) # Two columns for Login and Register buttons
        
        # Login Button
        if c1.button(ln['login_btn'], use_container_width=True):
            user = conn.execute("SELECT id, role, shop_name FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
            if user:
                # If login successful, set auth state and user details
                st.session_state.auth = True
                st.session_state.u_id = user[0]
                st.session_state.u_role = user[1]
                st.session_state.u_shop = user[2]
                st.rerun() # Rerun to switch to the authenticated view
            else:
                st.error("❌ Invalid Login Details! Please check your email and password.")
            
        # Register Button (switches view to registration form)
        if c2.button(ln['reg_btn'], use_container_width=True):
            st.session_state.view = "register"
            st.rerun()
            
        # Forgot Password Button (switches view to forgot password form)
        if st.button(ln['forgot_btn'], help="Click to recover your password."): # Removed variant="ghost" for older Streamlit compatibility
            st.session_state.view = "forgot"
            st.rerun()

    # --- 🟡 REGISTER NEW SHOP VIEW ---
    elif st.session_state.view == "register":
        st.title(ln['reg_btn']) # Title for the registration page
        
        # Registration Form Fields
        r_sn = st.text_input(ln['shop'], placeholder="Enter your Shop Name")
        r_ph = st.text_input(ln['phone'], placeholder="e.g., 03xx-xxxxxxx (Optional)")
        r_e = st.text_input(ln['email'], key="r_e").strip().lower() # Email for registration
        r_p = st.text_input(ln['pass'], key="r_p", type="password") # Password for registration
        r_sq = st.text_input(ln['s_q'], placeholder="e.g., Your Mother's Maiden Name?") # Security Question
        r_sa = st.text_input(ln['s_a'], placeholder="Your Answer to Security Question") # Security Answer

        cr1, cr2 = st.columns(2) # Columns for Create Account and Back buttons
        
        # Create Account Button
        if cr1.button("Create Account ✅", use_container_width=True):
            if r_sn and r_e and r_p: # Basic validation for essential fields
                try:
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO users (email, password, shop_name, role, phone, security_q, security_a) 
                        VALUES (?,?,?,?,?,?,?)
                    """, (r_e, r_p, r_sn, 'admin', r_ph, r_sq, r_sa))
                    conn.commit()
                    
                    # Auto-login the new user after successful registration
                    st.session_state.auth = True
                    st.session_state.u_id = cur.lastrowid # Get the ID of the newly inserted user
                    st.session_state.u_role = 'admin'
                    st.session_state.u_shop = r_sn
                    
                    st.success("🎉 Account Created Successfully! Logging you in...")
                    st.rerun() # Rerun to switch to the authenticated view
                except Exception as e:
                    # Handle case where email might already exist or other DB errors
                    st.error(f"⚠️ Registration failed! This email might already be registered. Error: {e}")
            else:
                st.warning("Please fill in all essential fields (Shop Name, Email, Password, Security Answer).")

        # Back to Login Button
        if cr2.button(ln['back'] + " " + ln['login_btn'], use_container_width=True):
            st.session_state.view = "login"
            st.rerun()

    # --- 🔴 FORGOT PASSWORD RECOVERY VIEW ---
    elif st.session_state.view == "forgot":
        st.title(ln['forgot_btn']) # Title for the forgot password page
        
        fe = st.text_input("Enter your registered Email Address for recovery").strip().lower()
        
        if fe: # Only proceed if an email is entered
            user_data = conn.execute("SELECT security_q, security_a, password FROM users WHERE LOWER(email)=?", (fe,)).fetchone()
            
            if user_data: # If email found in DB
                st.info(f"Your Security Question: **{user_data[0]}**")
                recovery_answer = st.text_input("Please enter your Security Answer")
                
                if st.button("Recover Password"):
                    if recovery_answer.lower() == user_data[1].lower(): # Case-insensitive comparison
                        st.success(f"🔓 Your Password is: **{user_data[2]}**")
                    else:
                        st.error("❌ Incorrect Security Answer!")
            else:
                st.error("📧 No account found with that email address.")
        
        # Back to Login Button
        if st.button(ln['back'], help="Go back to the login page."):
            st.session_state.view = "login"
            st.rerun()

# --- 5. AUTHENTICATED USER AREA (Dashboard, New Order, Reports, Settings) ---
else:
    # Sidebar Navigation for logged-in users
    with st.sidebar:
        st.markdown(f"🏪 **{st.session_state.u_shop}**") # Display current shop name
        
        # Menu options (using translated labels)
        menu_options = [ln['dash'], ln['order'], ln['report'], ln['sec']]
        menu = st.radio("MAIN MENU", menu_options)
        
        st.markdown("---")
        # Logout button
        if st.button(ln['logout'], use_container_width=True):
            st.session_state.auth = False # Set authentication to False
            st.rerun() # Rerun to go back to the login page

    # --- Page Content based on Menu Selection ---
    if menu == ln['order']:
        show_order_form(conn, ln) # Calls the function from measurment.py to show the order form
        
    elif menu == ln['dash'] or menu == ln['report']:
        st.header(menu)
        
        # Fetch and display orders for the logged-in user
        user_orders_df = pd.read_sql(
            f"SELECT client_name, client_phone, total_bill, order_date FROM orders WHERE user_id={st.session_state.u_id}", 
            conn
        )
        if not user_orders_df.empty:
            st.dataframe(user_orders_df, use_container_width=True)
        else:
            st.info("No orders found yet. Create your first order using the 'New Order' section!")
            
    elif menu == ln['sec']:
        st.header(ln['sec']) # Security/Settings page
        st.subheader("Account Settings")
        
        # Option to rename the shop
        new_shop_name = st.text_input(ln['rename_shop'], value=st.session_state.u_shop)
        if st.button(ln['update']):
            conn.execute("UPDATE users SET shop_name=? WHERE id=?", (new_shop_name, st.session_state.u_id))
            conn.commit()
            st.session_state.u_shop = new_shop_name # Update session state immediately
            st.success("Shop Name Updated Successfully! ✅")
            st.rerun() # Rerun to reflect changes in sidebar/dashboard
# ... Inside app.py navigation logic ...

elif menu == ln['cashbook']:
    st.header(ln['cashbook'])
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Calculate Today's Income (Sum of paid_amount)
    inc_query = f"SELECT SUM(paid_amount) FROM orders WHERE user_id={st.session_state.u_id} AND order_date='{today}'"
    income = conn.execute(inc_query).fetchone()[0] or 0.0
    
    # Calculate Today's Expenses
    exp_query = f"SELECT SUM(amount) FROM expenses WHERE user_id={st.session_state.u_id} AND exp_date='{today}'"
    expense = conn.execute(exp_query).fetchone()[0] or 0.0
    
    savings = income - expense

    # Display Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric(ln['today_inc'], f"Rs. {income}", delta_color="normal")
    m2.metric(ln['today_exp'], f"Rs. {expense}", delta="-", delta_color="inverse")
    m3.metric(ln['savings'], f"Rs. {savings}")

    st.markdown("---")
    # Add New Expense Form
    with st.expander(ln['add_exp']):
        desc = st.text_input(ln['exp_desc'])
        amt = st.number_input(ln['amount'], min_value=0.0)
        if st.button("Save Expense"):
            conn.execute("INSERT INTO expenses (user_id, description, amount, exp_date) VALUES (?,?,?,?)", 
                         (st.session_state.u_id, desc, amt, today))
            conn.commit()
            st.rerun()
# Main Content Container End
st.markdown('</div>', unsafe_allow_html=True)

