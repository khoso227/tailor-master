import streamlit as st
from datetime import date
import json

def show_order_form(conn, ln):
    st.markdown(f"## {ln['order']} ➕")
    
    with st.form("complete_order_form", clear_on_submit=True):
        # --- SECTION 1: Header Info ---
        c1, c2, c3 = st.columns(3)
        order_no = c1.text_input("Slip / Order No.", placeholder="e.g. 1793")
        client_name = c2.text_input(ln['client_name'])
        phone_number = c3.text_input(ln['phone'])

        st.divider()

        # --- SECTION 2: MEASUREMENTS (Inches) ---
        st.subheader("📏 Measurements (Inches)")
        
        # Grid Layout (4 columns like the slip)
        m1, m2, m3, m4 = st.columns(4)
        
        # Row 1
        length = m1.text_input("Length", placeholder="e.g. 42 1/2")
        sleeves = m2.text_input("Sleeves", placeholder="25 1/2")
        shoulder = m3.text_input("Shoulder", placeholder="20 1/2")
        collar = m4.text_input("Collar", placeholder="17 1/2")
        
        # Row 2
        chest = m1.text_input("Chest")
        l_chest = m2.text_input("Lower Chest (Fit)", placeholder="e.g. 48")
        waist = m3.text_input("Waist")
        hip = m4.text_input("Hip / Ghera", placeholder="28")
        
        # Row 3 (Shalwar / Pajama)
        s_length = m1.text_input("Shalwar Length", placeholder="40")
        bottom = m2.text_input("Bottom (Pancha)", placeholder="20")
        p_length = m3.text_input("Pajama Length")
        p_waist = m4.text_input("Pajama Waist")
        
        # Row 4 (Extra Pajama details)
        p_hip = m1.text_input("Pajama Hip")
        thigh = m2.text_input("Thigh (Raan)")
        p_bottom = m3.text_input("Pajama Bottom")
        fly = m4.text_input("Fly (Asan)")
        
        shirt_len = st.text_input("Front Shirt Length")

        st.divider()

        # --- SECTION 3: STYLE OPTIONS ---
        st.subheader("✂️ Style & Design Options")
        s1, s2, s3, s4 = st.columns(4)

        with s1:
            st.write("**Collar & Neck**")
            shirt_collar = st.checkbox("Shirt Collar")
            sherwani_collar = st.checkbox("Sherwani Collar")
            sada_neck = st.checkbox("Sada (Simple)")

        with s2:
            st.write("**Sleeves & Daman**")
            cuff_sleeves = st.checkbox("Cuff Aasteen")
            kurta_sleeves = st.checkbox("Kurta Aasteen")
            gol_daman = st.checkbox("Gol Daman")
            chakor_daman = st.checkbox("Chakor Daman")

        with s3:
            st.write("**Pockets**")
            side_pocket = st.checkbox("Side Pocket")
            side_qty = st.number_input("Qty", 0, 2, 0, key="side_p_qty")
            front_pocket = st.checkbox("Front Pocket")
            shalwar_pocket = st.checkbox("Shalwar Pocket")
            pajama_pocket = st.checkbox("Pajama Pocket")

        with s4:
            st.write("**Fitting & Silai**")
            shalwar_ghera = st.checkbox("Shalwar Ghera")
            smart_fit = st.checkbox("Smart Fit")
            losing = st.checkbox("Losing")
            gum_silai = st.checkbox("Gum Silai")
            double_silai = st.checkbox("Double Silai")

        design_details = st.text_input("Design Name / Number / Details")

        st.divider()

        # --- SECTION 4: BILL CALCULATOR ---
        st.subheader("💰 Bill Calculator")
        b1, b2, b3 = st.columns(3)
        total = b1.number_input("Total Bill", min_value=0, step=10)
        advance = b2.number_input("Advance Paid", min_value=0, step=10)
        
        balance = total - advance
        b3.markdown(f"### Balance Due: \n # Rs. {balance}")

        verbal_notes = st.text_area("🗣️ Special Verbal Instructions", placeholder="e.g. 17-6-1/4 swa...")

        # --- SUBMIT BUTTON ---
        if st.form_submit_button("Save Order ✅"):
            if client_name and order_no:
                # Measurements and Styles ko JSON mein convert karna
                m_data = json.dumps({
                    "measurements": {
                        "Length": length, "Sleeves": sleeves, "Shoulder": shoulder, "Collar": collar,
                        "Chest": chest, "Lower Chest": l_chest, "Waist": waist, "Hip": hip,
                        "Shalwar Length": s_length, "Bottom": bottom, "Pajama Length": p_length,
                        "Pajama Waist": p_waist, "Pajama Hip": p_hip, "Thigh": thigh,
                        "Pajama Bottom": p_bottom, "Fly": fly, "Shirt Length": shirt_len
                    },
                    "styles": {
                        "Shirt Collar": shirt_collar, "Sherwani Collar": sherwani_collar, "Sada": sada_neck,
                        "Cuff": cuff_sleeves, "Kurta": kurta_sleeves, "Gol Daman": gol_daman, 
                        "Chakor": chakor_daman, "Side Pocket": side_pocket, "Side Qty": side_qty,
                        "Front Pocket": front_pocket, "Shalwar Pocket": shalwar_pocket, 
                        "Pajama Pocket": pajama_pocket, "Smart Fit": smart_fit, "Gum Silai": gum_silai
                    }
                })

                try:
                    cur = conn.cursor()
                    # Make sure your 'orders' table has these columns
                    query = """INSERT INTO orders 
                               (user_id, client_name, client_phone, total_bill, paid_amount, balance, 
                                order_date, status, measurement_data, notes, order_no) 
                               VALUES (?,?,?,?,?,?,?,?,?,?,?)"""
                    
                    cur.execute(query, (
                        st.session_state.u_id, client_name, phone_number, 
                        total, advance, balance, date.today().strftime("%Y-%m-%d"), 
                        "Pending", m_data, verbal_notes, order_no
                    ))
                    conn.commit()
                    st.success(f"Order #{order_no} saved successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.warning("Please enter Client Name and Order Number!")
