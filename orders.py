import streamlit as st
from datetime import date
import json
from database import get_connection

def add_order_ui(user_id):
    st.markdown("### 📏 AZAD TAILOR - Measurement Form")
    
    with st.form("complete_order_form", clear_on_submit=True):
        # Section 1: Client & Order Info
        col_a, col_b, col_c = st.columns(3)
        order_no = col_a.text_input("Order No.", placeholder="e.g. 1793")
        name = col_b.text_input("Client Name")
        phone = col_c.text_input("WhatsApp Number")

        st.divider()

        # Section 2: Numerical Measurements (Left Side of Slip)
        st.subheader("📐 Measurements (Inches)")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        # Shirt / Kameez Measurements
        length = m_col1.text_input("Length")
        sleeves = m_col2.text_input("Sleeves")
        shoulder = m_col3.text_input("Shoulder")
        collar_size = m_col4.text_input("Collar")
        
        chest = m_col1.text_input("Chest")
        l_chest = m_col2.text_input("Lower Chest")
        waist = m_col3.text_input("Waist")
        hip = m_col4.text_input("Hip")
        
        # Bottom Measurements
        s_length = m_col1.text_input("Shalwar Length")
        bottom = m_col2.text_input("Bottom (Pancha)")
        p_length = m_col3.text_input("Pajama Length")
        p_waist = m_col4.text_input("Pajama Waist")
        
        p_hip = m_col1.text_input("Pajama Hip")
        thigh = m_col2.text_input("Thigh")
        p_bottom = m_col3.text_input("Pajama Bottom")
        fly = m_col4.text_input("Fly (Asan)")
        
        shirt_length = st.text_input("Front Shirt Length")

        st.divider()

        # Section 3: Design & Style Options (Right Side of Slip)
        st.subheader("✂️ Style & Design Options")
        
        d1, d2, d3, d4 = st.columns(4)
        
        # Collar & Neck
        with d1:
            st.write("**Collar/Neck**")
            shirt_collar = st.checkbox("Shirt Collar")
            sherwani_collar = st.checkbox("Sherwani Collar")
            sada_neck = st.checkbox("Sada (Simple)")

        # Sleeves & Daman
        with d2:
            st.write("**Sleeves & Daman**")
            cuff_sleeves = st.checkbox("Cuff Sleeves")
            kurta_sleeves = st.checkbox("Kurta Sleeves")
            gol_daman = st.checkbox("Gol Daman")
            chakor_daman = st.checkbox("Chakor Daman")

        # Pockets
        with d3:
            st.write("**Pockets**")
            side_pocket = st.checkbox("Side Pocket")
            side_pocket_qty = st.number_input("Qty", min_value=0, max_value=2, step=1, key="side_qty")
            front_pocket = st.checkbox("Front Pocket")
            shalwar_pocket = st.checkbox("Shalwar Pocket")
            pajama_pocket = st.checkbox("Pajama Pocket")

        # Fitting & Stitching
        with d4:
            st.write("**Fitting & Silai**")
            shalwar_ghera = st.checkbox("Shalwar Ghera")
            loose_fit = st.checkbox("Loose Fit")
            normal_fit = st.checkbox("Normal Fit")
            smart_fit = st.checkbox("Smart Fit")
            gum_silai = st.checkbox("Gum Silai")
            double_silai = st.checkbox("Double Silai")

        st.divider()

        # Section 4: Payment & Notes
        st.subheader("💰 Bill & Delivery")
        v1, v2, v3 = st.columns(3)
        total = v1.number_input("Total Bill", min_value=0)
        adv = v2.number_input("Advance Payment", min_value=0)
        del_date = v3.date_input("Delivery Date")
        
        verbal_summary = st.text_area("🗣️ Special Instructions / Sketch Details", 
                                     placeholder="E.g. '17-6-1/4 swa' ya koi aur makhsoos nishani...")

        # Form Submit Logic
        if st.form_submit_button("✅ Save Complete Order"):
            if name and order_no:
                # Sab data ko ek dictionary mein jama karna
                measurements = {
                    "Length": length, "Sleeves": sleeves, "Shoulder": shoulder, "Collar": collar_size,
                    "Chest": chest, "Lower Chest": l_chest, "Waist": waist, "Hip": hip,
                    "Shalwar Length": s_length, "Bottom": bottom, "Pajama Length": p_length,
                    "Pajama Waist": p_waist, "Pajama Hip": p_hip, "Thigh": thigh,
                    "Pajama Bottom": p_bottom, "Fly": fly, "Shirt Length": shirt_length
                }
                
                styles = {
                    "Shirt Collar": shirt_collar, "Sherwani Collar": sherwani_collar, "Sada Neck": sada_neck,
                    "Cuff Sleeves": cuff_sleeves, "Kurta Sleeves": kurta_sleeves, 
                    "Gol Daman": gol_daman, "Chakor Daman": chakor_daman,
                    "Side Pocket": side_pocket, "Side Qty": side_pocket_qty,
                    "Front Pocket": front_pocket, "Shalwar Pocket": shalwar_pocket, 
                    "Pajama Pocket": pajama_pocket, "Shalwar Ghera": shalwar_ghera,
                    "Loose Fit": loose_fit, "Normal Fit": normal_fit, "Smart Fit": smart_fit,
                    "Gum Silai": gum_silai, "Double Silai": double_silai
                }
                
                full_data = json.dumps({"measurements": measurements, "styles": styles})
                remaining = total - adv

                try:
                    conn = get_connection()
                    query = """INSERT INTO clients 
                               (user_id, name, phone, order_no, total, advance, remaining, status, 
                                order_date, delivery_date, m_data, verbal_notes) 
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"""
                    
                    conn.execute(query, (user_id, name, phone, order_no, total, adv, remaining, 
                                         'Pending', date.today(), del_date, full_data, verbal_summary))
                    conn.commit()
                    st.success(f"Order #{order_no} for {name} has been saved!")
                except Exception as e:
                    st.error(f"Error saving to database: {e}")
            else:
                st.error("Please enter at least Order Number and Client Name!")
