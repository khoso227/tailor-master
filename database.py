import sqlite3

def get_connection():
    conn = sqlite3.connect("tailor_master.db", check_same_thread=False)
    # 1. Users Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            email TEXT UNIQUE, password TEXT, shop_name TEXT, 
            role TEXT, phone TEXT, security_q TEXT, security_a TEXT, 
            status TEXT DEFAULT 'Active'
        )
    """)
    # 2. Orders & Measurements Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, client_name TEXT, client_phone TEXT,
            length TEXT, shoulder TEXT, chest TEXT, waist TEXT, sleeves TEXT, neck TEXT, bottom TEXT,
            thigh TEXT, fly TEXT, hip TEXT, 
            style_collar TEXT, style_sleeve TEXT, style_ghera TEXT,
            payment_method TEXT, total_bill REAL, paid_amount REAL,
            order_date TEXT, status TEXT DEFAULT 'Pending'
        )
    """)
    # Auto Admin
    admin_check = conn.execute("SELECT id FROM users WHERE email='admin@sahilarman.com'").fetchone()
    if not admin_check:
        conn.execute("INSERT INTO users (email, password, shop_name, role, status) VALUES ('admin@sahilarman.com', 'sahilarman2026', 'Super Admin', 'super_admin', 'Active')")
    conn.commit()
    return conn
