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

    # 2. Create Orders Table (Basic Structure)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, 
            client_name TEXT, 
            client_phone TEXT,
            order_date TEXT, 
            status TEXT DEFAULT 'Pending'
        )
    """)

    # --- AUTO-FIX LOGIC (Database Migration) ---
    # Ye section check karega ke agar koi column missing hai to usay add kar dega
    try:
        cursor = conn.cursor()
        # Maujooda columns ki list nikaalna
        cursor.execute("PRAGMA table_info(orders)")
        existing_columns = [info[1] for info in cursor.fetchall()]
        
        # Wo columns jo lazmi honay chahiye (Order Form ke mutabiq)
        required_cols = {
            "order_no": "TEXT",
            "measurement_data": "TEXT",
            "notes": "TEXT",
            "total_suits": "INTEGER DEFAULT 1",
            "total_bill": "REAL DEFAULT 0.0",
            "paid_amount": "REAL DEFAULT 0.0",
            "balance": "REAL DEFAULT 0.0",
            "is_synced": "INTEGER DEFAULT 0",
            "acc_no": "TEXT",
            "acc_name": "TEXT",
            "payment_via": "TEXT"
        }
        
        for col, col_type in required_cols.items():
            if col not in existing_columns:
                cursor.execute(f"ALTER TABLE orders ADD COLUMN {col} {col_type}")
                print(f"✅ Added missing column: {col}")
        
        # Expense table check
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER, description TEXT, amount REAL, exp_date TEXT
            )
        """)
        
    except Exception as e:
        print(f"Migration Notice: {e}")

    # 3. Create Default Admin
    admin_check = conn.execute("SELECT id FROM users WHERE email='admin@sahilarman.com'").fetchone()
    if not admin_check:
        conn.execute("""
            INSERT INTO users (email, password, shop_name, role, status) 
            VALUES ('admin@sahilarman.com', 'sahilarman2026', 'Super Admin', 'super_admin', 'Active')
        """)
    
    conn.commit()
    return conn

# Iske niche koi extra ALTER TABLE line nahi honi chahiye
