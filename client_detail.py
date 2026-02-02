import customtkinter as ctk
import sqlite3
from tkinter import messagebox

def open_add_client_window(callback):
    win = ctk.CTkToplevel()
    win.title("Add Measurement")
    win.geometry("550x750")
    win.attributes('-topmost', True)

    scroll = ctk.CTkScrollableFrame(win, width=500, height=700)
    scroll.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(scroll, text="CLIENT INFO", font=("Arial", 16, "bold")).pack(pady=5)
    name = ctk.CTkEntry(scroll, placeholder_text="Name", width=350); name.pack(pady=5)
    phone = ctk.CTkEntry(scroll, placeholder_text="Mobile", width=350); phone.pack(pady=5)

    # Measurement Fields
    fields = ["Length", "Sleeves", "Shoulder", "Collar", "Chest", "Waist", "Hip", "Shalwar Len", "Bottom"]
    entries = {}
    
    ctk.CTkLabel(scroll, text="MEASUREMENTS", font=("Arial", 16, "bold")).pack(pady=15)
    m_frame = ctk.CTkFrame(scroll)
    m_frame.pack(padx=20, fill="x")

    for i, field in enumerate(fields):
        r, c = divmod(i, 2)
        ctk.CTkLabel(m_frame, text=field+":").grid(row=r, column=c*2, padx=5, pady=5)
        e = ctk.CTkEntry(m_frame, width=100)
        e.grid(row=r, column=c*2+1, padx=5, pady=5)
        entries[field] = e

    total = ctk.CTkEntry(scroll, placeholder_text="Total Price", width=350); total.pack(pady=10)
    adv = ctk.CTkEntry(scroll, placeholder_text="Advance", width=350); adv.pack(pady=5)

    def save():
        try:
            rem = float(total.get()) - float(adv.get() if adv.get() else 0)
            conn = sqlite3.connect('tailor_pro.db')
            conn.execute('''INSERT INTO clients (name, phone, length, sleeves, shoulder, collar, chest, waist, hip, shalwar_len, bottom, total, advance, remaining, extra_notes) 
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                         (name.get(), phone.get(), entries["Length"].get(), entries["Sleeves"].get(), entries["Shoulder"].get(), 
                          entries["Collar"].get(), entries["Chest"].get(), entries["Waist"].get(), entries["Hip"].get(), 
                          entries["Shalwar Len"].get(), entries["Bottom"].get(), total.get(), adv.get(), rem, ""))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Saved!")
            callback()
            win.destroy()
        except: messagebox.showerror("Error", "Check Amounts")

    ctk.CTkButton(scroll, text="SAVE", command=save, fg_color="green", height=40).pack(pady=20)
    ctk.CTkButton(scroll, text="BACK / CANCEL", command=win.destroy, fg_color="gray").pack()

def show_full_profile(cid):
    pop = ctk.CTkToplevel()
    pop.geometry("450x600")
    pop.attributes('-topmost', True)
    
    conn = sqlite3.connect('tailor_pro.db')
    d = conn.execute("SELECT * FROM clients WHERE id=?", (cid,)).fetchone()
    conn.close()

    if d:
        ctk.CTkLabel(pop, text=f"Customer: {d[1]}", font=("Arial", 20, "bold")).pack(pady=15)
        # Displaying some measurements
        txt = f"Mobile: {d[2]}\n\nLength: {d[3]}\nSleeves: {d[4]}\nShoulder: {d[5]}\nCollar: {d[6]}\nChest: {d[7]}\nWaist: {d[8]}"
        ctk.CTkLabel(pop, text=txt, justify="left", font=("Arial", 14)).pack(pady=10)
        
        ctk.CTkLabel(pop, text=f"REMAINING: Rs. {d[14]}", text_color="red", font=("Arial", 18, "bold")).pack(pady=20)
        ctk.CTkButton(pop, text="BACK TO LIST", command=pop.destroy).pack(pady=10)