import streamlit as st
import sqlite3
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Tailor Master Pro", layout="wide", page_icon="🧵")

# --- Custom CSS for Stylish Look ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    div.stButton > button:first-child {
        background-color: #d4af37;
        color: black;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #fff;
        color: #d4af37;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .shop-title {
        color: #d4af37;
        font-family: 'Times New Roman';
        font-size: 50px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Database Setup ---
conn = sqlite3.connect('tailor_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS clients 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, 
             length TEXT, sleeves TEXT, shoulder TEXT, collar TEXT, chest TEXT, 
             waist TEXT, hip TEXT, shalwar_len TEXT, bottom TEXT,
             total REAL, advance REAL, remaining REAL, notes TEXT)''')
conn.commit()

# --- Sidebar & Shop Name Customization ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2933/2933941.png", width=100)
shop_name = st.sidebar.text_input("Change Shop Name", "Tailor Master")
st.sidebar.markdown("---")
choice = st.sidebar.radio("Main Menu", ["🔑 Login", "📊 Dashboard", "➕ Add New Client", "⚙️ Settings"])

# --- Main App Logic ---

st.markdown(f"<div class='shop-title'>{shop_name}</div>", unsafe_allow_html=True)

if choice == "🔑 Login":
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.subheader("Admin Authentication")
        user = st.text_input("Username")
        pas = st.text_input("Password", type="password")
        if st.button("Login Now"):
            if user == "admin" and pas == "1234":
                st.success(f"Welcome to {shop_name} Dashboard!")
                st.balloons()
            else:
                st.error("Access Denied!")

elif choice == "📊 Dashboard":
    st.subheader("📋 Customer Management System")
    
    # Search Bar
    search = st.text_input("🔍 Search Client by Name or Mobile")
    
    query = "SELECT id, name, phone, remaining FROM clients"
    if search:
        query = f"SELECT id, name, phone, remaining FROM clients WHERE name LIKE '%{search}%' OR phone LIKE '%{search}%'"
    
    df = pd.read_sql(query, conn)
    
    if not df.empty:
        # Table Layout
        st.dataframe(df, use_container_width=True)
        
        # Detail View per Click
        st.markdown("---")
        st.subheader("👤 View Full Client Detail")
        client_to_view = st.selectbox("Select Customer to open file", df['name'].tolist())
        
        if st.button("Open Record"):
            client_data = c.execute("SELECT * FROM clients WHERE name=?", (client_to_view,)).fetchone()
            if client_data:
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Name:** {client_data[1]}")
                    st.info(f"**Mobile:** {client_data[2]}")
                    st.write("---")
                    st.write(f"📏 **Length:** {client_data[3]} | **Sleeves:** {client_data[4]}")
                    st.write(f"📏 **Shoulder:** {client_data[5]} | **Collar:** {client_data[6]}")
                    st.write(f"📏 **Chest:** {client_data[7]} | **Waist:** {client_data[8]}")
                    st.write(f"📏 **Hip:** {client_data[9]} | **Bottom:** {client_data[11]}")
                with col2:
                    st.warning(f"💰 **Total Bill:** Rs. {client_data[12]}")
                    st.success(f"💳 **Advance Paid:** Rs. {client_data[13]}")
                    st.error(f"🔴 **Remaining Balance:** Rs. {client_data[14]}")
                    st.text_area("Additional Notes", client_data[15], disabled=True)
    else:
        st.info("No records found.")

elif choice == "➕ Add New Client":
    st.subheader("📏 New Measurement & Payment Entry")
    with st.form("client_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Customer Name")
            phone = st.text_input("Mobile Number")
        with c2:
            total = st.number_input("Total Bill (Rs.)", min_value=0.0)
            advance = st.number_input("Advance Payment (Rs.)", min_value=0.0)
        
        st.markdown("**Measurements**")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            length = st.text_input("Length")
            chest = st.text_input("Chest")
        with m2:
            sleeves = st.text_input("Sleeves")
            waist = st.text_input("Waist")
        with m3:
            shoulder = st.text_input("Shoulder")
            hip = st.text_input("Hip")
        with m4:
            collar = st.text_input("Collar")
            bottom = st.text_input("Bottom")
            
        notes = st.text_area("Design details (e.g., Cuff style, Pocket, etc.)")
        
        if st.form_submit_button("💾 Save Client Record"):
            if name and phone:
                remaining = total - advance
                c.execute('''INSERT INTO clients (name, phone, length, sleeves, shoulder, collar, chest, waist, hip, bottom, total, advance, remaining, notes) 
                             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                          (name, phone, length, sleeves, shoulder, collar, chest, waist, hip, bottom, total, advance, remaining, notes))
                conn.commit()
                st.success(f"Record Saved Successfully! Pending Balance: Rs. {remaining}")
            else:
                st.error("Name and Phone are required!")

elif choice == "⚙️ Settings":
    st.subheader("Application Settings")
    st.write("Current Shop Name:", shop_name)
    if st.button("Clear All Data (Careful!)"):
        st.warning("This will delete all records!")
        # Logic for clearing DB can be added here
