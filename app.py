import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import random

# --- 1. CONFIG & DATABASE ---
st.set_page_config(page_title="Tailor Master Pro", layout="wide", page_icon="👔")

def get_connection():
    conn = sqlite3.connect("tailor_master.db", check_same_thread=False)
    # Create Users Table if not exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            email TEXT UNIQUE, 
            password TEXT, 
            shop_name TEXT, 
            role TEXT, 
            phone TEXT, 
            security_q TEXT, 
            security_a TEXT, 
            status TEXT DEFAULT 'Active'
        )
    """)
    conn.commit()
    return conn

conn = get_connection()

# --- 2. THEME & WALLPAPER LOGIC ---
def apply_custom_style():
    day_wallpapers = [
        "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?q=80&w=2000",
        "https://images.unsplash.com/photo-1520004434532-668416a08753?q=80&w=2000",
        "https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=2000",
        "https://images.unsplash.com/photo-1594932224828-b4b059b6f684?q=80&w=2000",
        "https://images.unsplash.com/photo-1612423284934-2850a4ea6b0f?q=80&w=2000",
        "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?q=80&w=2000",
        "https://images.unsplash.com/photo-1534126511673-b68991578f6a?q=80&w=2000",
        "https://images.unsplash.com/photo-1516762689617-e1cffcef479d?q=80&w=2000",
        "https://images.unsplash.com/photo-1542060717-d79d9e463a8a?q=80&w=2000",
        "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?q=80&w=2000"
    ]
    night_wallpapers = [
        "https://images.unsplash.com/photo-1472457897821-70d3819a0e24?q=80&w=2000",
        "https://images.unsplash.com/photo-1514306191717-452ec28c7814?q=80&w=2000",
        "https://images.unsplash.com/photo-1537832816519-689ad163238b?q=80&w=2000",
        "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=2000",
        "https://images.unsplash.com/photo-1556905085-86a42173d520?q=80&w=2000",
        "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?q=80&w=2000",
        "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?q=80&w=2000",
        "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=2000",
        "https://images.unsplash.com/photo-1555529771-835f59fc5efe?q=80&w=2000",
        "https://images.unsplash.com/photo-1506157786151-b8491531f063?q=80&w=2000"
    ]

    with st.sidebar:
        st.write("### 🎨 UI Theme")
        mood = st.radio("Select Mood", ["Day Mood ☀️", "Night Mood 🌙"])
    
    # Save selection to session so it doesn't jump on every click
    if 'bg_choice' not in st.session_state or st.sidebar.button("🔀 Shuffle Wallpaper"):
        st.session_state.bg_choice = random.choice(day_wallpapers if "Day" in mood else night_wallpapers)
    
    bg_img = st.session_state.bg_choice
    overlay_color = "rgba(255, 255, 255, 0.85)" if "Day" in mood else "rgba(0, 0, 0, 0.80)"
    text_color = "#111111" if "Day" in mood else "#FFFFFF"

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{bg_img}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .main-container {{
            background-color: {overlay_color};
            padding: 40px;
            border-radius: 20px;
            color: {text_color};
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            margin-top: 20px;
        }}
        h1, h2, h3, p, label, .stMarkdown {{ color: {text_color} !important; }}
        .stButton>button {{ width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'view' not in st.session_state: st.session_state.view = "login"

apply_custom_style()

# --- 4. APP LOGIC ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

if not st.session_state.auth:
    # --- 🟢 LOGIN VIEW ---
    if st.session_state.view == "login":
        st.title("🔑 Login - Tailor Master Pro")
        le = st.text_input("Email / Username").strip().lower()
        lp = st.text_input("Password", type="password").strip()
        
        if st.button("Login Now"):
            user = conn.execute("SELECT id, role, shop_name, status FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
            if user:
                if user[3] == 'Blocked': st.error("🚫 Account Blocked! Contact Sahil & Arman IT Solutions.")
                else:
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = user[0], user[1], user[2]
                    st.rerun()
            else: st.error("❌ Invalid Details! Please try again.")
        
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("📝 Register New Shop"): st.session_state.view = "register"; st.rerun()
        with c2: 
            if st.button("❓ Forgot Password"): st.session_state.view = "forgot"; st.rerun()

    # --- 🟡 REGISTER VIEW ---
    elif st.session_state.view == "register":
        st.title("📝 Shop Registration")
        r_shop = st.text_input("Shop Name")
        r_email = st.text_input("Email (Login ID)").strip().lower()
        r_pass = st.text_input("Create Password", type="password")
        r_sq = st.text_input("Security Question (e.g. Best Friend's Name?)")
        r_sa = st.text_input("Security Answer")
        
        if st.button("Create Account & Login"):
            if r_shop and r_email and r_pass and r_sa:
                try:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO users (email, password, shop_name, role, security_q, security_a, status) VALUES (?,?,?,?,?,?,?)", 
                                 (r_email, r_pass, r_shop, 'admin', r_sq, r_sa, 'Active'))
                    conn.commit()
                    st.success("✅ Account Created Successfully!")
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = cur.lastrowid, 'admin', r_shop
                    st.rerun()
                except: st.error("⚠️ Email already exists!")
            else: st.warning("⚠️ Please fill all fields.")
        
        if st.button("← Back to Login"): st.session_state.view = "login"; st.rerun()

    # --- 🔴 FORGOT PASSWORD VIEW ---
    elif st.session_state.view == "forgot":
        st.title("🔐 Recover Password")
        fe = st.text_input("Enter your registered Email").strip().lower()
        if fe:
            user_data = conn.execute("SELECT security_q, security_a, password FROM users WHERE LOWER(email)=?", (fe,)).fetchone()
            if user_data:
                st.info(f"Question: {user_data[0]}")
                ans = st.text_input("Your Answer")
                if st.button("Show My Password"):
                    if ans.lower() == user_data[1].lower():
                        st.success(f"🔓 Your Password is: **{user_data[2]}**")
                    else: st.error("❌ Wrong Answer!")
            else: st.error("📧 Email not found.")
        
        if st.button("← Back to Login"): st.session_state.view = "login"; st.rerun()

else:
    # --- 🔵 AUTHENTICATED STATE (Functions) ---
    with st.sidebar:
        st.title("👔 Tailor Master")
        st.success(f"Shop: {st.session_state.u_shop}")
        menu = st.selectbox("Navigation", ["Dashboard", "Customers", "Measurements", "Global Stats", "Settings"])
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.auth = False
            st.rerun()

    if menu == "Global Stats":
        st.header("📊 Global Platform Analytics")
        df = pd.read_sql("SELECT shop_name, status, role FROM users", conn)
        
        c1, c2 = st.columns(2)
        c1.metric("Total Active Shops", len(df[df['status']=='Active']))
        c2.metric("Blocked Users", len(df[df['status']=='Blocked']))
        
        fig = px.pie(df, names='status', title="Account Status Overview", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
        st.table(df)

    elif menu == "Dashboard":
        st.header(f"Welcome to {st.session_state.u_shop}")
        st.write("Today's Tasks & Overview will appear here.")
        # Add quick metrics here
        st.info("💡 Pro Tip: Use the 'Shuffle' button in the sidebar to change the background anytime!")

    else:
        st.header(f"🚧 {menu} Module")
        st.write("Coming Soon: Full feature integration.")

st.markdown('</div>', unsafe_allow_html=True)
