import streamlit as st
import sqlite3
import pandas as pd

# Database Setup
conn = sqlite3.connect('tailor_live.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS clients 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, 
             length TEXT, sleeves TEXT, shoulder TEXT, collar TEXT, chest TEXT, 
             waist TEXT, hip TEXT, total REAL, advance REAL, remaining REAL)''')
conn.commit()

st.set_page_config(page_title="Azad Tailors", layout="wide")

st.sidebar.title("🧵 AZAD TAILORS")
choice = st.sidebar.radio("Navigation", ["Login", "Dashboard", "Add New Client"])

if choice == "Login":
    st.title("Admin Login")
    user = st.text_input("Username")
    pas = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pas == "1234":
            st.success("Logged In! Go to Dashboard.")
        else:
            st.error("Ghalat Password")

elif choice == "Dashboard":
    st.title("📋 Customer Database")
    df = pd.read_sql("SELECT * FROM clients", conn)
    st.dataframe(df, use_container_width=True)
    
    search = st.text_input("Search Customer Name")
    if search:
        res = df[df['name'].str.contains(search, case=False)]
        st.write(res)

elif choice == "Add New Client":
    st.title("📏 Add New Measurement")
    with st.form("my_form"):
        name = st.text_input("Customer Name")
        phone = st.text_input("Mobile No")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            l = st.text_input("Length")
            s = st.text_input("Sleeves")
        with col2:
            sh = st.text_input("Shoulder")
            cl = st.text_input("Collar")
        with col3:
            ch = st.text_input("Chest")
            w = st.text_input("Waist")
            
        t = st.number_input("Total Amount")
        a = st.number_input("Advance")
        
        if st.form_submit_button("Save Record"):
            rem = t - a
            c.execute("INSERT INTO clients (name,phone,length,sleeves,shoulder,collar,chest,waist,total,advance,remaining) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                      (name, phone, l, s, sh, cl, ch, w, t, a, rem))
            conn.commit()
            st.success("Client Added Successfully!")