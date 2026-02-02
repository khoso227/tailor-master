import sqlite3
from datetime import date, timedelta

def get_connection():
    return sqlite3.connect('tailor_master_v14.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Users table with Expiry Date
    c.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, 
         shop_name TEXT, role TEXT, phone TEXT, fee_status TEXT DEFAULT 'Unpaid', 
         security_q TEXT, security_a TEXT, status TEXT DEFAULT 'Active', 
         expiry_date DATE)''')

    # Super Admin (Life-time Access)
    c.execute("SELECT * FROM users WHERE email='admin@sahilarman.com'")
    if not c.fetchone():
        c.execute("INSERT INTO users (email, password, shop_name, role, fee_status, status, expiry_date) VALUES (?,?,?,?,?,?,?)", 
                  ('admin@sahilarman.com', 'sahilarman2026', 'Sahil & Arman IT Co', 'super_admin', 'Paid', 'Active', '2099-12-31'))

    c.execute('''CREATE TABLE IF NOT EXISTS clients 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, phone TEXT, 
         total REAL, advance REAL, remaining REAL, pay_method TEXT, order_date DATE, 
         delivery_date DATE, m_data TEXT, s_data TEXT, verbal_notes TEXT, status TEXT DEFAULT 'Pending')''')
    conn.commit()
    conn.close()
