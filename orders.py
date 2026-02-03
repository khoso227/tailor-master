import streamlit as st
import json
from datetime import date
from database import get_connection

def add_order_ui(user_id):
    st.header("📏 Detailed Measurement Form")
    with st.form("azad_form"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Client Name")
        phone = c2.text_input("WhatsApp Number")
        order_no = c3.text_input("Order No.", placeholder="e.g. 1793")

        st.markdown("---")
        m_col1, m_col2 = st.columns([2, 1])
        
        with m_col1:
            st.subheader("👕 Shirt & Shalwar")
            row1 = st.columns(3)
            l_len = row1[0].text_input("Length")
            l_slv = row1[1].text_input("Sleeves")
            l_shl = row1[2].text_input("Shoulder")
            
            row2 = st.columns(3)
            l_col = row2[0].text_input("Collar")
            l_chst = row2[1].text_input("Chest")
            l_lchst = row2[2].text_input("Lower Chest")
            
            row3 = st.columns(3)
            l_wst = row3[0].text_input("Waist")
            l_hip = row3[1].text_input("Hip / Ghera")
            l_slen = row3[2].text_input("Shalwar Length")
            
            row4 = st.columns(3)
            l_sbot = row4[0].text_input("Shalwar Bottom")
            l_thigh = row4[1].text_input("Thigh")
            l_fly = row4[2].text_input("Fly (Asan)")

        with m_col2:
            st.subheader("🎨 Styles")
            s_col = st.checkbox("Sherwani Collar")
            cuf = st.checkbox("Cuff Sleeves")
            gol = st.checkbox("Gol Daman")
            gum = st.checkbox("Gum Silai")
            fit = st.radio("Fitting", ["Normal", "Loose", "Smart"])
            
            st.divider()
            total = st.number_input("Total Bill", min_value=0)
            adv = st.number_input("Advance", min_value=0)
            pay = st.selectbox("Payment Via", ["Cash", "EasyPaisa", "JazzCash", "Bank Transfer"])
            dd = st.date_input("Delivery Date")

        st.markdown("---")
        verbal = st.text_area("🗣️ Verbal Details", placeholder="Client ne jo zubani baten batayi...")

        if st.form_submit_button("✅ SAVE ORDER"):
            if name and phone:
                conn = get_connection()
                rem = total - adv
                m_data = {"Len": l_len, "Slv": l_slv, "Shl": l_shl, "Col": l_col, "Chst": l_chst, "Wst": l_wst, "Hip": l_hip, "S_Len": l_slen, "Thigh": l_thigh, "Fly": l_fly}
                
                query = "INSERT INTO clients (user_id, name, phone, order_no, total, advance, remaining, pay_method, order_date, delivery_date, m_data, verbal_notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
                conn.execute(query, (user_id, name, phone, order_no, total, adv, rem, pay, str(date.today()), str(dd), json.dumps(m_data), verbal))
                conn.commit()
                st.success("✅ Order Saved!")
            else: st.error("Name and Phone required!")
