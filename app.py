import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# --- Page Config ---
st.set_page_config(page_title="Tailor Master Pro", layout="wide", page_icon="👔")

# --- Custom CSS for Professional UI ---
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    .main { background-color: #0e1117; }
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #d4af37;
    }
    div.stButton > button:first-child {
        background-color: #d4af37; color: black; font-weight: bold;
        border-radius: 8px; border: none; height: 45px;
    }
    .reminder-card {
        background-color: #262730; padding: 10px;
        border-radius: 5px; border-left: 3px solid #ff4b4b; margin-bottom: 5px;
    }
    .shop-title {
        color: #d4af37; font-family: 'Garamond', serif;
        font-size: 45px; font-weight: bold; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Database Setup ---
conn = sqlite3.connect('tailor_ultimate.db', check_same_thread=False)
c = conn.cursor()
# Clients Table
c.execute('''CREATE TABLE IF NOT EXISTS clients 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, 
             suits_count INTEGER, total REAL, advance REAL, prev_balance REAL, remaining REAL, 
             order_date DATE, delivery_date DATE, status TEXT, notes TEXT,
             l TEXT, s TEXT, sh TEXT, cl TEXT, ch TEXT, w TEXT, h TEXT, b TEXT)''')
# Expenses Table
c.execute('''CREATE TABLE IF NOT EXISTS expenses 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, amount REAL, date DATE)''')
conn.commit()

# --- Session State ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- App Logic ---
if not st.session_state['logged_in']:
    st.markdown("<div class='shop-title'>Tailor Master Pro</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.subheader("🔐 Admin Access")
        user = st.text_input("Username")
        pas = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "admin" and pas == "1234":
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("Invalid Credentials")
else:
    # --- Sidebar ---
    st.sidebar.markdown(f"<h1 style='color:#d4af37; text-align:center;'>TM PRO</h1>", unsafe_allow_html=True)
    shop_name = st.sidebar.text_input("Shop Name", "Tailor Master")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Main Menu", 
        ["🏠 Dashboard", "➕ New Order", "💸 Expenses", "📦 Order History", "⚙️ Settings"])
    
    if st.sidebar.button("🔌 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.markdown(f"<div class='shop-title'>{shop_name}</div>", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        # --- CALCULATIONS FOR CARDS ---
        today = date.today().strftime('%Y-%m-%d')
        daily_orders = pd.read_sql(f"SELECT COUNT(*) FROM clients WHERE order_date='{today}'", conn).iloc[0,0]
        daily_income = pd.read_sql(f"SELECT SUM(advance) FROM clients WHERE order_date='{today}'", conn).iloc[0,0] or 0
        total_pending = pd.read_sql("SELECT SUM(remaining) FROM clients", conn).iloc[0,0] or 0
        daily_exp = pd.read_sql(f"SELECT SUM(amount) FROM expenses WHERE date='{today}'", conn).iloc[0,0] or 0

        # --- METRIC CARDS ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Today's Orders", daily_orders)
        col2.metric("💰 Today's Income", f"Rs.{daily_income}")
        col3.metric("📉 Today's Expense", f"Rs.{daily_exp}")
        col4.metric("🛑 Total Recoverable", f"Rs.{total_pending}")

        st.markdown("---")
        
        # --- REMINDERS & SEARCH ---
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            st.subheader("🔍 Client Search & Quick View")
            search = st.text_input("Search by Name or Phone")
            query = "SELECT id, name, phone, delivery_date, remaining, status FROM clients"
            if search:
                query += f" WHERE name LIKE '%{search}%' OR phone LIKE '%{search}%'"
            df = pd.read_sql(query, conn)
            st.dataframe(df, use_container_width=True)

        with right_col:
            st.subheader("🔔 Reminders")
            # Payment Reminders
            pendings = pd.read_sql("SELECT name, remaining FROM clients WHERE remaining > 0 LIMIT 5", conn)
            for _, row in pendings.iterrows():
                st.markdown(f"<div class='reminder-card'>💸 <b>{row['name']}</b>: Pending Rs.{row['remaining']}</div>", unsafe_allow_html=True)
            
            # Delivery Reminders
            upcoming = pd.read_sql(f"SELECT name, delivery_date FROM clients WHERE status='Pending' AND delivery_date >= '{today}' LIMIT 5", conn)
            for _, row in upcoming.iterrows():
                st.markdown(f"<div class='reminder-card'>📅 <b>{row['name']}</b>: Delivery on {row['delivery_date']}</div>", unsafe_allow_html=True)

    elif menu == "➕ New Order":
        st.subheader("📏 Add New Measurement & Order")
        with st.form("order_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                name = st.text_input("Customer Name")
                phone = st.text_input("Mobile No")
            with c2:
                suits = st.number_input("Number of Suits", 1)
                del_date = st.date_input("Delivery Date")
            with c3:
                total = st.number_input("Total Bill", 0.0)
                adv = st.number_input("Advance Payment", 0.0)
            
            st.markdown("### 📏 Measurements")
            m1, m2, m3, m4 = st.columns(4)
            l = m1.text_input("Length"); s = m2.text_input("Sleeves")
            sh = m3.text_input("Shoulder"); cl = m4.text_input("Collar")
            ch = m1.text_input("Chest"); w = m2.text_input("Waist")
            h = m3.text_input("Hip"); b = m4.text_input("Bottom")
            
            notes = st.text_area("Order Special Instructions")
            
            if st.form_submit_button("Submit Order"):
                rem = total - adv
                c.execute('''INSERT INTO clients (name, phone, suits_count, total, advance, remaining, order_date, delivery_date, status, notes, l, s, sh, cl, ch, w, h, b) 
                             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                          (name, phone, suits, total, adv, rem, date.today(), del_date, 'Pending', notes, l, s, sh, cl, ch, w, h, b))
                conn.commit()
                st.success("Order Placed Successfully!")

    elif menu == "💸 Expenses":
        st.subheader("💰 Daily Shop Expenses")
        with st.form("exp_form"):
            title = st.text_input("Expense Description (e.g., Thread, Electricity, Rent)")
            amt = st.number_input("Amount", 0.0)
            if st.form_submit_button("Add Expense"):
                c.execute("INSERT INTO expenses (title, amount, date) VALUES (?,?,?)", (title, amt, date.today()))
                conn.commit()
                st.success("Expense Recorded")
        
        exp_df = pd.read_sql("SELECT * FROM expenses ORDER BY date DESC", conn)
        st.table(exp_df)

    elif menu == "📦 Order History":
        st.subheader("All Time Records")
        all_data = pd.read_sql("SELECT * FROM clients", conn)
        st.dataframe(all_data)
