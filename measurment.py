import streamlit as st
import json
from datetime import datetime

def show_order_form(conn, ln):
    st.header(ln['order'])
    
    # Init Custom Fields in Session
    if 'custom_rows' not in st.session_state: st.session_state.custom_rows = []

    with st.form("digital_diary_form"):
        # --- CLIENT INFO ---
        c1, c2 = st.columns(2)
        name = c1.text_input(ln['c_name'], placeholder="Client Name")
        phone = c2.text_input(ln['c_phone'], placeholder="03xx-xxxxxxx")

        # --- 1. MEASUREMENTS (4x2 Grid) ---
        st.subheader(f"📏 {ln['measure']}")
        m1, m2, m3, m4 = st.columns(4)
        length = m1.text_input(ln['len'], placeholder="42 1/2")
        sleeves = m2.text_input(ln['slv'], placeholder="25 1/4")
        shoulder = m3.text_input(ln['shl'], placeholder="20")
        collar = m4.text_input(ln['col'], placeholder="17 1/2")
        
        m5, m6, m7, m8 = st.columns(4)
        chest = m5.text_input(ln['chst'], placeholder="46-48")
        hip = m6.text_input(ln['hip'], placeholder="27 1/2")
        sh_len = m7.text_input(ln['sh_len'], placeholder="40")
        bottom = m8.text_input(ln['bot'], placeholder="20")

        # --- 2. DESIGN SELECTION (Left & Right Columns) ---
        st.markdown("---")
        d_col1, d_col2 = st.columns(2)
        
        with d_col1:
            st.subheader(f"⬅️ {ln['design_l']}")
            sh_col = st.checkbox("Shirt Collar (شرٹ کالر)")
            cuff = st.checkbox("Cuff Sleeves (کف آستین)")
            round_d = st.checkbox("Round Daman (گول دامن)")
            c_pock = st.number_input("Chest Pocket (فرنٹ پاکٹ)", 0, 2)
            paj_pock = st.checkbox("Pajama Pocket (پاجامہ پاکٹ)")

        with d_col2:
            st.subheader(f"➡️ {ln['design_r']}")
            sw_col = st.checkbox("Sherwani Collar (شیروانی کالر)")
            kur_slv = st.checkbox("Kurta Sleeves (کرتا آستین)")
            sq_d = st.checkbox("Square Daman (چکور دامن)")
            s_pock = st.number_input("Side Pockets (سائیڈ پاکٹ)", 0, 2)
            shl_pock = st.text_input("Shalwar Pocket", placeholder="Cross / Simple")
            fit_mood = st.radio("Fitting", ["Simple", "Loose Fit", "Smart Fit"], horizontal=True)

        # --- 3. SPECIAL INSTRUCTIONS & VERBAL ---
        st.markdown("---")
        st.subheader("📝 Special Instructions")
        i1, i2 = st.columns(2)
        patti = i1.text_input(ln['patti'], placeholder="17 - 1 1/4")
        pock_size = i2.text_input(ln['pock_dim'], placeholder="6 x 5 1/2")
        verbal = st.text_area(ln['verbal'], placeholder="Any other note...")

        # --- 4. DYNAMIC CUSTOM FIELDS ---
        st.write("---")
        st.subheader("➕ Custom Data (Apne Fields)")
        dynamic_data = {}
        for i in range(len(st.session_state.custom_rows)):
            k_col, v_col = st.columns(2)
            key = k_col.text_input(f"Label {i+1}", key=f"k_{i}")
            val = v_col.text_input(f"Value {i+1}", key=f"v_{i}")
            if key: dynamic_data[key] = val

        # Add row button (bahir form se manage hoga session state ke zariye)
        if st.form_submit_button(ln['save']):
            if name and phone:
                # Convert design to string for DB
                d_left = f"Collar:{sh_col}, Cuff:{cuff}, Round:{round_d}, CPocket:{c_pock}"
                d_right = f"Sherwani:{sw_col}, Kurta:{kur_slv}, SidePock:{s_pock}, Fit:{fit_mood}"
                
                conn.execute("""INSERT INTO orders 
                    (user_id, client_name, client_phone, length, sleeves, shoulder, collar, chest, hip_ghera, shalwar_length, bottom, design_left, design_right, patti_size, pocket_dim, verbal_notes, custom_fields, order_date) 
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                    (st.session_state.u_id, name, phone, length, sleeves, shoulder, collar, chest, hip, sh_len, bottom, d_left, d_right, patti, pock_size, verbal, json.dumps(dynamic_data), datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                st.success("Order Registered in Diary! ✅")
            else: st.error("Client Name and Phone are required!")
import streamlit as st
from datetime import datetime

def show_order_form(conn, ln):
    st.header(ln['order'])
    with st.form("new_order_form"):
        # ... Measurements section ...
        
        st.subheader("💰 Bill Calculator")
        c1, c2, c3, c4 = st.columns(4)
        suits = c1.number_input(ln['suits'], min_value=1, step=1)
        total = c2.number_input(ln['total'], min_value=0.0)
        paid = c3.number_input("Advance Paid", min_value=0.0)
        
        # Calculation logic
        balance = total - paid
        c4.metric(ln['bal'], f"Rs. {balance}")

        st.subheader("💳 Payment Details")
        p1, p2, p3 = st.columns(3)
        via = p1.selectbox(ln['via'], ["Cash", "JazzCash", "EasyPaisa", "Bank Account"])
        acc_no = p2.text_input(ln['acc_no'])
        acc_name = p3.text_input(ln['acc_name'])

        if st.form_submit_button(ln['save']):
            conn.execute("""INSERT INTO orders (user_id, client_name, client_phone, total_suits, total_bill, paid_amount, balance, acc_no, acc_name, payment_via, order_date) 
                         VALUES (?,?,?,?,?,?,?,?,?,?,?)""", 
                         (st.session_state.u_id, "Name", "Phone", suits, total, paid, balance, acc_no, acc_name, via, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.success("Order Saved! ✅")
    # Row add karne ka button form ke bahir taake state update ho sake
    if st.button(ln['add_field']):
        st.session_state.custom_rows.append("")
        st.rerun()

