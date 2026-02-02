import streamlit as st
from datetime import datetime

def show_order_form(conn, ln):
    st.header(ln['order'])
    with st.form("measurement_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input(ln['c_name'])
        phone = c2.text_input(ln['c_phone'])
        
        st.subheader(ln['measure'])
        m1, m2, m3, m4 = st.columns(4)
        length = m1.text_input(ln['len'])
        shoulder = m2.text_input(ln['sh'])
        chest = m3.text_input(ln['ch'])
        waist = m4.text_input(ln['ws'])
        
        m5, m6, m7, m8 = st.columns(4)
        sleeves = m5.text_input(ln['sl'])
        neck = m6.text_input(ln['nk'])
        bottom = m7.text_input(ln['bt'])
        
        st.markdown("---")
        p1, p2, p3 = st.columns(3)
        p_method = p1.selectbox(ln['pay'], ["Cash", "EasyPaisa", "JazzCash", "Bank Transfer"])
        bill = p2.number_input(ln['bill'], min_value=0.0)
        adv = p3.number_input(ln['advance'], min_value=0.0)
        
        if st.form_submit_button(ln['save']):
            if name and phone:
                conn.execute("""INSERT INTO orders (user_id, client_name, client_phone, length, shoulder, chest, waist, sleeves, neck, bottom, payment_method, total_bill, paid_amount, order_date) 
                             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                             (st.session_state.u_id, name, phone, length, shoulder, chest, waist, sleeves, neck, bottom, p_method, bill, adv, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                st.success("Order Saved Successfully!")
            else: st.warning("Please fill Name and Phone!")
