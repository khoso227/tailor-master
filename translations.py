def get_text(lang):
    urdu = {
        "title": "ٹیلر ماسٹر پرو", "login": "لاگ ان", "register": "نیا اکاؤنٹ بنائیں",
        "forgot": "پاس ورڈ بھول گئے؟", "email": "ای میل", "pass": "پاس ورڈ",
        "shop": "دکان کا نام", "phone": "موبائل نمبر", "s_q": "سیکیورٹی سوال", "s_a": "جواب",
        "dash": "ڈیش بورڈ", "new_order": "نیا آرڈر", "reports": "رپورٹس", "security": "سیکیورٹی",
        "cust_name": "گاہک کا نام", "total": "کل بل", "advance": "ایڈوانس",
        "rem": "باقی رقم", "pay_mode": "ادائیگی کا طریقہ", "del_date": "ڈیلیوری کی تاریخ",
        "meas": "پیمائش (Measurements)", "styles": "ڈیزائن اور اسٹائل", "save": "آرڈر محفوظ کریں",
        "verbal": "زبانی ہدایات (Special Notes)", "extra": "اضافی ضرورت",
        # Measurements Labels
        "len": "لمبائی (Length)", "slv": "آستین (Sleeves)", "shl": "تیرا (Shoulder)",
        "col": "گلا (Collar)", "chst": "چھاتی (Chest)", "l_chst": "گھیرا (Lower Chest)",
        "wst": "کمر (Waist)", "hip": "ہپ (Hip)", "shl_len": "شلوار لمبائی",
        "shl_bot": "پانچہ (Bottom)", "paj_len": "پاجامہ لمبائی", "paj_wst": "پاجامہ کمر",
        "paj_hip": "پاجامہ ہپ", "paj_thi": "تھائی (Thigh)", "paj_bot": "پاجامہ پانچہ",
        "fly": "فلائی (Fly)", "shirt_len": "شرٹ لمبائی",
        # Style Labels
        "sh_col": "شرٹ کالر", "sw_col": "شیروانی کالر", "cuf": "کف آستین",
        "kur_slv": "کرتہ آستین", "round": "گول دامن", "square": "چکور دامن",
        "fit": "فٹنگ (Fitting)", "double": "ڈبل سلائی", "gum": "گم سلائی",
        "remind": "پیمنٹ ریمائنڈر", "delete": "حذف کریں", "status": "حالت"
    }
    
    english = {
        "title": "Tailor Master Pro", "login": "Login", "register": "Create Free Account",
        "forgot": "Forgot Password?", "email": "Email Address", "pass": "Password",
        "shop": "Shop Name", "phone": "Mobile Number", "s_q": "Security Question", "s_a": "Answer",
        "dash": "Dashboard", "new_order": "New Order", "reports": "Reports", "security": "Security",
        "cust_name": "Customer Name", "total": "Total Bill", "advance": "Advance",
        "rem": "Remaining", "pay_mode": "Payment Mode", "del_date": "Delivery Date",
        "meas": "Measurements", "styles": "Styles & Design", "save": "Save Order",
        "verbal": "Verbal Instructions", "extra": "Extra Requirement",
        # Measurements Labels
        "len": "Length", "slv": "Sleeves", "shl": "Shoulder", "col": "Collar",
        "chst": "Chest", "l_chst": "Lower Chest", "wst": "Waist", "hip": "Hip",
        "shl_len": "Shalwar Length", "shl_bot": "Bottom (Pancha)",
        "paj_len": "Pajama Length", "paj_wst": "Pajama Waist",
        "paj_hip": "Pajama Hip", "paj_thi": "Thigh", "paj_bot": "Pajama Bottom",
        "fly": "Fly", "shirt_len": "Shirt Length",
        # Style Labels
        "sh_col": "Shirt Collar", "sw_col": "Sherwani Collar", "cuf": "Cuff Sleeve",
        "kur_slv": "Kurta Sleeve", "round": "Round Ghera", "square": "Square Ghera",
        "fit": "Fitting", "double": "Double Stitch", "gum": "Gum Silai",
        "remind": "Send Reminder", "delete": "Delete Shop", "status": "Status"
    }
    return urdu if lang == "Urdu" else english
