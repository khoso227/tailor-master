import sqlite3
import json
from datetime import datetime

DB_NAME = "tailor_master_v11.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    # 1. Users Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            email TEXT UNIQUE, password TEXT, shop_name TEXT, role TEXT
        )
    """)

    # 2. Clients/Orders Table (Combined for Azad Tailor Slip)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, name TEXT, phone TEXT, order_no TEXT,
            total REAL DEFAULT 0, advance REAL DEFAULT 0, remaining REAL DEFAULT 0,
            pay_method TEXT, order_date TEXT, delivery_date TEXT,
            m_data TEXT, verbal_notes TEXT, status TEXT DEFAULT 'Pending'
        )
    """)

    # --- Migration Logic ---
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(clients)")
        cols = [info[1] for info in cursor.fetchall()]
        if 'verbal_notes' not in cols:
            cursor.execute("ALTER TABLE clients ADD COLUMN verbal_notes TEXT")
        if 'pay_method' not in cols:
            cursor.execute("ALTER TABLE clients ADD COLUMN pay_method TEXT")
    except: pass

    # Default Admin
    try:
        conn.execute("INSERT OR IGNORE INTO users (email, password, shop_name, role) VALUES (?,?,?,?)",
                     ('admin@tailor.com', 'admin123', 'AZAD TAILOR', 'admin'))
    except: pass
    
    conn.commit()
    conn.close()
