import sqlite3

def get_connection():
    conn = sqlite3.connect("tailor_master.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, client_name TEXT, client_phone TEXT,
            length TEXT, sleeves TEXT, shoulder TEXT, collar TEXT, 
            lower_chest TEXT, hip_ghera TEXT, shalwar_length TEXT, bottom TEXT,
            design_left TEXT, design_right TEXT,
            patti_size TEXT, pocket_dim TEXT, 
            verbal_notes TEXT, custom_fields TEXT,
            total_bill REAL, paid_amount REAL, order_date TEXT
        )
    """)
    conn.commit()
    return conn
