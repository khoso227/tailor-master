import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
from database import get_connection

# Important: user_id is now a required argument
def add_order_ui(labels, user_id):
    st.subheader("📝 New Order Entry")
    
    with st.form("new_order_form"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Customer Name")
        phone = c2.text_input("WhatsApp (e.g. 923...)")
        suits = c3.number_input("Suits Count", 1)

        c1, c2, c3 = st.columns(3)
        total = c1.number_input("Total Bill")
        adv = c2.number_input("Advance Paid")
        del_date = c3.date_input("Delivery Date")

        st.markdown("---")
        st.write("📏 **Measurements**")
        m_cols = st.columns(4)
        m_results = {}
        for i, label in enumerate(labels):
            m_results[label] = m_cols[i % 4].text_input(label)

        staff = st.selectbox("Assign to Master", ["Sahil", "Arman", "Karigar 1"])
        notes = st.text_area("Extra Style Details")

        if st.form_submit_button("Save Order & Notify"):
            if name and phone:
                conn = get_connection()
                rem = total - adv
                m_str = str(m_results)
                
                query = "INSERT INTO clients (user_id, name, phone, suits_count, total, advance, remaining, status, order_date, delivery_date, m_data, staff_assigned, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"
                conn.execute(query, (user_id, name, phone, suits, total, adv, rem, 'Cutting', date.today(), del_date, m_str, staff, notes))
                conn.commit()
                conn.close()
                
                st.success(f"Order for {name} saved!")
                
                msg = f"Salam {name}, your order for {suits} suits is booked at {st.session_state.shop_name}. Delivery on {del_date}. Total: {total}. Regards."
                url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{url}" target="_blank" style="background-color:#238636;color:white;padding:10px;border-radius:5px;text-decoration:none;">💬 Send WhatsApp Notification</a>', unsafe_allow_html=True)
            else:
                st.error("Missing Name or Phone!")
