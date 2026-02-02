import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
from modules.database import get_connection

def add_order_ui(labels):
    st.subheader("➕ New Client Registration")
    with st.form("new_order_form"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Customer Name")
        phone = c2.text_input("Mobile (with 92...)")
        suits = c3.number_input("Number of Suits", 1)

        c1, c2, c3 = st.columns(3)
        total = c1.number_input("Total Amount")
        adv = c2.number_input("Advance Paid")
        del_date = c3.date_input("Delivery Date")

        st.markdown("### 📏 Detailed Measurements")
        m_cols = st.columns(4)
        m_results = {}
        for i, label in enumerate(labels):
            m_results[label] = m_cols[i % 4].text_input(label)

        staff = st.selectbox("Assign to Tailor", ["Master Sahil", "Master Arman", "Worker 1"])
        notes = st.text_area("Design Special Instructions")

        if st.form_submit_button("Save & Send WhatsApp"):
            if name and phone:
                conn = get_connection()
                rem = total - adv
                m_str = str(m_results) # Converting measurements to string for DB
                conn.execute("INSERT INTO clients (name, phone, suits_count, total, advance, remaining, status, order_date, delivery_date, m_data, staff_assigned, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                             (name, phone, suits, total, adv, rem, 'Cutting', date.today(), del_date, m_str, staff, notes))
                conn.commit()
                conn.close()
                st.success("Order Saved Successfully!")
                
                # WhatsApp Logic
                msg = f"Salam {name}, Welcome to our shop! Your order for {suits} suits is booked. Total: {total}, Advance: {adv}. Delivery on {del_date}. - Tailor Master"
                url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">💬 Send Welcome Message</a>', unsafe_allow_html=True)