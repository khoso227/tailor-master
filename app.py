import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import random

# --- 1. DATABASE CONNECTION ---
def get_connection():
    return sqlite3.connect("tailor_master.db", check_same_thread=False)

conn = get_connection()

# --- 2. MULTI-LANGUAGE (t dictionary) ---
# Maine basics add kiye hain, aap apne purane dict se replace kar sakte hain
t = {
    'login': 'Login', 'email': 'Email', 'pass': 'Password', 'register': 'Register',
    'shop': 'Shop Name', 'phone': 'Phone Number', 's_q': 'Security Question',
    's_a': 'Security Answer', 'forgot': 'Forgot Password?'
}

# --- 3. WALLPAPER LOGIC (20 Mood Wallpapers) ---
def set_wallpaper():
    day_wallpapers = [
        "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?q=80&w=2000", # Fashion Shop
        "https://images.unsplash.com/photo-1520004434532-668416a08753?q=80&w=2000", # Fabric
        "https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=2000", # Tailor Room
        "https://images.unsplash.com/photo-1594932224828-b4b059b6f684?q=80&w=2000", # White Shirt
        "https://images.unsplash.com/photo-1612423284934-2850a4ea6b0f?q=80&w=2000", # Sewing
        "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?q=80&w=2000", # Sunlight Fashion
        "https://images.unsplash.com/photo-1534126511673-b68991578f6a?q=80&w=2000", # Modern Studio
        "https://images.unsplash.com/photo-1516762689617-e1cffcef479d?q=80&w=2000", # Clothes Rack
        "https://images.unsplash.com/photo-1542060717-d79d9e463a8a?q=80&w=2000", # Measuring Tape
        "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?q=80&w=2000"  # Boutique
    ]
    
    night_wallpapers = [
        "https://images.unsplash.com/photo-1472457897821-70d3819a0e24?q=80&w=2000", # Neon Tailor
        "https://images.unsplash.com/photo-1514306191717-452ec28c7814?q=80&w=2000", # Dark Studio
        "https://images.unsplash.com/photo-1537832816519-689ad163238b?q=80&w=2000", # Night Fashion
        "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=2000", # Elegant Dark
        "https://images.unsplash.com/photo-1556905085-86a42173d520?q=80&w=2000", # Cozy sewing
        "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?q=80&w=2000", # Dark Boutique
        "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?q=80&w=2000", # Abstract Fabric
        "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=2000", # Night Shop
        "https://images.unsplash.com/photo-1555529771-835f59fc5efe?q=80&w=2000", # Moody Lighting
        "https://images.unsplash.com/photo-1506157786151-b8491531f063?q=80&w=2000"  # Dark Aesthetic
    ]

    st.sidebar.markdown("### 🎨 UI Theme")
    mood = st.sidebar.radio("Select Mood", ["Day Mood ☀️", "Night Mood 🌙"])
    
    if mood == "Day Mood ☀️":
        bg_img = random.choice(day_wallpapers)
        text_color = "black"
    else:
        bg_img = random.choice(night_wallpapers)
        text_color = "white"

    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("{bg_img}");
        background-size: cover;
        background-repeat: no-repeat;
        color: {text_color};
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# --- 4. ANALYTICS VIEW (Merged from analytics.py) ---
def show_global_stats(conn=None):
    st.header("📊 Global System Overview")
    if conn is None:
        conn = get_connection()
    
    # Example Query - Update based on your actual DB schema
    try:
        stats = pd.read_sql("SELECT shop_name, status, role FROM users", conn)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Shops", len(stats))
        c2.metric("Active Admins", len(stats[stats['role'] == 'admin']))
        c3.metric("Blocked Accounts", len(stats[stats['status'] == 'Blocked']))
        
        fig = px.pie(stats, names='status', title="Account Status Distribution")
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.info("No analytics data available yet.")

# --- 5. MAIN APP LOGIC ---
if 'view' not in st.session_state: st.session_state.view = "login"
if 'auth' not in st.session_state: st.session_state.auth = False

# Apply Theme
set_wallpaper()

if not st.session_state.auth:
    # 🟢 LOGIN VIEW
    if st.session_state.view == "login":
        st.subheader(t['login'])
        le = st.text_input(t['email'], key="l_e").strip().lower()
        lp = st.text_input(t['pass'], type="password", key="l_p").strip()
        
        c_l1, c_l2 = st.columns([1, 4])
        if c_l1.button(t['login']):
            user = conn.execute("SELECT id, role, shop_name, email, status FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
            if user:
                if user[4] == 'Blocked': st.error("Account Blocked! Contact Sahil & Arman IT Solutions.")
                else:
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop, st.session_state.u_email = user[0], user[1], user[2], user[3]
                    st.rerun()
            else: st.error("Invalid Details!")
        
        st.markdown("---")
        c_alt1, c_alt2 = st.columns(2)
        if c_alt1.button(t['register']): st.session_state.view = "register"; st.rerun()
        if c_alt2.button(t['forgot']): st.session_state.view = "forgot"; st.rerun()

    # 🟡 REGISTER VIEW
    elif st.session_state.view == "register":
        st.subheader(t['register'])
        reg_sn = st.text_input(t['shop'])
        reg_ph = st.text_input(t['phone'])
        reg_e = st.text_input(t['email'], key="r_e").strip().lower()
        reg_p = st.text_input(t['pass'], key="r_p").strip()
        reg_sq = st.text_input(t['s_q'])
        reg_sa = st.text_input(t['s_a'])
        
        c_r1, c_r2 = st.columns([1, 4])
        if c_r1.button("Create Account & Enter"):
            if reg_sn and reg_e and reg_p:
                try:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO users (email, password, shop_name, role, phone, security_q, security_a, status) VALUES (?,?,?,?,?,?,?,?)", 
                                 (reg_e, reg_p, reg_sn, 'admin', reg_ph, reg_sq, reg_sa, 'Active'))
                    conn.commit()
                    st.session_state.auth = True
                    st.session_state.u_id = cur.lastrowid
                    st.session_state.u_role = 'admin'
                    st.session_state.u_shop = reg_sn
                    st.session_state.u_email = reg_e
                    st.rerun()
                except: st.error("Email already exists!")
            else: st.warning("Please fill essential fields")
        
        if c_r2.button("← Back to Login"): st.session_state.view = "login"; st.rerun()

    # 🔴 FORGOT PASSWORD VIEW
    elif st.session_state.view == "forgot":
        st.subheader(t['forgot'])
        fe = st.text_input("Recovery Email").strip().lower()
        if fe:
            f_user = conn.execute("SELECT security_q, security_a, password FROM users WHERE LOWER(email)=?", (fe,)).fetchone()
            if f_user:
                st.info(f"Question: {f_user[0]}")
                ans = st.text_input("Your Answer")
                if st.button("Recover Password"):
                    if ans == f_user[1]: st.success(f"Your Password is: {f_user[2]}")
                    else: st.error("Wrong Answer!")
            else: st.error("Email not found.")
        if st.button("← Back to Login"): st.session_state.view = "login"; st.rerun()

else:
    # --- AFTER LOGIN: SHOW ANALYTICS ---
    st.sidebar.title(f"Welcome, {st.session_state.u_shop}")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
    
    # Analytics function call
    show_global_stats(conn)
