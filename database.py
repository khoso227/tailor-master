import sqlite3
import json
from datetime import datetime

DB_NAME = "tailor_master_pro.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    # 1. Users Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, 
            password TEXT, shop_name TEXT, role TEXT)""")

    # 2. Clients Table (Customer Management)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            name TEXT, phone TEXT UNIQUE, email TEXT, address TEXT, notes TEXT)""")

    # 3. Orders Table (Azad Tailor Digital Slip)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, client_id INTEGER,
            client_name TEXT, client_phone TEXT, order_no TEXT UNIQUE,
            order_date TEXT, delivery_date TEXT, status TEXT DEFAULT 'Pending',
            suits INTEGER DEFAULT 1, total_bill REAL, advance REAL, balance REAL,
            measurement_data TEXT, notes TEXT, address TEXT, is_synced INTEGER DEFAULT 0)""")

    # 4. Payments Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, 
            amount REAL, payment_date TEXT, payment_method TEXT, notes TEXT)""")

    # Default Login
    try:
        conn.execute("INSERT OR IGNORE INTO users (email, password, shop_name, role) VALUES (?,?,?,?)",
                     ('admin@sahilarman.com', 'sahilarman2026', 'AZAD TAILOR', 'admin'))
    except: pass
    conn.commit()
    conn.close()

def add_client(name, phone, email, address, notes, user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clients (user_id, name, phone, email, address, notes) VALUES (?,?,?,?,?,?)",
                       (user_id, name, phone, email, address, notes))
        conn.commit()
        return cursor.lastrowid
    except: return None # Client exists

def quick_search_customers(term, user_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    res = conn.execute("SELECT * FROM clients WHERE (name LIKE ? OR phone LIKE ?) AND user_id=?", 
                       (f"%{term}%", f"%{term}%", user_id)).fetchall()
    return [dict(row) for row in res]
