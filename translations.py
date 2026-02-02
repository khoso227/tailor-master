TRANSLATIONS = {
    "English": {
        "measure": "Measurements (Inches)", "design_l": "Design Details (Left)", "design_r": "Design Details (Right)",
        "len": "Length", "slv": "Sleeves", "shl": "Shoulder", "col": "Collar", "chst": "Chest", "hip": "Hip/Ghera",
        "sh_len": "Shalwar Length", "bot": "Bottom (Pancha)",
        "patti": "Front Placket (Patti)", "pock_dim": "Pocket Size (LxW)", "verbal": "Verbal Instructions",
        "add_field": "➕ Add Custom Field", "field_name": "Field Name (e.g. Color)", "field_val": "Value",
        "save": "Save Order ✅"
    },
    "Urdu": {
        "measure": "پیمائش (انچ میں)", "design_l": "ڈیزائن کی تفصیل (بائیں طرف)", "design_r": "ڈیزائن کی تفصیل (دائیں طرف)",
        "len": "لمبائی (Length)", "slv": "آستین (Sleeves)", "shl": "تیرا (Shoulder)", "col": "کالر (Collar)",
        "chst": "چھاتی (Lower Chest)", "hip": "گھیرا (Hip)", "sh_len": "شلوار لمبائی", "bot": "پائنچہ (Bottom)",
        "patti": "سامنے پٹی (Patti Size)", "pock_dim": "پاکٹ سائز (LxW)", "verbal": "زبانی ہدایات (Notes)",
        "add_field": "➕ نیا کالم شامل کریں", "field_name": "کالم کا نام (مثلاً رنگ)", "field_val": "معلومات",
        "save": "آرڈر محفوظ کریں ✅"
    }
}
# translations.py (Final Sync Version)

TRANSLATIONS = {
    "English": {
        # Navigation & Sidebar
        "title": "Tailor Master Pro 👔",
        "lang_label": "Language 🌐",
        "theme_label": "Theme Mood 🎨",
        "shuffle": "🔀 Shuffle Wallpaper",
        "dash": "Dashboard",
        "order": "New Order ➕",
        "report": "Reports 📋",
        "sec": "Security / Settings ⚙️",
        "logout": "Logout 🚪",
        
        # Auth
        "login_btn": "Login Now",
        "email": "Email Address",
        "pass": "Password",
        "reg_btn": "Register Shop",
        "forgot_btn": "Forgot Password?",
        
        # Order Form - Measurements
        "c_name": "Client Name",
        "c_phone": "Phone Number",
        "measure": "Measurements (Inches)",
        "len": "Length",
        "slv": "Sleeves",
        "shl": "Shoulder (Teera)",
        "col": "Collar",
        "chst": "Chest (Chaati)",
        "hip": "Hip / Ghera",
        "sh_len": "Shalwar Length",
        "bot": "Pancha / Bottom",
        
        # Design Labels
        "design_l": "Design Details (Left)",
        "design_r": "Design Details (Right)",
        "patti": "Front Placket (Patti Size)",
        "pock_dim": "Pocket Size (LxW)",
        "verbal": "Verbal Instructions (Special Notes)",
        "add_field": "➕ Add Custom Field",
        "save": "Save Order ✅",
        
        # Settings
        "rename_shop": "Rename Shop",
        "update": "Update Name"
    },
    
    "Urdu": {
        # Navigation & Sidebar
        "title": "ٹیلر ماسٹر پرو 👔",
        "lang_label": "زبان تبدیل کریں 🌐",
        "theme_label": "تھیم تبدیل کریں 🎨",
        "shuffle": "وال پیپر تبدیل کریں 🔀",
        "dash": "ڈیش بورڈ",
        "order": "نیا آرڈر ➕",
        "report": "رپورٹس 📋",
        "sec": "سیکیورٹی / سیٹنگز ⚙️",
        "logout": "لاگ آؤٹ 🚪",
        
        # Auth
        "login_btn": "لاگ ان کریں",
        "email": "ای میل",
        "pass": "پاس ورڈ",
        "reg_btn": "رجسٹریشن",
        "forgot_btn": "پاس ورڈ بھول گئے؟",
        
        # Order Form - Measurements
        "c_name": "گاہک کا نام",
        "c_phone": "فون نمبر",
        "measure": "پیمائش (انچ میں)",
        "len": "لمبائی (Length)",
        "slv": "آستین (Sleeves)",
        "shl": "تیرا / کندھا (Shoulder)",
        "col": "کالر (Collar)",
        "chst": "چھاتی (Chest)",
        "hip": "گھیرا / ہپ (Hip)",
        "sh_len": "شلوار لمبائی",
        "bot": "پائنچہ (Bottom)",
        
        # Design Labels
        "design_l": "ڈیزائن کی تفصیل (بائیں طرف)",
        "design_r": "ڈیزائن کی تفصیل (دائیں طرف)",
        "patti": "سامنے پٹی کا سائز (Patti)",
        "pock_dim": "پاکٹ سائز (LxW)",
        "verbal": "زبانی ہدایات (Notes)",
        "add_field": "➕ نیا کالم شامل کریں",
        "save": "آرڈر محفوظ کریں ✅",
        
        # Settings
        "rename_shop": "دکان کا نام تبدیل کریں",
        "update": "اپ ڈیٹ کریں"
    }
}

def get_text(lang):
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"])
