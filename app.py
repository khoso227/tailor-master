import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_connection
from translations import TRANSLATIONS
from styling import apply_style
from measurment import show_order_form # Spelling as per your file structure

# 1. Database Connection & Initial Configuration
conn = get_connection()

# 2. Session States Initialization
if 'lang' not in st.session_state: st.session_state.lang = "English"
if 'auth' not in st.session_state: st.session_state.auth = False
if 'view' not in st.session_state: st.session_state.view = "login"

# Get Current Language Dictionary from translations.py
ln = TRANSLATIONS[st.session_state.lang]

# 3. Apply Styling (Wallpapers & Sidebar Controls)
apply_style(ln)

# Main Content Container Start
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# --- 4. AUTHENTICATION LOGIC (Logged Out Views) ---
if not st.session_state.auth:
    
    # --- 🟢 LOGIN VIEW ---
    if st.session_state.view == "login":
        st.title(ln['title'])
        le = st.text_input(ln['email'], key="l_e").strip().lower()
        lp = st.text_input(ln['pass'], type="password", key="l_p").strip()
        
        c1, c2 = st.columns(2)
        if c1.button(ln['login_btn'], use_container_width=True):
            user = conn.execute("SELECT id, role, shop_name FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
            if user:
                st.session_state.auth, st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = True, user[0], user[1], user[2]
                st.rerun()
            else:
                st.error("❌ Invalid Login Details!")
            
        if c2.button(ln['reg_btn'], use_container_width=True):
            st.session_state.view = "register"
            st.rerun()
            
        if st.button(ln['forgot_btn']):
            st.session_state.view = "forgot"
            st.rerun()

    # --- 🟡 REGISTER VIEW ---
    elif st.session_state.view == "register":
        st.title(ln['reg_btn'])
        r_sn = st.text_input(ln['shop'])
        r_ph = st.text_input(ln['phone'])
        r_e = st.text_input(ln['email'], key="r_e").strip().lower()
        r_p = st.text_input(ln['pass'], key="r_p", type="password")
        r_sq = st.text_input(ln['s_q'])
        r_sa = st.text_input(ln['s_a'])

        cr1, cr2 = st.columns(2)
        if cr1.button("Create Account ✅", use_container_width=True):
            if r_sn and r_e and r_p:
                try:
                    cur = conn.cursor()
                    cur.execute("""INSERT INTO users (email, password, shop_name, role, phone, security_q, security_a) 
                                   VALUES (?,?,?,?,?,?,?)""", (r_e, r_p, r_sn, 'admin', r_ph, r_sq, r_sa))
                    conn.commit()
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = cur.lastrowid, 'admin', r_sn
                    st.rerun()
                except: st.error("⚠️ Email already exists!")
            else: st.warning("Please fill essential fields!")

        if cr2.button("← Back to Login", use_container_width=True):
            st.session_state.view = "login"; st.rerun()

    # --- 🔴 FORGOT PASSWORD VIEW ---
    elif st.session_state.view == "forgot":
        st.title(ln['forgot_btn'])
        fe = st.text_input("Enter Recovery Email").strip().lower()
        if fe:
            u = conn.execute("SELECT security_q, security_a, password FROM users WHERE LOWER(email)=?", (fe,)).fetchone()
            if u:
                st.info(f"Question: {u[0]}")
                ans = st.text_input("Answer")
                if st.button("Recover Password"):
                    if ans.lower() == u[1].lower(): st.success(f"Password: {u[2]}")
                    else: st.error("Wrong Answer!")
        if st.button("← Back"):
            st.session_state.view = "login"; st.rerun()

# --- 5. AUTHENTICATED AREA (Logged In Views) ---
else:
    with st.sidebar:
        st.markdown(f"🏪 **{st.session_state.u_shop}**")
        # Sidebar Menu with Cashbook
        menu_options = [ln['dash'], ln['order'], ln['cashbook'], ln['report'], ln['sec']]
        menu = st.radio("Navigation", menu_options)
        
        st.markdown("---")
        if st.button(ln['logout'], use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    # --- 🔵 NEW ORDER PAGE ---
    if menu == ln['order']:
        show_order_form(conn, ln)
        
    # --- 💰 CASHBOOK PAGE (Financial Tracking) ---
    elif menu == ln['cashbook']:
        st.header(ln['cashbook'])
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate Income from Orders
        income = conn.execute(f"SELECT SUM(paid_amount) FROM orders WHERE user_id={st.session_state.u_id} AND order_date='{today}'").fetchone()[0] or 0.0
        
        # Calculate Expenses
        expense = conn.execute(f"SELECT SUM(amount) FROM expenses WHERE user_id={st.session_state.u_id} AND exp_date='{today}'").fetchone()[0] or 0.0
        
        net_savings = income - expense

        # Metrics Display
        m1, m2, m3 = st.columns(3)
        m1.metric(ln['today_inc'], f"Rs. {income}")
        m2.metric(ln['today_exp'], f"Rs. {expense}", delta=f"-{expense}", delta_color="inverse")
        m3.metric(ln['savings'], f"Rs. {net_savings}")

        st.markdown("---")
        # Add Expense Form
        with st.expander(ln['add_exp']):
            with st.form("exp_form"):
                desc = st.text_input(ln['exp_desc'])
                amt = st.number_input(ln['amount'], min_value=0.0)
                if st.form_submit_button("Save"):
                    conn.execute("INSERT INTO expenses (user_id, description, amount, exp_date) VALUES (?,?,?,?)", 
                                 (st.session_state.u_id, desc, amt, today))
                    conn.commit()
                    st.rerun()

    # --- 🟢 DASHBOARD & REPORTS ---
    elif menu == ln['dash'] or menu == ln['report']:
        st.header(menu)
        query = f"SELECT client_name, client_phone, total_bill, paid_amount, balance, order_date FROM orders WHERE user_id={st.session_state.u_id}"
        df = pd.read_sql(query, conn)
        st.dataframe(df, use_container_width=True)
            
    # --- ⚙️ SECURITY / SETTINGS ---
    elif menu == ln['sec']:
        st.header(ln['sec'])
        new_sn = st.text_input(ln['rename_shop'], value=st.session_state.u_shop)
        if st.button(ln['update']):
            conn.execute("UPDATE users SET shop_name=? WHERE id=?", (new_sn, st.session_state.u_id))
            conn.commit()
            st.session_state.u_shop = new_sn
            st.success("Shop Renamed Successfully! ✅")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
