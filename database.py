import sqlite3

def get_connection():
    conn = sqlite3.connect("tailor_master.db", check_same_thread=False)
    # Merged Orders Table (Includes Measurements + Billing + Bank Info)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, client_name TEXT, client_phone TEXT,
            length TEXT, sleeves TEXT, shoulder TEXT, collar TEXT, 
            lower_chest TEXT, hip_ghera TEXT, shalwar_length TEXT, bottom TEXT,
            design_left TEXT, design_right TEXT, patti_size TEXT, pocket_dim TEXT, 
            verbal_notes TEXT, custom_fields TEXT,
            total_suits INTEGER, total_bill REAL, paid_amount REAL, balance REAL,
            acc_no TEXT, acc_name TEXT, payment_via TEXT,
            order_date TEXT, status TEXT DEFAULT 'Pending'
        )
    """)
    # Daily Expenses Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER, description TEXT, amount REAL, exp_date TEXT
        )
    """)
    # Auto Admin creation
    admin_check = conn.execute("SELECT id FROM users WHERE email='admin@sahilarman.com'").fetchone()
    if not admin_check:
        conn.execute("INSERT INTO users (email, password, shop_name, role, status) VALUES ('admin@sahilarman.com', 'sahilarman2026', 'Super Admin', 'super_admin', 'Active')")
    conn.commit()
    return conn
