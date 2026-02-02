import customtkinter as ctk
from tkinter import messagebox
from main import TailorMasterDashboard

def handle_login():
    if user_ent.get() == "admin" and pass_ent.get() == "1234":
        app.destroy()
        dashboard = TailorMasterDashboard()
        dashboard.mainloop()
    else:
        messagebox.showerror("Error", "Invalid Credentials")

app = ctk.CTk()
app.title("Login - Tailor Master")
app.geometry("400x500")

ctk.CTkLabel(app, text="AZAD TAILORS\nMANAGEMENT", font=("Arial", 24, "bold"), text_color="#3b8ed0").pack(pady=50)
user_ent = ctk.CTkEntry(app, placeholder_text="Username", width=280, height=45); user_ent.pack(pady=10)
pass_ent = ctk.CTkEntry(app, placeholder_text="Password", show="*", width=280, height=45); pass_ent.pack(pady=10)

ctk.CTkButton(app, text="LOGIN", command=handle_login, width=280, height=45, font=("Arial", 16, "bold")).pack(pady=30)
ctk.CTkLabel(app, text="v1.0 Live Project", text_color="gray").pack(side="bottom", pady=20)

app.mainloop()