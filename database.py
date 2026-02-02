import sqlite3

def get_connection():
    conn = sqlite3.connect("tailor_master.db", check_same_thread=False)
    
    # 1. Create Users Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            email TEXT UNIQUE, password TEXT, shop_name TEXT, 
            role TEXT, phone TEXT, security_q TEXT, security_a TEXT, 
            status TEXT DEFAULT 'Active'
        )
    """)

    # 2. Create Orders Table with all new columns
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

    # --- AUTO-FIX LOGIC (Database Migration) ---
    # Agar purani table hai to ye naye columns add kar dega bina data delete kiye
    try:
        cursor = conn.cursor()
        existing_columns = [info[1] for info in cursor.execute("PRAGMA table_info(orders)").fetchall()]
        
        # New columns to add if they don't exist
        new_cols = {
            "total_suits": "INTEGER DEFAULT 1",
            "balance": "REAL DEFAULT 0.0",
            "acc_no": "TEXT",
            "acc_name": "TEXT",
            "payment_via": "TEXT"
        }
        
        for col, col_type in new_cols.items():
            if col not in existing_columns:
                cursor.execute(f"ALTER TABLE orders ADD COLUMN {col} {col_type}")
                print(f"Added missing column: {col}")
        
        # Expense table check
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER, description TEXT, amount REAL, exp_date TEXT
            )
        """)
        
    except Exception as e:
        print(f"Migration Notice: {e}")

    # Create Admin
    admin_check = conn.execute("SELECT id FROM users WHERE email='admin@sahilarman.com'").fetchone()
    if not admin_check:
        conn.execute("INSERT INTO users (email, password, shop_name, role, status) VALUES ('admin@sahilarman.com', 'sahilarman2026', 'Super Admin', 'super_admin', 'Active')")
    
    conn.commit()
    return conn
