# translations.py (Modular Sync Version 20.0)

TRANSLATIONS = {
    "English": {
        # --- Authentication & Navigation ---
        "title": "Tailor Master Pro 👔",
        "lang_label": "Language 🌐",
        "theme_label": "Theme Mood 🎨",
        "shuffle": "🔀 Shuffle Wallpaper",
        "dash": "Dashboard",
        "order": "New Order ➕",
        "report": "Reports 📋",
        "sec": "Security / Settings ⚙️",
        "logout": "Logout 🚪",
        "login_btn": "Login Now",
        "email": "Email Address",
        "pass": "Password",
        "reg_btn": "Register Shop",
        "forgot_btn": "Forgot Password?",
        "shop": "Shop Name",
        "phone": "Phone Number",
        "s_q": "Security Question",
        "s_a": "Answer",
        "back": "← Back",
        
        # --- Client & Diary Measurements (Fractions Support) ---
        "c_name": "Client Name",
        "c_phone": "Phone Number",
        "measure": "Measurements (Inches) 📏",
        "len": "Length (لمبائی)",
        "slv": "Sleeves (آستین)",
        "shl": "Shoulder (تیرا)",
        "col": "Collar (کالر)",
        "chst": "Chest (چھاتی)",
        "hip": "Hip / Ghera (گھیرا)",
        "sh_len": "Shalwar Length",
        "bot": "Pancha / Bottom",
        
        # --- Design Selection (Diary Layout) ---
        "design_l": "Design Details (Left Column)",
        "design_r": "Design Details (Right Column)",
        "patti": "Front Placket (Patti Size)",
        "pock_dim": "Pocket Size (LxW)",
        "verbal": "Verbal Instructions (Notes)",
        "add_field": "➕ Add Custom Column",
        "save": "Save Order to Diary ✅",
        
        # --- Account & System Settings ---
        "rename_shop": "Rename Shop",
        "update": "Update Name",
        "success_save": "Order Registered Successfully!",
        "error_fill": "Please fill essential fields!"
    },
    
    "Urdu": {
        # --- Authentication & Navigation ---
        "title": "ٹیلر ماسٹر پرو 👔",
        "lang_label": "زبان 🌐",
        "theme_label": "تھیم 🎨",
        "shuffle": "تبدیل کریں 🔀",
        "dash": "ڈیش بورڈ",
        "order": "نیا آرڈر ➕",
        "report": "رپورٹس 📋",
        "sec": "سیکیورٹی ⚙️",
        "logout": "لاگ آؤٹ 🚪",
        "login_btn": "لاگ ان کریں",
        "email": "ای میل",
        "pass": "پاس ورڈ",
        "reg_btn": "رجسٹریشن",
        "forgot_btn": "پاس ورڈ بھول گئے؟",
        "shop": "دکان کا نام",
        "phone": "فون نمبر",
        "s_q": "سیکیورٹی سوال",
        "s_a": "جواب",
        "back": "واپس ←",
        
        # --- Client & Diary Measurements ---
        "c_name": "گاہک کا نام",
        "c_phone": "فون نمبر",
        "measure": "پیمائش (انچ میں) 📏",
        "len": "لمبائی (Length)",
        "slv": "آستین (Sleeves)",
        "shl": "تیرا / کندھا (Shoulder)",
        "col": "کالر (Collar)",
        "chst": "چھاتی (Chest)",
        "hip": "گھیرا / ہپ (Hip)",
        "sh_len": "شلوار لمبائی",
        "bot": "پائنچہ (Bottom)",
        
        # --- Design Selection ---
        "design_l": "ڈیزائن کی تفصیل (بائیں طرف)",
        "design_r": "ڈیزائن کی تفصیل (دائیں طرف)",
        "patti": "سامنے پٹی کا سائز (Patti)",
        "pock_dim": "پاکٹ سائز (LxW)",
        "verbal": "زبانی ہدایات (خصوصی نوٹس)",
        "add_field": "➕ نیا کالم شامل کریں",
        "save": "آرڈر محفوظ کریں ✅",
        
        # --- Account & System Settings ---
        "rename_shop": "دکان کا نام بدلیں",
        "update": "اپ ڈیٹ کریں",
        "success_save": "آرڈر کامیابی سے محفوظ ہو گیا!",
        "error_fill": "براہ کرم ضروری معلومات درج کریں!"
    }
}
TRANSLATIONS = {
    "English": {
        "cashbook": "Cashbook 💰", "today_inc": "Today's Income", "today_exp": "Today's Expense", "savings": "Net Savings",
        "add_exp": "Add Expense", "exp_desc": "Expense Detail", "amount": "Amount", "suits": "Total Suits (Jore)",
        "acc_no": "Account Number", "acc_name": "Account Holder", "via": "Payment Service", "bal": "Remaining Balance",
        # ... baaki purani keys ...
    },
    "Urdu": {
        "cashbook": "روزنامچہ (کیش بک) 💰", "today_inc": "آج کی آمدنی", "today_exp": "آج کا خرچہ", "savings": "آج کی بچت",
        "add_exp": "خرچہ درج کریں", "exp_desc": "خرچے کی تفصیل", "amount": "رقم", "suits": "کل جوڑے",
        "acc_no": "اکاؤنٹ نمبر", "acc_name": "اکاؤنٹ ہولڈر کا نام", "via": "سروس (جاز کیش/بینک)", "bal": "باقیہ رقم",
    }
}
# Helper function for modular files
def get_text(lang):
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"])

