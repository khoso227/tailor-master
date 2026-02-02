import streamlit as st
from datetime import date
from database import get_connection

def add_order_ui(labels, user_id):
    st.subheader("📝 Place New Order")
    with st.form("new_order"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Client Name")
        phone = col2.text_input("WhatsApp Number")
        
        c1, c2, c3 = st.columns(3)
        total = c1.number_input("Total Bill", min_value=0)
        adv = c2.number_input("Advance Amount", min_value=0)
        pay = c3.selectbox("Payment Mode", ["Cash", "EasyPaisa", "JazzCash", "Bank Transfer"])
        
        st.write("📐 **Measurements**")
        m_cols = st.columns(4)
        m_data = {}
        for i, l in enumerate(labels):
            m_data[l] = m_cols[i%4].text_input(l)

        st.markdown("---")
        # NAYE COLUMNS YAHAN HAIN
        st.write("💡 **Extra Requirements**")
        cx1, cx2 = st.columns([1, 2])
        c_label = cx1.text_input("Custom Field Name", placeholder="e.g. Pocket Style")
        c_val = cx2.text_input("Details", placeholder="e.g. Double pocket with zip")
        
        v_notes = st.text_area("🗒️ Verbal Instructions / Client Special Requirements", 
                               placeholder="Write anything the client told you verbally...")

        del_date = st.date_input("Delivery Commitment Date")

        if st.form_submit_button("Save Order & Print"):
            if name and phone:
                conn = get_connection()
                rem = total - adv
                custom_info = f"{c_label}: {c_val}" if c_label else ""
                
                query = "INSERT INTO clients (user_id, name, phone, suits_count, total, advance, remaining, status, order_date, delivery_date, m_data, pay_method, verbal_notes, custom_field) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                conn.execute(query, (user_id, name, phone, 1, total, adv, rem, 'Cutting', date.today(), del_date, str(m_data), pay, v_notes, custom_info))
                conn.commit()
                st.success("Order Saved! You can see it in Dashboard.")
            else:
                st.error("Name and Phone are required!")
