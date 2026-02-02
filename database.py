import sqlite3

def get_connection():
    return sqlite3.connect('tailor_platform_v5.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Users Table (Super Admin & Shop Admins)
    c.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
         email TEXT UNIQUE, 
         password TEXT, 
         shop_name TEXT, 
         role TEXT)''') # Roles: 'super_admin', 'admin'

    # Super Admin Default Account (Sahil & Arman)
    try:
        c.execute("INSERT INTO users (email, password, shop_name, role) VALUES (?,?,?,?)", 
                  ('admin@sahilarman.com', 'sahilarman2026', 'Sahil & Arman IT Co', 'super_admin'))
    except: pass # Already exists

    # 2. Advanced Clients Table (Linked to User ID)
    c.execute('''CREATE TABLE IF NOT EXISTS clients 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
         user_id INTEGER,
         name TEXT, phone TEXT, suits_count INTEGER, total REAL, advance REAL, remaining REAL,
         status TEXT, order_date DATE, delivery_date DATE, m_data TEXT, staff_assigned TEXT)''')
    
    # 3. Staff Table
    c.execute('''CREATE TABLE IF NOT EXISTS staff (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, role TEXT)''')
    
    conn.commit()
    conn.close()
