import sqlite3

def get_connection():
    return sqlite3.connect('tailor_pro_v4.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Clients Table with Advanced Fields
    c.execute('''CREATE TABLE IF NOT EXISTS clients 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, 
         suits_count INTEGER, total REAL, advance REAL, prev_balance REAL, remaining REAL,
         status TEXT, order_date DATE, delivery_date DATE, 
         m_data TEXT, pay_mode TEXT, staff_assigned TEXT, notes TEXT)''')
    
    # Settings Table
    c.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, shop_name TEXT, password TEXT, m_labels TEXT)''')
    if not c.execute("SELECT * FROM settings").fetchone():
        c.execute("INSERT INTO settings VALUES (1, 'Tailor Master Pro', '1234', 'Length,Sleeves,Shoulder,Collar,Chest,Waist,Hip,Bottom')")
    
    # Expenses Table
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, title TEXT, amount REAL, date DATE)''')
    
    # Staff Table
    c.execute('''CREATE TABLE IF NOT EXISTS staff (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT, phone TEXT)''')
    
    conn.commit()
    conn.close()