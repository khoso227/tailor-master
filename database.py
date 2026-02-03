import sqlite3
import json
from datetime import datetime

DB_NAME = "tailor_master_final.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Tables
    c.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, 
         shop_name TEXT, role TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, phone TEXT, 
         order_no TEXT, total_bill REAL, advance REAL, balance REAL, pay_method TEXT, 
         order_date TEXT, delivery_date TEXT, measurement_data TEXT, notes TEXT, status TEXT)''')

    # Force Insert Admin
    c.execute("INSERT OR REPLACE INTO users (id, email, password, shop_name, role) VALUES (1, ?, ?, ?, ?)", 
              ('admin@tailor.com', 'admin123', 'AZAD TAILOR', 'admin'))
    
    conn.commit()
    conn.close()
