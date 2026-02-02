import customtkinter as ctk
from tkinter import ttk
import sqlite3
import modules.client_detail as cd
import os
import sys

class TailorMasterDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tailor Master Pro")
        self.geometry("1100x700")
        
        # Database Setup
        self.init_db()

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="AZAD\nTAILORS", font=("Arial", 28, "bold"), text_color="#3b8ed0").pack(pady=40)
        
        ctk.CTkButton(self.sidebar, text="+ Add New Client", height=45, fg_color="#2ecc71", hover_color="#27ae60", command=self.add_client).pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Refresh List", height=40, command=self.load_data).pack(pady=10, padx=20, fill="x")
        
        # --- Logout Button (Back to Login) ---
        ctk.CTkButton(self.sidebar, text="Logout / Back", height=40, fg_color="#e74c3c", hover_color="#c0392b", command=self.logout).pack(side="bottom", pady=30, padx=20, fill="x")

        # Main Area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Search
        self.search_ent = ctk.CTkEntry(self.main_frame, placeholder_text="Search Customer...", width=400)
        self.search_ent.pack(pady=10, padx=10, anchor="w")
        self.search_ent.bind("<KeyRelease>", lambda e: self.load_data(self.search_ent.get()))

        # Table
        self.tree = ttk.Treeview(self.main_frame, columns=("ID", "Name", "Phone", "Balance"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Customer Name")
        self.tree.heading("Phone", text="Mobile")
        self.tree.heading("Balance", text="Remaining Pay")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree.bind("<Double-1>", self.on_row_click)
        self.load_data()

    def init_db(self):
        conn = sqlite3.connect('tailor_pro.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS clients 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, 
             length TEXT, sleeves TEXT, shoulder TEXT, collar TEXT, chest TEXT, waist TEXT, hip TEXT, shalwar_len TEXT, bottom TEXT,
             total REAL, advance REAL, remaining REAL, extra_notes TEXT)''')
        conn.close()

    def load_data(self, search=""):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = sqlite3.connect('tailor_pro.db')
        query = "SELECT id, name, phone, remaining FROM clients"
        if search: query += f" WHERE name LIKE '%{search}%'"
        for r in conn.execute(query).fetchall():
            self.tree.insert("", "end", values=r)
        conn.close()

    def logout(self):
        self.destroy()
        # Login file ko dobara chalana
        os.system(f'"{sys.executable}" login.py')

    def add_client(self):
        cd.open_add_client_window(self.load_data)

    def on_row_click(self, event):
        item = self.tree.selection()[0]
        c_id = self.tree.item(item)['values'][0]
        cd.show_full_profile(c_id)

if __name__ == "__main__":
    app = TailorMasterDashboard()
    app.mainloop()