import sqlite3

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect('tailor_shop.db', check_same_thread=False)
    
    # Create tables if they don't exist
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        shop_name TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        phone TEXT,
        security_q TEXT,
        security_a TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        client_name TEXT NOT NULL,
        client_phone TEXT,
        total_bill REAL NOT NULL,
        paid_amount REAL DEFAULT 0,
        balance REAL DEFAULT 0,
        order_date DATE NOT NULL,
        delivery_date DATE,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        exp_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    return conn
