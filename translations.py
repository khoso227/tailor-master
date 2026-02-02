def get_text(lang):
    urdu = {
        "title": "ٹیلر ماسٹر پرو",
        "login": "لاگ ان",
        "register": "نیا اکاؤنٹ بنائیں",
        "forgot": "پاس ورڈ بھول گئے؟",
        "email": "ای میل",
        "pass": "پاس ورڈ",
        "shop": "دکان کا نام",
        "s_q": "سیکیورٹی سوال (بچپن کا دوست؟)",
        "s_a": "جواب",
        "dash": "ڈیش بورڈ",
        "new_order": "نیا آرڈر",
        "save": "محفوظ کریں",
        "remind": "پیمنٹ ریمائنڈر",
        "delete": "حذف کریں",
        "status": "حالت",
        "access": "لاگ ان ایکسیس"
    }
    
    english = {
        "title": "Tailor Master Pro",
        "login": "Login",
        "register": "Create Free Account",
        "forgot": "Forgot Password?",
        "email": "Email Address",
        "pass": "Password",
        "shop": "Shop Name",
        "s_q": "Security Question (Best Friend?)",
        "s_a": "Answer",
        "dash": "Dashboard",
        "new_order": "New Order",
        "save": "Save Order",
        "remind": "Send Reminder",
        "delete": "Delete Shop",
        "status": "Status",
        "access": "Login Access"
    }
    
    if lang == "Urdu":
        return urdu
    else:
        return english
