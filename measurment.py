import streamlit as st
from datetime import date
import json

def show_order_form(conn, ln):
    # Header Title
    st.markdown("### 📏 AZAD TAILOR - New Order Form")
    
    # Form Shuru
    with st.form("complete_order_form", clear_on_submit=True):
        
        # --- SECTION 1: HEADER INFO ---
        col_h1, col_h2, col_h3 = st.columns(3)
        order_no = col_h1.text_input("Order No.", placeholder="e.g. 1793")
        # ln.get use kiya hai taake agar key missing ho to error na aaye
        client_name = col_h2.text_input("Client Name")
        phone_number = col_h3.text_input("WhatsApp Number")

        st.divider()

        # --- SECTION 2: MEASUREMENTS (Inches) ---
        st.subheader("📐 Measurements (Inches)")
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            length = st.text_input("Length", placeholder="42 1/2")
            chest = st.text_input("Chest")
            s_length = st.text_input("Shalwar Length", placeholder="40")
            p_hip = st.text_input("Pajama Hip")
            shirt_len = st.text_input("Shirt Length")

        with m2:
            sleeves = st.text_input("Sleeves", placeholder="25 1/2")
            l_chest = st.text_input("Lower Chest", placeholder="48")
            bottom = st.text_input("Bottom (Pancha)", placeholder="20")
            thigh = st.text_input("Thigh (Raan)")

        with m3:
            shoulder = st.text_input("Shoulder", placeholder="20 1/2")
            waist = st.text_input("Waist")
            p_length = st.text_input("Pajama Length")
            p_bottom = st.text_input("Pajama Bottom")

        with m4:
            collar = st.text_input("Collar", placeholder="17 1/2")
            hip = st.text_input("Hip / Ghera", placeholder="28")
            p_waist = st.text_input("Pajama Waist")
            fly = st.text_input("Fly (Asan)")

        st.divider()

        # --- SECTION 3: STYLE OPTIONS ---
        st.subheader("✂️ Style & Design Options")
        s1, s2, s3, s4 = st.columns(4)

        with s1:
            st.write("**Neck**")
            shirt_collar = st.checkbox("Shirt Collar")
            sherwani_collar = st.checkbox("Sherwani Collar")
            sada_neck = st.checkbox("Sada Neck")

        with s2:
            st.write("**Sleeves/Daman**")
            cuff_sleeves = st.checkbox("Cuff Aasteen")
            kurta_sleeves = st.checkbox("Kurta Aasteen")
            gol_daman = st.checkbox("Gol Daman")
            chakor_daman = st.checkbox("Chakor Daman")

        with s3:
            st.write("**Pockets**")
            side_pocket = st.checkbox("Side Pocket")
            front_pocket = st.checkbox("Front Pocket")
            shalwar_pocket = st.checkbox("Shalwar Pocket")
            pajama_pocket = st.checkbox("Pajama Pocket")

        with s4:
            st.write("**Fitting/Silai**")
            smart_fit = st.checkbox("Smart Fit")
            normal_fit = st.checkbox("Normal Fit")
            gum_silai = st.checkbox("Gum Silai")
            double_silai = st.checkbox("Double Silai")

        st.divider()

        # --- SECTION 4: BILL & NOTES ---
        b1, b2 = st.columns(2)
        total = b1.number_input("Total Bill", min_value=0)
        advance = b2.number_input("Advance Payment", min_value=0)
        
        verbal_notes = st.text_area("🗣️ Verbal Summary / Special Notes", placeholder="e.g. Collar loose rakhna...")

        # --- SUBMIT BUTTON (ZAROORI) ---
        submit_button = st.form_submit_button("✅ SAVE COMPLETE ORDER")

        if submit_button:
            if client_name and order_no:
                # Sara data JSON mein save karne ke liye
                full_m_data = json.dumps({
                    "measurements": {
                        "Length": length, "Sleeves": sleeves, "Shoulder": shoulder, "Collar": collar,
                        "Chest": chest, "Lower Chest": l_chest, "Waist": waist, "Hip": hip,
                        "Shalwar Length": s_length, "Bottom": bottom, "Pajama Length": p_length,
                        "Pajama Waist": p_waist, "Pajama Hip": p_hip, "Thigh": thigh,
                        "Pajama Bottom": p_bottom, "Fly": fly, "Shirt Length": shirt_len
                    },
                    "styles": {
                        "Shirt Collar": shirt_collar, "Sherwani Collar": sherwani_collar,
                        "Cuff": cuff_sleeves, "Kurta": kurta_sleeves, "Gol": gol_daman,
                        "Side Pocket": side_pocket, "Front Pocket": front_pocket,
                        "Smart Fit": smart_fit, "Gum Silai": gum_silai
                    }
                })

                try:
                    cur = conn.cursor()
                    # Query for your database
                    query = """INSERT INTO orders 
                               (user_id, client_name, client_phone, total_bill, paid_amount, balance, 
                                order_date, status, measurement_data, notes, order_no) 
                               VALUES (?,?,?,?,?,?,?,?,?,?,?)"""
                    
                    cur.execute(query, (
                        st.session_state.u_id, client_name, phone_number, 
                        total, advance, (total - advance), date.today().strftime("%Y-%m-%d"), 
                        "Pending", full_m_data, verbal_notes, order_no
                    ))
                    conn.commit()
                    st.success(f"🎉 Order #{order_no} for {client_name} saved!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Database Error: {e}")
            else:
                st.warning("⚠️ Please fill Client Name and Order Number!")
