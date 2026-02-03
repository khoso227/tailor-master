import requests # Internet check karne ke liye
import sqlite3

def sync_data_to_cloud():
    # 1. Check karein ke internet hai ya nahi
    try:
        requests.get("https://www.google.com", timeout=3)
        internet = True
    except:
        internet = False

    if internet:
        # 2. Local database se wo data uthain jo sync nahi hua (is_synced = 0)
        local_conn = sqlite3.connect('tailor_offline.db')
        cursor = local_conn.cursor()
        unsynced_orders = cursor.execute("SELECT * FROM orders WHERE is_synced=0").fetchall()

        if unsynced_orders:
            for order in unsynced_orders:
                # 3. Yahan Cloud Database (PostgreSQL/MySQL) mein data insert karne ki logic aayegi
                # Agar aap Supabase ya Firebase use kar rahe hain to unki API call hogi
                
                # 4. Success hone par local record ko update kar dein
                cursor.execute("UPDATE orders SET is_synced=1 WHERE id=?", (order[0],))
            
            local_conn.commit()
            return f"✅ {len(unsynced_orders)} Orders synced to cloud!"
        else:
            return "ℹ️ Everything is already up to date."
    else:
        return "❌ No internet! Data saved locally."