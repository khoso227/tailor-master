import streamlit as st
import pandas as pd
import plotly.express as pximport streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import random
from datetime import datetime

# --- 1. CONFIG & DATABASE ---
st.set_page_config(page_title="Tailor Master Pro", layout="wide", page_icon="👔")

def get_connection():
    conn = sqlite3.connect("tailor_master.db", check_same_thread=False)
    # Users Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            email TEXT UNIQUE, password TEXT, shop_name TEXT, 
            role TEXT, phone TEXT, security_q TEXT, security_a TEXT, 
            status TEXT DEFAULT 'Active'
        )
    """)
    # Orders/Measurements Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            client_name TEXT,
            client_phone TEXT,
            length TEXT, shoulder TEXT, chest TEXT, waist TEXT, sleeves TEXT, neck TEXT, bottom TEXT,
            payment_method TEXT, total_bill REAL, paid_amount REAL,
            order_date TEXT, status TEXT DEFAULT 'Pending'
        )
    """)
    # AUTO-CREATE ADMIN
    admin_check = conn.execute("SELECT id FROM users WHERE email='admin@sahilarman.com'").fetchone()
    if not admin_check:
        conn.execute("""
            INSERT INTO users (email, password, shop_name, role, status) 
            VALUES ('admin@sahilarman.com', 'sahilarman2026', 'Super Admin', 'super_admin', 'Active')
        """)
    conn.commit()
    return conn

conn = get_connection()

# --- 2. BILINGUAL SUPPORT ---
if 'lang' not in st.session_state: st.session_state.lang = "English"

translations = {
    "English": {
        "title": "🔑 Login - Tailor Master Pro",
        "email": "Email", "pass": "Password", "login_btn": "Login Now",
        "reg_btn": "Register New Shop", "forgot_btn": "Forgot Password?",
        "dash": "Dashboard", "order": "New Order ➕", "report": "Reports 📋", "sec": "Security / Settings ⚙️",
        "logout": "Logout 🚪", "shuffle": "🔀 Shuffle Wallpaper",
        "c_name": "Client Name", "c_phone": "Mobile Number", "measure": "Measurements (Inches)",
        "len": "Length", "sh": "Shoulder", "ch": "Chest", "ws": "Waist", "sl": "Sleeves", "nk": "Neck", "bt": "Bottom",
        "pay": "Payment Method", "bill": "Total Bill", "advance": "Advance Paid", "save": "Save Order ✅",
        "rename_shop": "Rename Your Shop", "update": "Update Shop Name"
    },
    "Urdu": {
        "title": "لاگ ان - ٹیلر ماسٹر پرو 🔑",
        "email": "ای میل", "pass": "پاس ورڈ", "login_btn": "لاگ ان کریں",
        "reg_btn": "نئی دکان رجسٹر کریں", "forgot_btn": "پاس ورڈ بھول گئے؟",
        "dash": "ڈیش بورڈ", "order": "نیا آرڈر ➕", "report": "رپورٹس 📋", "sec": "سیکورٹی / سیٹنگز ⚙️",
        "logout": "لاگ آؤٹ 🚪", "shuffle": "تبدیل کریں 🔀",
        "c_name": "گاہک کا نام", "c_phone": "موبائل نمبر", "measure": "پیمائش (انچ میں)",
        "len": "لمبائی", "sh": "تیرا / کندھا", "ch": "چھاتی", "ws": "کمر", "sl": "آستین", "nk": "گلا / کالر", "bt": "گھیرا / پانچہ",
        "pay": "ادائیگی کا طریقہ", "bill": "کل بل", "advance": "ایڈوانس رقم", "save": "آرڈر محفوظ کریں ✅",
        "rename_shop": "دکان کا نام تبدیل کریں", "update": "اپ ڈیٹ کریں"
    }
}

ln = translations[st.session_state.lang]

# --- 3. THEME & WALLPAPER ---
def apply_custom_style():
    day_wallpapers = ["https://images.unsplash.com/photo-1558769132-cb1aea458c5e", "https://images.unsplash.com/photo-1520004434532-668416a08753", "https://images.unsplash.com/photo-1544441893-675973e31985"]
    night_wallpapers = ["https://images.unsplash.com/photo-1472457897821-70d3819a0e24", "https://images.unsplash.com/photo-1514306191717-452ec28c7814", "https://images.unsplash.com/photo-1537832816519-689ad163238b"]
    
    with st.sidebar:
        st.session_state.lang = st.selectbox("Language", ["English", "Urdu"], index=0 if st.session_state.lang=="English" else 1)
        mood = st.radio("UI Mode", ["Day Mood ☀️", "Night Mood 🌙"])
        if st.button(ln['shuffle']):
            st.session_state.bg_choice = random.choice(day_wallpapers if "Day" in mood else night_wallpapers)
    
    if 'bg_choice' not in st.session_state: st.session_state.bg_choice = day_wallpapers[0]
    overlay = "rgba(255, 255, 255, 0.90)" if "Day" in mood else "rgba(0, 0, 0, 0.85)"
    txt = "#111" if "Day" in mood else "#fff"

    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{st.session_state.bg_choice}"); background-size: cover; background-attachment: fixed; }}
        .main-container {{ background-color: {overlay}; padding: 25px; border-radius: 15px; color: {txt}; }}
        h1, h2, h3, p, label {{ color: {txt} !important; {'text-align: right;' if st.session_state.lang=='Urdu' else ''} }}
        </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'view' not in st.session_state: st.session_state.view = "login"

apply_custom_style()
st.markdown('<div class="main-container">', unsafe_allow_html=True)

if not st.session_state.auth:
    # --- LOGIN / REGISTER / FORGOT VIEWS ---
    if st.session_state.view == "login":
        st.title(ln['title'])
        le = st.text_input(ln['email']).strip().lower()
        lp = st.text_input(ln['pass'], type="password").strip()
        if st.button(ln['login_btn']):
            user = conn.execute("SELECT id, role, shop_name, status FROM users WHERE LOWER(email)=? AND password=?", (le, lp)).fetchone()
            if user:
                st.session_state.auth, st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = True, user[0], user[1], user[2]
                st.rerun()
            else: st.error("Invalid Login!")
        if st.button(ln['reg_btn']): st.session_state.view = "register"; st.rerun()

    elif st.session_state.view == "register":
        st.title(ln['reg_btn'])
        r_sn = st.text_input("Shop Name")
        r_e = st.text_input("Email").strip().lower()
        r_p = st.text_input("Password", type="password")
        if st.button("Create Account"):
            conn.execute("INSERT INTO users (email, password, shop_name, role) VALUES (?,?,?,?)", (r_e, r_p, r_sn, 'admin'))
            conn.commit()
            st.success("Success! Please Login.")
            st.session_state.view = "login"; st.rerun()
        if st.button("Back"): st.session_state.view = "login"; st.rerun()

else:
    # --- LOGGED IN AREA ---
    with st.sidebar:
        st.markdown(f"**{st.session_state.u_shop}**")
        menu = st.radio("Navigation", [ln['dash'], ln['order'], ln['report'], ln['sec']])
        if st.button(ln['logout']): st.session_state.auth = False; st.rerun()

    # --- 🔵 NEW ORDER PAGE ---
    if menu == ln['order']:
        st.header(ln['order'])
        with st.form("measurement_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input(ln['c_name'])
            phone = c2.text_input(ln['c_phone'])
            
            st.subheader(ln['measure'])
            m1, m2, m3, m4 = st.columns(4)
            length = m1.text_input(ln['len'])
            shoulder = m2.text_input(ln['sh'])
            chest = m3.text_input(ln['ch'])
            waist = m4.text_input(ln['ws'])
            
            m5, m6, m7, m8 = st.columns(4)
            sleeves = m5.text_input(ln['sl'])
            neck = m6.text_input(ln['nk'])
            bottom = m7.text_input(ln['bt'])
            
            st.markdown("---")
            p1, p2, p3 = st.columns(3)
            p_method = p1.selectbox(ln['pay'], ["Cash", "EasyPaisa", "JazzCash", "Bank Transfer"])
            bill = p2.number_input(ln['bill'], min_value=0.0)
            adv = p3.number_input(ln['advance'], min_value=0.0)
            
            if st.form_submit_button(ln['save']):
                if name and phone:
                    conn.execute("""INSERT INTO orders (user_id, client_name, client_phone, length, shoulder, chest, waist, sleeves, neck, bottom, payment_method, total_bill, paid_amount, order_date) 
                                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                                 (st.session_state.u_id, name, phone, length, shoulder, chest, waist, sleeves, neck, bottom, p_method, bill, adv, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit()
                    st.success("Order Saved Successfully!")
                else: st.warning("Please fill Name and Phone!")

    # --- 🟢 DASHBOARD / REPORTS ---
    elif menu == ln['dash'] or menu == ln['report']:
        st.header(menu)
        df = pd.read_sql(f"SELECT client_name, client_phone, total_bill, status, order_date FROM orders WHERE user_id={st.session_state.u_id}", conn)
        st.dataframe(df, use_container_width=True)

    # --- 🔴 SECURITY / SETTINGS PAGE ---
    elif menu == ln['sec']:
        st.header(ln['sec'])
        st.subheader("Your Shop Details")
        st.info(f"📍 Shop Name: {st.session_state.u_shop}")
        
        new_sn = st.text_input(ln['rename_shop'], value=st.session_state.u_shop)
        if st.button(ln['update']):
            conn.execute("UPDATE users SET shop_name=? WHERE id=?", (new_sn, st.session_state.u_id))
            conn.commit()
            st.session_state.u_shop = new_sn
            st.success("Shop Renamed Successfully! Please refresh or continue.")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
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

# --- 2. BILINGUAL SUPPORT ---
if 'lang' not in st.session_state: st.session_state.lang = "English"

translations = {
    "English": {
        "title": "🔑 Login - Tailor Master Pro",
        "email": "Email / Username",
        "pass": "Password",
        "login_btn": "Login Now",
        "reg_btn": "Register New Shop",
        "forgot_btn": "Forgot Password?",
        "shop_label": "Shop Name",
        "phone_label": "Phone Number",
        "sq_label": "Security Question (e.g. Best Friend's Name?)",
        "sa_label": "Security Answer",
        "create_btn": "Create Account & Login",
        "back_btn": "← Back to Login",
        "recovery_email": "Enter Recovery Email",
        "recover_btn": "Show Password",
        "dash": "Dashboard", "order": "New Order", "report": "Reports", "sec": "Security / Settings",
        "lang_label": "Language 🌐", "theme_label": "Theme Mood 🎨", "logout": "Logout 🚪", "shuffle": "🔀 Shuffle Wallpaper"
    },
    "Urdu": {
        "title": "لاگ ان - ٹیلر ماسٹر پرو 🔑",
        "email": "ای میل یا یوزر نیم",
        "pass": "پاس ورڈ",
        "login_btn": "لاگ ان کریں",
        "reg_btn": "نئی دکان رجسٹر کریں",
        "forgot_btn": "پاس ورڈ بھول گئے؟",
        "shop_label": "دکان کا نام",
        "phone_label": "فون نمبر",
        "sq_label": "سیکورٹی سوال (مثلاً بہترین دوست؟)",
        "sa_label": "سیکورٹی جواب",
        "create_btn": "اکاؤنٹ بنائیں اور لاگ ان کریں",
        "back_btn": "لاگ ان پر واپس جائیں ←",
        "recovery_email": "ریکوری ای میل درج کریں",
        "recover_btn": "پاس ورڈ دیکھیں",
        "dash": "ڈیش بورڈ", "order": "نیا آرڈر", "report": "رپورٹس", "sec": "سیکورٹی / سیٹنگز",
        "lang_label": "زبان 🌐", "theme_label": "تھیم موڈ 🎨", "logout": "لاگ آؤٹ 🚪", "shuffle": "وال پیپر تبدیل کریں 🔀"
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

# --- 4. APP LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'view' not in st.session_state: st.session_state.view = "login"

apply_custom_style()

st.markdown('<div class="main-container">', unsafe_allow_html=True)

if not st.session_state.auth:
    # --- 🟢 LOGIN VIEW ---
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

    # --- 🟡 REGISTER VIEW (Form Restored) ---
    elif st.session_state.view == "register":
        st.title(ln['reg_btn'])
        r_sn = st.text_input(ln['shop_label'])
        r_ph = st.text_input(ln['phone_label'])
        r_e = st.text_input(ln['email']).strip().lower()
        r_p = st.text_input(ln['pass'], type="password")
        r_sq = st.text_input(ln['sq_label'])
        r_sa = st.text_input(ln['sa_label'])
        
        if st.button(ln['create_btn']):
            if r_sn and r_e and r_p and r_sa:
                try:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO users (email, password, shop_name, role, phone, security_q, security_a) VALUES (?,?,?,?,?,?,?)", 
                                 (r_e, r_p, r_sn, 'admin', r_ph, r_sq, r_sa))
                    conn.commit()
                    st.success("✅ Account Created!")
                    st.session_state.auth = True
                    st.session_state.u_id, st.session_state.u_role, st.session_state.u_shop = cur.lastrowid, 'admin', r_sn
                    st.rerun()
                except: st.error("⚠️ Email already exists!")
            else: st.warning("⚠️ Please fill essential fields.")
        
        if st.button(ln['back_btn']): st.session_state.view = "login"; st.rerun()

    # --- 🔴 FORGOT PASSWORD VIEW (Logic Restored) ---
    elif st.session_state.view == "forgot":
        st.title(ln['forgot_btn'])
        fe = st.text_input(ln['recovery_email']).strip().lower()
        if fe:
            u_data = conn.execute("SELECT security_q, security_a, password FROM users WHERE LOWER(email)=?", (fe,)).fetchone()
            if u_data:
                st.info(f"Question: {u_data[0]}")
                ans = st.text_input(ln['sa_label'])
                if st.button(ln['recover_btn']):
                    if ans.lower() == u_data[1].lower():
                        st.success(f"🔓 Your Password: **{u_data[2]}**")
                    else: st.error("❌ Wrong Answer!")
            else: st.error("📧 Email not found.")
        
        if st.button(ln['back_btn']): st.session_state.view = "login"; st.rerun()

else:
    # --- 🔵 AUTHENTICATED STATE (Navigation Restored) ---
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
        st.info("📊 Welcome to your digital summary.")
        
    elif menu == ln['order']:
        st.header(ln['order'])
        st.write("Order entry form goes here.")
        
    elif menu == ln['report']:
        st.header(ln['report'])
        st.write("View sales and order history.")

    elif menu == ln['sec']:
        st.header(ln['sec'])
        if st.session_state.u_role == 'super_admin':
            st.subheader("Admin Control Panel")
            df = pd.read_sql("SELECT shop_name, email, status FROM users", conn)
            st.dataframe(df)
        else:
            st.write("Security settings and password change.")

st.markdown('</div>', unsafe_allow_html=True)

