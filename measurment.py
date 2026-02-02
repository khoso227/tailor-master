import streamlit as st
from datetime import datetime

def show_order_form(conn, ln):
    st.header(ln['order'])
    with st.form("measurement_form"):
        c1, c2 = st.columns(2)
        name, phone = c1.text_input(ln['c_name']), c2.text_input(ln['c_phone'])
        
        st.subheader(ln['measure'])
        m1, m2, m3, m4 = st.columns(4)
        length, shoulder, chest, waist = m1.text_input(ln['len']), m2.text_input(ln['sh']), m3.text_input(ln['ch']), m4.text_input(ln['ws'])
        m5, m6, m7, m8 = st.columns(4)
        sleeves, neck, bottom, thigh = m5.text_input(ln['sl']), m6.text_input(ln['nk']), m7.text_input(ln['bt']), m8.text_input(ln['thi'])
        
        st.subheader(ln['style'])
        s1, s2, s3 = st.columns(3)
        col_style = s1.selectbox("Collar", ["Shirt Collar", "Sherwani Ban", "Gola Neck"])
        slv_style = s2.selectbox("Sleeve", ["Cuff آستین", "Kurta آستین"])
        ghera_style = s3.selectbox("Ghera", ["Round گول", "Square چکور"])

        st.markdown("---")
        p1, p2, p3 = st.columns(3)
        p_method = p1.selectbox(ln['pay'], ["Cash", "EasyPaisa", "JazzCash"])
        bill, adv = p2.number_input(ln['bill']), p3.number_input(ln['adv'])
        
        if st.form_submit_button(ln['save']):
            if name and phone:
                conn.execute("""INSERT INTO orders (user_id, client_name, client_phone, length, shoulder, chest, waist, sleeves, neck, bottom, thigh, style_collar, style_sleeve, style_ghera, payment_method, total_bill, paid_amount, order_date) 
                             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                             (st.session_state.u_id, name, phone, length, shoulder, chest, waist, sleeves, neck, bottom, thigh, col_style, slv_style, ghera_style, p_method, bill, adv, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                st.success("Order Saved! ✅")
            else: st.warning("Please fill essential data!")
