import streamlit as st
from datetime import date
import json
from database import get_connection

def add_order_ui(user_id):
    st.markdown("### 📏 AZAD TAILOR - Complete Measurement Form")
    
    with st.form("complete_order_form", clear_on_submit=True):
        # --- SECTION 1: SLIP HEADER ---
        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            order_no = st.text_input("Order No.", placeholder="e.g. 1793")
        with col_h2:
            booking_date = st.date_input("B/Date (Booking Date)", value=date.today())
        with col_h3:
            delivery_date = st.date_input("D/Date (Delivery Date)")

        col_u1, col_u2 = st.columns(2)
        client_name = col_u1.text_input("Client Name")
        phone_number = col_u2.text_input("WhatsApp Number")

        st.divider()

        # --- SECTION 2: MEASUREMENTS (Left Side of Slip) ---
        st.subheader("📐 Measurements (Inches)")
        # Char columns banaye hain taake slip jaisa layout dikhe
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            length = st.text_input("Length", placeholder="e.g. 42 1/2")
            chest = st.text_input("Chest")
            s_length = st.text_input("Shalwar Length", placeholder="40")
            p_hip = st.text_input("Hip (Pajama)")
            shirt_len = st.text_input("Shirt Length")

        with m2:
            sleeves = st.text_input("Sleeves", placeholder="25 1/2")
            l_chest = st.text_input("Lower Chest", placeholder="48")
            bottom = st.text_input("Bottom (Pancha)", placeholder="20")
            thigh = st.text_input("Thigh")

        with m3:
            shoulder = st.text_input("Shoulder", placeholder="20 1/2")
            waist = st.text_input("Waist")
            p_length = st.text_input("Pajama Length")
            p_bottom = st.text_input("Bottom (Pajama)")

        with m4:
            collar = st.text_input("Collar", placeholder="17 1/2")
            hip = st.text_input("Hip", placeholder="28")
            p_waist = st.text_input("Waist (Pajama)")
            fly = st.text_input("Fly (Asan)")

        st.divider()

        # --- SECTION 3: STYLE OPTIONS (Right Side of Slip) ---
        st.subheader("✂️ Style & Design Options")
        s1, s2, s3, s4 = st.columns(4)

        with s1:
            st.write("**Neck & Sleeves**")
            shirt_collar = st.checkbox("Shirt Collar")
            sherwani_collar = st.checkbox("Sherwani Collar")
            cuff_sleeves = st.checkbox("Cuff Aasteen")
            kurta_sleeves = st.checkbox("Kurta Aasteen")

        with s2:
            st.write("**Daman & Pockets**")
            gol_daman = st.checkbox("Gol Daman")
            chakor_daman = st.checkbox("Chakor Daman")
            side_pocket = st.checkbox("Side Pocket")
            side_pocket_qty = st.number_input("Side Pocket Qty", 0, 2, 0)
            front_pocket = st.checkbox("Front Pocket")

        with s3:
            st.write("**Bottom & Fitting**")
            shalwar_pocket = st.checkbox("Shalwar Pocket")
            pajama_pocket = st.checkbox("Pajama Pocket")
            shalwar_ghera = st.checkbox("Shalwar Ghera")
            losing = st.checkbox("Losing (Extra Loose)")
            normal_fit = st.checkbox("Normal Fit")
            smart_fit = st.checkbox("Smart Fit")

        with s4:
            st.write("**Details & Silai**")
            sada = st.checkbox("Sada")
            design = st.checkbox("Design")
            design_no = st.text_input("Design Number")
            gum_silai = st.checkbox("Gum Silai")
            double_silai = st.checkbox("Double Silai")

        st.divider()

        # --- SECTION 4: PAYMENT & NOTES ---
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            total = st.number_input("Total Bill", min_value=0, step=50)
            advance = st.number_input("Advance Payment", min_value=0, step=50)
        with col_p2:
            verbal_notes = st.text_area("🗣️ Verbal Summary / Special Notes", 
                                        placeholder="E.g. 17-6-1/4 swa, ya koi aur makhsoos nishan...")

        # --- SUBMIT LOGIC ---
        if st.form_submit_button("✅ Save Complete Order"):
            if client_name and order_no:
                # Measurements data object
                m_data_obj = {
                    "measurements": {
                        "Length": length, "Sleeves": sleeves, "Shoulder": shoulder, "Collar": collar,
                        "Chest": chest, "Lower Chest": l_chest, "Waist": waist, "Hip": hip,
                        "Shalwar Length": s_length, "Bottom": bottom, "Pajama Length": p_length,
                        "Pajama Waist": p_waist, "Pajama Hip": p_hip, "Thigh": thigh,
                        "Pajama Bottom": p_bottom, "Fly": fly, "Shirt Length": shirt_len
                    },
                    "styles": {
                        "Shirt Collar": shirt_collar, "Sherwani Collar": sherwani_collar,
                        "Cuff Sleeves": cuff_sleeves, "Kurta Sleeves": kurta_sleeves,
                        "Gol Daman": gol_daman, "Chakor Daman": chakor_daman,
                        "Side Pocket": side_pocket, "Side Qty": side_pocket_qty,
                        "Front Pocket": front_pocket, "Shalwar Pocket": shalwar_pocket,
                        "Pajama Pocket": pajama_pocket, "Shalwar Ghera": shalwar_ghera,
                        "Losing": losing, "Normal Fit": normal_fit, "Smart Fit": smart_fit,
                        "Sada": sada, "Design": design, "Design No": design_no,
                        "Gum Silai": gum_silai, "Double Silai": double_silai
                    }
                }
                
                m_data_json = json.dumps(m_data_obj)
                remaining = total - advance

                try:
                    conn = get_connection()
                    query = """INSERT INTO clients 
                               (user_id, name, phone, order_no, total, advance, remaining, status, 
                                order_date, delivery_date, m_data, verbal_notes) 
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"""
                    
                    conn.execute(query, (user_id, client_name, phone_number, order_no, total, advance, remaining, 
                                         'Pending', booking_date, delivery_date, m_data_json, verbal_notes))
                    conn.commit()
                    st.success(f"🎉 Order #{order_no} for {client_name} saved successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please fill Order Number and Client Name!")
