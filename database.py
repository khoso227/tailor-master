import sqlite3
import json
from datetime import datetime

# Database name constant
DB_NAME = "tailor_master.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    
    # 1. Create Users Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            email TEXT UNIQUE, 
            password TEXT, 
            shop_name TEXT, 
            role TEXT, 
            phone TEXT, 
            security_q TEXT, 
            security_a TEXT, 
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
            status TEXT DEFAULT 'Pending',
            delivery_date TEXT,
            suits INTEGER DEFAULT 1,
            measurement_data TEXT,
            design_data TEXT,
            total_bill REAL DEFAULT 0.0,
            advance REAL DEFAULT 0.0,
            balance REAL DEFAULT 0.0,
            status_history TEXT,
            notes TEXT,
            is_synced INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Create Clients Table (For better customer management)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            phone TEXT UNIQUE,
            email TEXT,
            address TEXT,
            measurement_template TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. Create Payments Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            amount REAL,
            payment_date TEXT,
            payment_method TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    # 5. Create Expenses Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER, 
            description TEXT, 
            amount REAL, 
            exp_date TEXT,
            category TEXT DEFAULT 'General',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- AUTO-FIX LOGIC (Database Migration) ---
    try:
        cursor = conn.cursor()
        
        # Check and add missing columns for orders table
        cursor.execute("PRAGMA table_info(orders)")
        existing_columns = [info[1] for info in cursor.fetchall()]
        
        # Required columns for orders
        required_order_cols = {
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
            "payment_via": "TEXT",
            "delivery_date": "TEXT",
            "design_data": "TEXT",
            "advance": "REAL DEFAULT 0.0",
            "status_history": "TEXT"
        }
        
        for col, col_type in required_order_cols.items():
            if col not in existing_columns:
                cursor.execute(f"ALTER TABLE orders ADD COLUMN {col} {col_type}")
                print(f"✅ Added missing column to orders: {col}")
        
        # Check and add missing columns for clients table
        cursor.execute("PRAGMA table_info(clients)")
        existing_client_columns = [info[1] for info in cursor.fetchall()] if cursor.fetchall() else []
        
        required_client_cols = {
            "email": "TEXT",
            "address": "TEXT",
            "measurement_template": "TEXT",
            "notes": "TEXT",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
        
        for col, col_type in required_client_cols.items():
            if col not in existing_client_columns:
                cursor.execute(f"ALTER TABLE clients ADD COLUMN {col} {col_type}")
                print(f"✅ Added missing column to clients: {col}")
        
    except Exception as e:
        print(f"Migration Notice: {e}")

    # 6. Create Default Admin if not exists
    admin_check = conn.execute("SELECT id FROM users WHERE email='admin@sahilarman.com'").fetchone()
    if not admin_check:
        conn.execute("""
            INSERT INTO users (email, password, shop_name, role, status) 
            VALUES ('admin@sahilarman.com', 'sahilarman2026', 'Super Admin', 'super_admin', 'Active')
        """)
        print("✅ Default admin created")
    
    conn.commit()
    return conn

# Initialize database
def init_db():
    return get_connection()

# --- ORDER STATUS MANAGEMENT FUNCTIONS ---
def add_order_status_columns():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if status_history column exists
    cursor.execute("PRAGMA table_info(orders)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'status_history' not in columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN status_history TEXT")
        print("✅ Added status_history column to orders table")
    
    conn.commit()
    conn.close()

def update_order_status(order_id, new_status, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get current status history
    cursor.execute("SELECT status_history FROM orders WHERE id=?", (order_id,))
    result = cursor.fetchone()
    
    history = []
    if result and result[0]:
        try:
            history = json.loads(result[0])
        except:
            history = []
    
    # Add new status entry
    history.append({
        'status': new_status,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'notes': notes
    })
    
    # Update database
    cursor.execute("""
        UPDATE orders 
        SET status = ?, status_history = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    """, (new_status, json.dumps(history), order_id))
    
    conn.commit()
    conn.close()
    return True

def get_order_status_history(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status_history FROM orders WHERE id=?", (order_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        try:
            return json.loads(result[0])
        except:
            return []
    return []

# --- CLIENT MANAGEMENT FUNCTIONS ---
def add_client(name, phone, email="", address="", notes="", user_id=1):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO clients (user_id, name, phone, email, address, notes) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, phone, email, address, notes))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Client already exists with this phone
        return None
    finally:
        conn.close()

def search_clients(name="", phone="", min_orders=0, last_order_days=0):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT c.*, 
           COUNT(o.id) as total_orders,
           MAX(o.order_date) as last_order_date
    FROM clients c
    LEFT JOIN orders o ON c.id = o.client_id
    WHERE 1=1
    """
    
    params = []
    
    if name:
        query += " AND c.name LIKE ?"
        params.append(f"%{name}%")
    
    if phone:
        query += " AND c.phone LIKE ?"
        params.append(f"%{phone}%")
    
    query += " GROUP BY c.id"
    
    if min_orders > 0:
        query += " HAVING COUNT(o.id) >= ?"
        params.append(min_orders)
    
    cursor.execute(query, params)
    clients = cursor.fetchall()
    
    # Filter by last order days if specified
    if last_order_days > 0:
        cutoff_date = (datetime.now() - timedelta(days=last_order_days)).strftime("%Y-%m-%d")
        clients = [c for c in clients if c[9] and c[9] >= cutoff_date]  # last_order_date is index 9
    
    # Convert to list of dictionaries
    columns = [description[0] for description in cursor.description]
    result = [dict(zip(columns, client)) for client in clients]
    
    conn.close()
    return result

def quick_search_customers(search_term, user_id=1):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT id, name, phone, email, address 
    FROM clients 
    WHERE (name LIKE ? OR phone LIKE ?) AND user_id = ?
    LIMIT 10
    """
    
    cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", user_id))
    customers = cursor.fetchall()
    
    columns = [description[0] for description in cursor.description]
    result = [dict(zip(columns, customer)) for customer in customers]
    
    conn.close()
    return result

# --- ORDER MANAGEMENT FUNCTIONS ---
def get_all_orders(user_id=1, status_filter=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT o.*, c.name as client_name, c.phone as client_phone 
    FROM orders o
    LEFT JOIN clients c ON o.client_id = c.id
    WHERE o.user_id = ?
    """
    
    params = [user_id]
    
    if status_filter and status_filter != "All":
        query += " AND o.status = ?"
        params.append(status_filter)
    
    query += " ORDER BY o.order_date DESC, o.id DESC"
    
    cursor.execute(query, params)
    orders = cursor.fetchall()
    
    columns = [description[0] for description in cursor.description]
    result = [dict(zip(columns, order)) for order in orders]
    
    conn.close()
    return result

def get_today_summary(user_id=1):
    conn = get_connection()
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Today's orders count
    cursor.execute("SELECT COUNT(*) FROM orders WHERE order_date = ? AND user_id = ?", (today, user_id))
    today_orders = cursor.fetchone()[0]
    
    # Today's deliveries
    cursor.execute("SELECT COUNT(*) FROM orders WHERE delivery_date = ? AND status = 'Delivered' AND user_id = ?", 
                   (today, user_id))
    today_deliveries = cursor.fetchone()[0]
    
    # Today's revenue
    cursor.execute("SELECT SUM(total_bill) FROM orders WHERE delivery_date = ? AND status = 'Delivered' AND user_id = ?", 
                   (today, user_id))
    today_revenue = cursor.fetchone()[0] or 0
    
    # Today's payments received
    cursor.execute("SELECT SUM(amount) FROM payments p JOIN orders o ON p.order_id = o.id WHERE p.payment_date = ? AND o.user_id = ?", 
                   (today, user_id))
    today_payments = cursor.fetchone()[0] or 0
    
    # Pending orders
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status != 'Delivered' AND user_id = ?", (user_id,))
    pending_orders = cursor.fetchone()[0]
    
    # Total outstanding balance
    cursor.execute("SELECT SUM(balance) FROM orders WHERE balance > 0 AND user_id = ?", (user_id,))
    total_outstanding = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'today_orders': today_orders,
        'today_deliveries': today_deliveries,
        'today_revenue': today_revenue,
        'today_payments': today_payments,
        'pending_orders': pending_orders,
        'total_outstanding': total_outstanding
    }

def get_weekly_sales(user_id=1):
    conn = get_connection()
    
    # Last 7 days sales
    query = """
    SELECT date(delivery_date) as date, 
           COUNT(*) as order_count,
           SUM(total_bill) as sales
    FROM orders 
    WHERE status = 'Delivered' 
    AND user_id = ?
    AND delivery_date >= date('now', '-7 days')
    GROUP BY date(delivery_date)
    ORDER BY date
    """
    
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries
    return [
        {'date': r[0], 'order_count': r[1], 'sales': r[2] or 0}
        for r in results
    ]

# --- EXPORT FUNCTIONS ---
def export_data(data_type, start_date, end_date, user_id=1):
    conn = get_connection()
    
    if data_type == "orders":
        query = f"""
        SELECT o.id, o.order_no, c.name as client_name, c.phone, 
               o.order_date, o.delivery_date, o.status,
               o.suits, o.total_bill, o.advance, o.balance, o.notes
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.id
        WHERE o.user_id = ? 
        AND o.order_date BETWEEN ? AND ?
        ORDER BY o.order_date DESC
        """
        params = (user_id, start_date, end_date)
    elif data_type == "clients":
        query = "SELECT * FROM clients WHERE user_id = ?"
        params = (user_id,)
    elif data_type == "payments":
        query = f"""
        SELECT p.id, c.name as client_name, o.order_no, p.amount,
               p.payment_date, p.payment_method, p.notes
        FROM payments p
        JOIN orders o ON p.order_id = o.id
        JOIN clients c ON o.client_id = c.id
        WHERE o.user_id = ? 
        AND p.payment_date BETWEEN ? AND ?
        ORDER BY p.payment_date DESC
        """
        params = (user_id, start_date, end_date)
    else:
        # Complete database summary
        query = """
        SELECT 'orders' as table_name, COUNT(*) as count FROM orders WHERE user_id = ?
        UNION ALL
        SELECT 'clients' as table_name, COUNT(*) as count FROM clients WHERE user_id = ?
        UNION ALL
        SELECT 'payments' as table_name, COUNT(*) as count FROM payments p JOIN orders o ON p.order_id = o.id WHERE o.user_id = ?
        """
        params = (user_id, user_id, user_id)
    
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    columns = [description[0] for description in cursor.description]
    data = [dict(zip(columns, row)) for row in results]
    
    conn.close()
    return data, columns

# --- CREATE QUICK ORDER FUNCTION ---
def create_quick_order(client_id, order_type, quantity=1, urgent=False, user_id=1):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get client details
    cursor.execute("SELECT name, phone FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    
    if not client:
        conn.close()
        return False
    
    client_name, client_phone = client
    
    # Generate order number
    order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Insert order
    cursor.execute("""
        INSERT INTO orders (
            user_id, client_id, client_name, client_phone, 
            order_date, delivery_date, status, suits, 
            order_no, total_bill, advance, balance, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, client_id, client_name, client_phone,
        datetime.now().strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        'Pending' if not urgent else 'Urgent',
        quantity,
        order_no,
        0.0,  # Will be updated later
        0.0,
        0.0,
        f"Quick order: {order_type}" + (" (Urgent)" if urgent else "")
    ))
    
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return order_id

# Required imports for time operations
from datetime import timedelta

# Make sure timedelta is imported at the top
