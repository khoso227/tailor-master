import sqlite3

def get_connection():
    # Database ka naam badal kar v7 kar diya hai
    return sqlite3.connect('tailor_platform_v7.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, 
         shop_name TEXT, role TEXT, fee_status TEXT DEFAULT 'Unpaid')''')

    # Create Super Admin if not exists
    c.execute("SELECT * FROM users WHERE email='admin@sahilarman.com'")
    if not c.fetchone():
        c.execute("INSERT INTO users (email, password, shop_name, role, fee_status) VALUES (?,?,?,?,?)", 
                  ('admin@sahilarman.com', 'sahilarman2026', 'Sahil & Arman IT Co', 'super_admin', 'Paid'))

    # Clients Table (Sari dukanon ka data alag karne ke liye user_id zaroori hai)
    c.execute('''CREATE TABLE IF NOT EXISTS clients 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, phone TEXT, 
         suits_count INTEGER, total REAL, advance REAL, remaining REAL,
         status TEXT, order_date DATE, delivery_date DATE, m_data TEXT, staff_assigned TEXT, notes TEXT)''')
    
    conn.commit()
    conn.close()
import sqlite3

def get_connection():
    return sqlite3.connect('tailor_platform_v8.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, 
         shop_name TEXT, role TEXT, fee_status TEXT DEFAULT 'Unpaid')''')

    # Create Super Admin
    try:
        c.execute("INSERT INTO users (email, password, shop_name, role, fee_status) VALUES (?,?,?,?,?)", 
                  ('admin@sahilarman.com', 'sahilarman2026', 'Sahil & Arman IT Co', 'super_admin', 'Paid'))
    except: pass

    # Clients Table with pay_method
    c.execute('''CREATE TABLE IF NOT EXISTS clients 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, phone TEXT, 
         suits_count INTEGER, total REAL, advance REAL, remaining REAL,
         status TEXT, order_date DATE, delivery_date DATE, m_data TEXT, 
         staff_assigned TEXT, pay_method TEXT)''')
    
    conn.commit()
    conn.close()
