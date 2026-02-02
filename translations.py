def get_text(lang):
    urdu = {
        "title": "ٹیلر ماسٹر پرو", "login": "لاگ ان", "register": "نیا اکاؤنٹ بنائیں",
        "forgot": "پاس ورڈ بھول گئے؟", "email": "ای میل", "pass": "پاس ورڈ",
        "shop": "دکان کا نام", "phone": "موبائل نمبر", "s_q": "سیکیورٹی سوال", "s_a": "جواب",
        "dash": "ڈیش بورڈ", "new_order": "نیا آرڈر", "save": "محفوظ کریں",
        "remind": "پیمنٹ ریمائنڈر", "delete": "حذف کریں", "status": "حالت"
    }
    english = {
        "title": "Tailor Master Pro", "login": "Login", "register": "Create Free Account",
        "forgot": "Forgot Password?", "email": "Email Address", "pass": "Password",
        "shop": "Shop Name", "phone": "Mobile Number", "s_q": "Security Question", "s_a": "Answer",
        "dash": "Dashboard", "new_order": "New Order", "save": "Save Order",
        "remind": "Send Reminder", "delete": "Delete Shop", "status": "Status"
    }
    return urdu if lang == "Urdu" else english
