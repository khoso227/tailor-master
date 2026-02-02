import streamlit as st
import json
from datetime import datetime

def show_order_form(conn, ln):
    st.header(ln['order'])
    if 'custom_rows' not in st.session_state: st.session_state.custom_rows = []

    with st.form("master_order_form"):
        # Client Info
        c1, c2 = st.columns(2)
        name = c1.text_input(ln['c_name'])
        phone = c2.text_input(ln['c_phone'])

        # Measurements
        st.subheader(ln['measure'])
        m1, m2, m3, m4 = st.columns(4)
        length = m1.text_input(ln['len'], placeholder="42 1/2")
        sleeves = m2.text_input(ln['slv'], placeholder="25")
        shoulder = m3.text_input(ln['shl'])
        collar = m4.text_input(ln['col'])
        
        m5, m6, m7, m8 = st.columns(4)
        chest = m5.text_input(ln['chst'])
        hip = m6.text_input(ln['hip'])
        sh_len = m7.text_input(ln['sh_len'])
        bottom = m8.text_input(ln['bot'])

        # Bill Calculator
        st.markdown("---")
        st.subheader("💰 Bill Calculator")
        b1, b2, b3, b4 = st.columns(4)
        suits = b1.number_input(ln['suits'], min_value=1, step=1)
        total_bill = b2.number_input(ln['total'], min_value=0.0)
        paid_amt = b3.number_input(ln['paid'], min_value=0.0)
        balance = total_bill - paid_amt
        b4.metric(ln['bal'], f"Rs. {balance}")

        # Payment Info
        st.subheader("💳 Payment Details")
        p1, p2, p3 = st.columns(3)
        via = p1.selectbox(ln['via'], ["Cash", "JazzCash", "EasyPaisa", "Bank Transfer"])
        acc_no = p2.text_input(ln['acc_no'])
        acc_name = p3.text_input(ln['acc_name'])

        if st.form_submit_button(ln['save']):
            if name and total_bill > 0:
                conn.execute("""INSERT INTO orders 
                    (user_id, client_name, client_phone, length, sleeves, shoulder, collar, lower_chest, hip_ghera, shalwar_length, bottom, total_suits, total_bill, paid_amount, balance, acc_no, acc_name, payment_via, order_date) 
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                    (st.session_state.u_id, name, phone, length, sleeves, shoulder, collar, chest, hip, sh_len, bottom, suits, total_bill, paid_amt, balance, acc_no, acc_name, via, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                st.success("Order & Payment Recorded! ✅")
            else: st.warning("Fill Name and Bill!")

    if st.button(ln['add_field']):
        st.session_state.custom_rows.append("")
        st.rerun()
