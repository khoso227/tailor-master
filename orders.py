import streamlit as st
from datetime import date
import json
from database import get_connection

def add_order_ui(user_id):
    st.markdown("### 📏 Detailed Measurement Form")
    
    with st.form("complete_order_form", clear_on_submit=True):
        # Section 1: Client Info
        col1, col2, col3 = st.columns(3)
        name = col1.text_input("Client Name")
        phone = col2.text_input("WhatsApp Number")
        order_no = col3.text_input("Slip / Order No.", placeholder="e.g. 1793")

        st.divider()

        # Section 2: Kameez / Shirt Measurements
        st.subheader("👕 Kameez / Shirt")
        c1, c2, c3, c4 = st.columns(4)
        m_kameez = {
            "Length": c1.text_input("Length (K)"),
            "Sleeves": c2.text_input("Sleeves"),
            "Shoulder": c3.text_input("Shoulder"),
            "Collar": c4.text_input("Collar"),
            "Chest": c1.text_input("Chest"),
            "Lower Chest": c2.text_input("Lower Chest"),
            "Waist (K)": c3.text_input("Waist (K)"),
            "Hip (K)": c4.text_input("Hip (K)"),
            "Front Shirt Length": st.text_input("Front Shirt Length (Optional)")
        }

        # Section 3: Shalwar / Pajama Measurements
        st.subheader("👖 Shalwar / Pajama")
        p1, p2, p3, p4 = st.columns(4)
        m_pants = {
            "Shalwar Length": p1.text_input("Shalwar Length"),
            "Shalwar Bottom": p2.text_input("Bottom (Pancha)"),
            "Pajama Length": p3.text_input("Pajama Length"),
            "Pajama Waist": p4.text_input("Pajama Waist"),
            "Pajama Hip": p1.text_input("Pajama Hip"),
            "Thigh": p2.text_input("Thigh"),
            "Fly": p3.text_input("Fly (Asan)"),
            "Pajama Bottom": p4.text_input("Pajama Bottom")
        }

        # Section 4: Styling Options
        st.subheader("✂️ Style & Design Options")
        s1, s2, s3 = st.columns(3)
        style = {
            "Collar Type": s1.radio("Collar", ["Shirt Collar", "Sherwani Collar", "Simple Neck"], horizontal=True),
            "Sleeves Type": s2.radio("Sleeves Style", ["Cuff Sleeves", "Kurta Sleeves"], horizontal=True),
            "Daman": s3.radio("Daman Style", ["Gol Daman", "Chakor Daman"], horizontal=True),
            "Pockets": st.multiselect("Pockets", ["Side Pocket", "Front Pocket", "Pajama Pocket", "Shalwar Pocket"]),
            "Fitting": st.select_slider("Fitting Preference", options=["Loose", "Normal", "Smart", "Tight"]),
            "Stitching Type": st.selectbox("Stitching Type", ["Simple Silai", "Double Silai", "Gum Silai"]),
            "Design Details": st.text_input("Design Name / Number")
        }

        st.divider()

        # Section 5: Payment & Summary
        st.subheader("💰 Payment & Verbal Summary")
        v1, v2 = st.columns(2)
        total = v1.number_input("Total Bill", min_value=0, step=10)
        adv = v2.number_input("Advance Payment", min_value=0, step=10)
        
        verbal_summary = st.text_area("🗣️ Verbal Details / Summary", 
                                     placeholder="E.g. Collar thora loose rakhna, Pocket right side pe ho...")
        
        del_date = st.date_input("Expected Delivery Date", min_value=date.today())

        # Submit Button
        submit = st.form_submit_button("✅ Save Complete Order")
        
        if submit:
            if name and phone:
                try:
                    conn = get_connection()
                    # Data ko JSON string mein convert karna behtar hai
                    full_m_data = json.dumps({**m_kameez, **m_pants, **style})
                    rem = total - adv
                    
                    # Make sure aapki database table mein 'order_no' ka column maujood ho
                    query = """INSERT INTO clients 
                               (user_id, name, phone, order_no, total, advance, remaining, status, 
                                order_date, delivery_date, m_data, verbal_notes) 
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"""
                    
                    conn.execute(query, (
                        user_id, name, phone, order_no, total, adv, rem, 'Pending', 
                        date.today(), del_date, full_m_data, verbal_summary
                    ))
                    conn.commit()
                    st.success(f"🎉 Order #{order_no} for {name} saved successfully!")
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.error("Please fill Client Name and Phone Number!")
