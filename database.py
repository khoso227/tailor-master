import sqlite3

def get_connection():
    return sqlite3.connect('tailor_platform_v6.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Users Table with Fee Status
    c.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, 
         shop_name TEXT, role TEXT, fee_status TEXT DEFAULT 'Unpaid')''')

    # Default Super Admin
    try:
        c.execute("INSERT INTO users (email, password, shop_name, role, fee_status) VALUES (?,?,?,?,?)", 
                  ('admin@sahilarman.com', 'sahilarman2026', 'Sahil & Arman IT Co', 'super_admin', 'Paid'))
    except: pass

    # Clients Table
    c.execute('''CREATE TABLE IF NOT EXISTS clients 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, phone TEXT, 
         suits_count INTEGER, total REAL, advance REAL, remaining REAL,
         status TEXT, order_date DATE, delivery_date DATE, m_data TEXT, staff_assigned TEXT)''')
    
    conn.commit()
    conn.close()
