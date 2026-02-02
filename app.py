import streamlit as st
import sqlite3
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Tailor Master Pro", layout="wide", page_icon="🧵")

# --- Custom CSS for Stylish Look ---
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;} /* Hide default menu */
    .main { background-color: #0e1117; }
    div.stButton > button:first-child {
        background-color: #d4af37; color: black; font-weight: bold;
        border-radius: 10px; width: 100%; border: none;
    }
    .client-card {
        background-color: #1e1e1e; border-left: 5px solid #d4af37;
        padding: 20px; border-radius: 10px; margin-bottom: 15px;
    }
    .shop-title {
        color: #d4af37; font-family: 'Times New Roman';
        font-size: 45px; font-weight: bold; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Database Setup ---
conn = sqlite3.connect('tailor_pro_v2.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS clients 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, 
             length TEXT, sleeves TEXT, shoulder TEXT, collar TEXT, chest TEXT, 
             waist TEXT, hip TEXT, bottom TEXT, suits_count INTEGER,
             total REAL, advance REAL, prev_balance REAL, remaining REAL, notes TEXT)''')
conn.commit()

# --- Session State for Login ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- Logout Function ---
def logout():
    st.session_state['logged_in'] = False
    st.rerun()

# --- MAIN APP LOGIC ---

# 1. LOGIN SCREEN (If not logged in)
if not st.session_state['logged_in']:
    st.markdown("<div class='shop-title'>Tailor Master Pro</div>", unsafe_allow_html=True)
    st.write("---")
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.subheader("🔑 Admin Login")
        user = st.text_input("Username")
        pas = st.text_input("Password", type="password")
        if st.button("Login Now"):
            if user == "admin" and pas == "1234":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Ghalat Username ya Password!")

# 2. DASHBOARD (After Login)
else:
    # Custom Sidebar
    shop_name = st.sidebar.text_input("Shop Name", "Tailor Master")
    st.sidebar.markdown(f"### Welcome, Admin")
    menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "➕ Add New Client", "📑 All Records", "⚙️ Settings"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        logout()

    st.markdown(f"<div class='shop-title'>{shop_name}</div>", unsafe_allow_html=True)

    if menu == "📊 Dashboard":
        st.subheader("📋 Recent Customers & Search")
        search = st.text_input("🔍 Search Client by Name or Mobile")
        
        query = "SELECT id, name, phone, remaining FROM clients ORDER BY id DESC"
        if search:
            query = f"SELECT id, name, phone, remaining FROM clients WHERE name LIKE '%{search}%' OR phone LIKE '%{search}%'"
        
        df = pd.read_sql(query, conn)
        
        if not df.empty:
            # Table View
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            # Select Client to View Details
            selected_client = st.selectbox("Select Customer to View Full Details", df['name'].tolist())
            if st.button("View Full Profile"):
                data = c.execute("SELECT * FROM clients WHERE name=?", (selected_client,)).fetchone()
                if data:
                    st.markdown(f"""
                    <div class="client-card">
                        <h3>👤 {data[1]}</h3>
                        <p>📞 <b>Phone:</b> {data[2]} | 👔 <b>Suits:</b> {data[11]}</p>
                        <hr>
                        <p>📏 <b>Measurements:</b> L: {data[3]} | S: {data[4]} | Sh: {data[5]} | C: {data[6]} | W: {data[7]} | B: {data[10]}</p>
                        <p>💰 <b>Total Bill:</b> Rs. {data[12]} | <b>Advance:</b> Rs. {data[13]} | <b>Prev. Bal:</b> Rs. {data[14]}</p>
                        <h2 style='color:#e74c3c;'>Remaining: Rs. {data[15]}</h2>
                        <p>📝 <b>Notes:</b> {data[16]}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Koi records nahi mile.")

    elif menu == "➕ Add New Client":
        st.subheader("📏 New Measurement & Payment Entry")
        with st.form("add_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                name = st.text_input("Customer Name")
                phone = st.text_input("Mobile Number")
            with c2:
                suits = st.number_input("No. of Suits", min_value=1, step=1)
                prev_bal = st.number_input("Previous Balance (if any)", min_value=0.0)
            with c3:
                total = st.number_input("Total Bill (New)", min_value=0.0)
                advance = st.number_input("Advance Paid", min_value=0.0)
            
            st.markdown("---")
            st.write("📏 **Measurements**")
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1: l = st.text_input("Length")
            with m2: s = st.text_input("Sleeves")
            with m3: sh = st.text_input("Shoulder")
            with m4: cl = st.text_input("Collar")
            with m5: ch = st.text_input("Chest")
            
            m6, m7, m8, m9, m10 = st.columns(5)
            with m6: w = st.text_input("Waist")
            with m7: h = st.text_input("Hip")
            with m8: b = st.text_input("Bottom")
            
            notes = st.text_area("Design Details")
            
            if st.form_submit_button("Save Record"):
                if name and phone:
                    # Calculation: (Total + Previous) - Advance
                    final_rem = (total + prev_bal) - advance
                    c.execute('''INSERT INTO clients (name, phone, length, sleeves, shoulder, collar, chest, waist, hip, bottom, suits_count, total, advance, prev_balance, remaining, notes) 
                                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                              (name, phone, l, s, sh, cl, ch, w, h, b, suits, total, advance, prev_bal, final_rem, notes))
                    conn.commit()
                    st.success(f"Record Saved! Remaining: Rs. {final_rem}")
                else:
                    st.error("Name aur Phone zaroori hain!")

    elif menu == "📑 All Records":
        st.subheader("All Customer Data")
        all_df = pd.read_sql("SELECT * FROM clients", conn)
        st.dataframe(all_df)
        
        # Sync/Offline Concept: Export to CSV
        st.markdown("---")
        st.subheader("📥 Data Backup (Offline Sync)")
        csv = all_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Backup (Excel/CSV)", csv, "tailor_backup.csv", "text/csv")

    elif menu == "⚙️ Settings":
        st.subheader("Settings")
        if st.button("Delete All Data"):
            st.error("Data delete karne ke liye developer se rabta karein.")
