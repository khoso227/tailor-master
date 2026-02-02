import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import random

# --- 1. CONFIG & DATABASE ---
st.set_page_config(page_title="Tailor Master Pro", layout="wide", page_icon="👔")

def get_connection():
    conn = sqlite3.connect("tailor_master.db", check_same_thread=False)
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
    # 🔥 AUTO-CREATE ADMIN (Agar database khali ho)
    admin_check = conn.execute("SELECT id FROM users WHERE email='admin@sahilarman.com'").fetchone()
    if not admin_check:
        conn.execute("""
            INSERT INTO users (email, password, shop_name, role, status) 
            VALUES ('admin@sahilarman.com', 'sahilarman2026', 'Super Admin', 'super_admin', 'Active')
        """)
        conn.commit()
    return conn

conn = get_connection()

# --- 2. BILINGUAL SUPPORT (Urdu + English) ---
if 'lang' not in st.session_state: st.session_state.lang = "English"

translations = {
    "English": {
        "title": "🔑 Login - Tailor Master Pro",
        "email": "Email / Username",
        "pass": "Password",
        "login_btn": "Login Now",
        "reg_btn": "Register New Shop",
        "forgot_btn": "Forgot Password?",
        "dash": "Dashboard",
        "order": "New Order",
        "report": "Reports",
        "sec": "Security / Settings",
        "lang_label": "Language 🌐",
        "theme_label": "Theme Mood 🎨",
        "logout": "Logout 🚪",
        "shuffle": "🔀 Shuffle Wallpaper"
    },
    "Urdu": {
        "title": "لاگ ان - ٹیلر ماسٹر پرو 🔑",
        "email": "ای میل یا یوزر نیم",
        "pass": "پاس ورڈ",
        "login_btn": "لاگ ان کریں",
        "reg_btn": "نئی دکان رجسٹر کریں",
        "forgot_btn": "پاس ورڈ بھول گئے؟",
        "dash": "ڈیش بورڈ",
        "order": "نیا آرڈر",
        "report": "رپورٹس",
        "sec": "سیکورٹی / سیٹنگز",
        "lang_label": "زبان 🌐",
        "theme_label": "تھیم موڈ 🎨",
        "logout": "لاگ آؤٹ 🚪",
        "shuffle": "وال پیپر تبدیل کریں 🔀"
    }
}

ln = translations[st.session_state.lang]

# --- 3. THEME & 20 WALLPAPERS LOGIC ---
def apply_custom_style():
    day_wallpapers = [
        "https://images.unsplash.com/photo-1558769132-cb1aea458c5e", "https://images.unsplash.com/photo-1520004434532-668416a08753",
        "https://images.unsplash.com/photo-1544441893-675973e31985", "https://images.unsplash.com/photo-1594932224828-b4b059b6f684",
        "https://images.unsplash.com/photo-1612423284934-2850a4ea6b0f", "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f",
        "https://images.unsplash.com/photo-1534126511673-b68991578f6a", "https://images.unsplash.com/photo-1516762689617-e1cffcef479d",
        "https://images.unsplash.com/photo-1542060717-d79d9e463a8a", "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5"
    ]
    night_wallpapers = [
        "https://images.unsplash.com/photo-1472457897821-70d3819a0e24", "https://images.unsplash.com/photo-1514306191717-452ec28c7814",
        "https://images.unsplash.com/photo-1537832816519-689ad163238b", "https://images.unsplash.com/photo-1490481651871-ab68de25d43d",
        "https://images.unsplash.com/photo-1556905085-86a42173d520", "https://images.unsplash.com/photo-1512436991641-6745cdb1723f",
        "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3", "https://images.unsplash.com/photo-1441986300917-64674bd600d8",
        "https://images.unsplash.com/photo-1555529771-835f59fc5efe", "https://images.unsplash.com/photo-1506157786151-b8491531f063"
    ]

    with st.sidebar:
        st.write(f"### {ln['lang_label']}")
        st.session_state.lang = st.selectbox("", ["English", "Urdu"], index=0 if st.session_state.lang=="English" else 1)
        
        st.write(f"### {ln['theme_label']}")
        mood = st.radio("", ["Day Mood ☀️", "Night Mood 🌙"])
        
        if st.button(ln['shuffle']):
            st.session_state.bg_choice = random.choice(day_wallpapers if "Day" in mood else night_wallpapers)
    
    if 'bg_choice' not in st.session_state:
        st.session_state.bg_choice = day_wallpapers[0]
    
    bg_img = st.session_state.bg_choice
    overlay = "rgba(255, 255, 255, 0.88)" if "Day" in mood else "rgba(0, 0, 0, 0.82)"
    txt = "#111111" if "Day" in mood else "#FFFFFF"

    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{bg_img}?auto=format&fit=crop&w=2000&q=80"); background-size: cover; background-attachment: fixed; }}
        .main-container {{ 
            background-color: {overlay}; padding: 35px; border-radius: 20px; color: {txt}; 
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        h1, h2, h3, p, label, .stMarkdown {{ color: {txt} !important; {'text-align: right;' if st.session_state.lang=='Urdu' else ''} }}
        .stButton>button {{ width: 100%; border-radius: 12px; font-weight: bold; height: 3.5em; }}
        </style>
    """, unsafe_allow_html=True)

# --- 4. MAIN APP ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'view' not in st.session_state: st.session_state.view = "login"

apply_custom_style()

st.markdown('<div class="main-container">', unsafe_allow_html=True)

if not st.session_state.auth:
    # --- AUTHENTICATION VIEWS ---
    if st.session_state.view == "login":
        st.title(ln['title'])
        le = st.text_input(ln['email']).strip().lower()
        lp = st.text_input(ln['pass'], type="password").strip()
        
        if st.button(ln['login_btn']):
            user = conn.execute("SELECT id, role, shop_name, status FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
            if user:
                if user[3] == 'Blocked': st.error("🚫 Account Blocked! Contact Admin.")
                else:
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = user[0], user[1], user[2]
                    st.rerun()
            else: st.error("❌ Invalid Details!" if st.session_state.lang=="English" else "❌ غلط تفصیلات!")
        
        c1, c2 = st.columns(2)
        with c1: 
            if st.button(ln['reg_btn']): st.session_state.view = "register"; st.rerun()
        with c2: 
            if st.button(ln['forgot_btn']): st.session_state.view = "forgot"; st.rerun()

    elif st.session_state.view == "register":
        st.title(ln['reg_btn'])
        # Register inputs yahan aayenge...
        if st.button("← Back" if st.session_state.lang=="English" else "← واپس"): 
            st.session_state.view = "login"; st.rerun()

    elif st.session_state.view == "forgot":
        st.title(ln['forgot_btn'])
        # Forgot password logic yahan aayegi...
        if st.button("← Back" if st.session_state.lang=="English" else "← واپس"): 
            st.session_state.view = "login"; st.rerun()

else:
    # --- LOGGED IN SIDEBAR MENU ---
    with st.sidebar:
        st.markdown("---")
        st.success(f"Shop: {st.session_state.u_shop}")
        menu = st.radio("MENU", [ln['dash'], ln['order'], ln['report'], ln['sec']])
        
        if st.button(ln['logout']):
            st.session_state.auth = False
            st.rerun()

    # --- PAGES ---
    if menu == ln['dash']:
        st.header(f"{ln['dash']} - {st.session_state.u_shop}")
        st.info("📊 Welcome to your digital diary.")
        # Analytics charts yahan add karein
        
    elif menu == ln['order']:
        st.header(ln['order'])
        st.write("Measurement Form will be displayed here.")
        
    elif menu == ln['report']:
        st.header(ln['report'])
        st.write("Detailed History of Orders.")

    elif menu == ln['sec']:
        st.header(ln['sec'])
        if st.session_state.u_role == 'super_admin':
            st.subheader("Admin Control Panel")
            df = pd.read_sql("SELECT shop_name, email, status FROM users", conn)
            st.dataframe(df)
        else:
            st.write("Personal Security Settings.")

st.markdown('</div>', unsafe_allow_html=True)
