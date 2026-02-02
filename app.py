import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import urllib.parse

# --- Page Config ---
st.set_page_config(page_title="Tailor Master Pro", layout="wide", page_icon="👔")

# --- Modern CSS for Premium Look ---
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    .main { background: linear-gradient(to bottom, #121212, #1a1a1a); color: white; }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px; border-radius: 15px;
        border: 1px solid rgba(212, 175, 55, 0.3);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div.stButton > button {
        background: linear-gradient(135deg, #d4af37 0%, #b8860b 100%);
        color: black !important; font-weight: bold; border-radius: 12px;
        border: none; transition: 0.3s; height: 45px; width: 100%;
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(212,175,55,0.4); }
    .sidebar-box { padding: 20px; background: #000; border-radius: 15px; margin-bottom: 20px; border: 1px solid #333; }
    .whatsapp-btn {
        background-color: #25d366; color: white; padding: 10px;
        border-radius: 8px; text-decoration: none; display: inline-block; font-weight: bold;
    }
    .shop-title {
        background: -webkit-linear-gradient(#d4af37, #f7e7b4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 50px; font-weight: 800; text-align: center; margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Database Setup ---
conn = sqlite3.connect('tailor_ultimate_v3.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS clients 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, suits_count INTEGER, 
             total REAL, advance REAL, prev_balance REAL, remaining REAL, 
             order_date DATE, delivery_date DATE, status TEXT, notes TEXT,
             m1 TEXT, m2 TEXT, m3 TEXT, m4 TEXT, m5 TEXT, m6 TEXT, m7 TEXT, m8 TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, shop_name TEXT, password TEXT, m_labels TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, title TEXT, amount REAL, date DATE)''')

# Initial Settings check
if not c.execute("SELECT * FROM settings").fetchone():
    c.execute("INSERT INTO settings (id, shop_name, password, m_labels) VALUES (1, 'Tailor Master', '1234', 'Length,Sleeves,Shoulder,Collar,Chest,Waist,Hip,Bottom')")
    conn.commit()

# --- Load Settings ---
set_data = c.execute("SELECT * FROM settings WHERE id=1").fetchone()
current_shop_name = set_data[1]
current_pass = set_data[2]
labels = set_data[3].split(',')

# --- App Logic ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown(f"<div class='shop-title'>{current_shop_name} Pro</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<div class='sidebar-box'>", unsafe_allow_html=True)
        st.subheader("🔐 Staff Login")
        user = st.text_input("Username", placeholder="admin")
        pas = st.text_input("Password", type="password")
        
        if st.button("Sign In"):
            if pas == current_pass:
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("Wrong Password!")
        
        # Forgot Password Section
        with st.expander("Forgot Password?"):
            master_key = st.text_input("Enter Master Recovery Key", type="password", help="Default is: MASTER2026")
            if st.button("Reset Password"):
                if master_key == "MASTER2026":
                    st.warning(f"Your Password is: {current_pass}")
                else: st.error("Invalid Master Key!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- Professional Sidebar ---
    st.sidebar.markdown(f"<h2 style='color:#d4af37; text-align:center;'>{current_shop_name}</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    menu = st.sidebar.selectbox("Navigate Menu", ["🏠 Dashboard", "➕ New Order", "💸 Expenses", "📦 Order History", "⚙️ Custom Settings"])
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🔌 Logout System"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.markdown(f"<div class='shop-title'>{current_shop_name}</div>", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        # Metrics Calculation
        today = date.today().strftime('%Y-%m-%d')
        daily_inc = pd.read_sql(f"SELECT SUM(advance) FROM clients WHERE order_date='{today}'", conn).iloc[0,0] or 0
        total_rec = pd.read_sql("SELECT SUM(remaining) FROM clients", conn).iloc[0,0] or 0
        daily_exp = pd.read_sql(f"SELECT SUM(amount) FROM expenses WHERE date='{today}'", conn).iloc[0,0] or 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Today's Income", f"Rs.{daily_inc}")
        c2.metric("📉 Today's Expense", f"Rs.{daily_exp}")
        c3.metric("🛑 Pending Recovery", f"Rs.{total_rec}")

        st.markdown("---")
        l_col, r_col = st.columns([2, 1])
        with l_col:
            st.subheader("🔍 Client Records")
            search = st.text_input("Search Name/Mobile")
            q = f"SELECT id, name, phone, delivery_date, remaining FROM clients"
            if search: q += f" WHERE name LIKE '%{search}%' OR phone LIKE '%{search}%'"
            st.dataframe(pd.read_sql(q, conn), use_container_width=True)
        
        with r_col:
            st.subheader("🔔 Reminders")
            pendings = pd.read_sql("SELECT name, phone, remaining FROM clients WHERE remaining > 0 LIMIT 5", conn)
            for _, r in pendings.iterrows():
                msg = f"Dear {r['name']}, your remaining balance at {current_shop_name} is Rs.{r['remaining']}. Please clear it soon."
                url = f"https://wa.me/{r['phone']}?text={urllib.parse.quote(msg)}"
                st.markdown(f"**{r['name']}** (Rs.{r['remaining']})")
                st.markdown(f"<a href='{url}' target='_blank' class='whatsapp-btn'>💬 Remind on WhatsApp</a>", unsafe_allow_html=True)

    elif menu == "➕ New Order":
        st.subheader("📏 Create New Order")
        with st.form("new_order"):
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Client Name")
            phone = c2.text_input("WhatsApp Number (with Country Code)")
            suits = c3.number_input("Suits Count", 1)
            
            c1, c2, c3 = st.columns(3)
            total = c1.number_input("Total Bill")
            adv = c2.number_input("Advance")
            prev = c3.number_input("Old Balance")
            del_date = st.date_input("Delivery Date")
            
            st.markdown("### 📏 Measurements")
            m_cols = st.columns(4)
            m_vals = []
            for i in range(8):
                label = labels[i] if i < len(labels) else f"Field {i+1}"
                val = m_cols[i%4].text_input(label)
                m_vals.append(val)
            
            notes = st.text_area("Order Details")
            if st.form_submit_button("Submit Order"):
                rem = (total + prev) - adv
                c.execute(f"INSERT INTO clients (name, phone, suits_count, total, advance, prev_balance, remaining, order_date, delivery_date, status, notes, m1, m2, m3, m4, m5, m6, m7, m8) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (name, phone, suits, total, adv, prev, rem, date.today(), del_date, 'Pending', notes, *m_vals))
                conn.commit()
                st.success("Order Saved!")
                welcome_msg = f"Welcome to {current_shop_name}! Your order for {suits} suits is booked. Total: {total}, Advance: {adv}. Delivery on {del_date}."
                wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(welcome_msg)}"
                st.markdown(f"<a href='{wa_url}' target='_blank' class='whatsapp-btn'>✅ Send Welcome WhatsApp</a>", unsafe_allow_html=True)

    elif menu == "⚙️ Custom Settings":
        st.subheader("🛠️ Professional System Customization")
        with st.form("set_form"):
            new_name = st.text_input("Change Shop Name", current_shop_name)
            new_pass = st.text_input("Change Admin Password", current_pass)
            new_labels = st.text_area("Measurement Labels (Comma separated)", ",".join(labels))
            if st.form_submit_button("Update System"):
                c.execute("UPDATE settings SET shop_name=?, password=?, m_labels=? WHERE id=1", (new_name, new_pass, new_labels))
                conn.commit()
                st.success("Settings Updated! Please refresh.")

    elif menu == "💸 Expenses":
        st.subheader("Expenses")
        with st.form("ex"):
            t = st.text_input("Item Name"); a = st.number_input("Price")
            if st.form_submit_button("Add"):
                c.execute("INSERT INTO expenses (title, amount, date) VALUES (?,?,?)", (t, a, date.today()))
                conn.commit(); st.success("Added")
        st.table(pd.read_sql("SELECT * FROM expenses", conn))

    elif menu == "📦 Order History":
        st.subheader("History")
        st.dataframe(pd.read_sql("SELECT * FROM clients", conn))
