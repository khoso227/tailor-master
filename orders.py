import streamlit as st
import json
from datetime import date
from database import get_connection

def add_order_ui(user_id):
    st.markdown("### 📝 New Order: Customer Requirements")
    
    with st.form("professional_order_form"):
        # Top Header: Basic Info
        c1, c2, c3, c4 = st.columns(4)
        name = c1.text_input("Customer Name")
        phone = c2.text_input("Mobile No")
        total = c3.number_input("Total Bill", min_value=0)
        adv = c4.number_input("Advance", min_value=0)

        st.markdown("---")
        
        # MAIN LAYOUT: Measurements (Left) vs Styles (Right)
        col_m, col_s = st.columns([1.2, 1])

        with col_m:
            st.markdown("#### 📏 Measurements (Paimayish)")
            m1, m2 = st.columns(2)
            # Shirt/Top
            len_s = m1.text_input("Length (Lambai)")
            slv = m2.text_input("Sleeves (Aastin)")
            shl = m1.text_input("Shoulder (Teera)")
            col = m2.text_input("Collar (Gala)")
            chst = m1.text_input("Chest")
            l_chst = m2.text_input("Lower Chest (Ghera)")
            wst = m1.text_input("Waist (Kamar)")
            hip = m2.text_input("Hip")
            # Bottoms
            st.write("**Bottoms (Shalwar/Pajama)**")
            shl_len = m1.text_input("Shalwar Length")
            shl_bot = m2.text_input("Bottom (Pancha)")
            paj_len = m1.text_input("Pajama Length")
            paj_wst = m2.text_input("Waist (Pajama)")
            paj_hip = m1.text_input("Hip (Pajama)")
            paj_thi = m2.text_input("Thigh (Thail)")
            paj_bot = m1.text_input("Bottom (Pajama)")
            fly = m2.text_input("Fly")
            shirt_len = m1.text_input("Shirt Length")

        with col_s:
            st.markdown("#### 🎨 Style & Design")
            # Collars & Sleeves
            s1, s2 = st.columns(2)
            shirt_col = s1.checkbox("Shirt Collar")
            sherwani_col = s2.checkbox("Sherwani Collar")
            cuff_slv = s1.checkbox("Cuff Sleeve")
            kurta_slv = s2.checkbox("Kurta Sleeve")
            
            # Ghera & Pockets
            st.write("**Ghera & Pockets**")
            gol_dam = s1.checkbox("Round Ghera (Gol)")
            chk_dam = s2.checkbox("Square Ghera (Chakor)")
            chst_p = s1.text_input("Chest Pocket (Qty/Type)")
            side_p = s2.text_input("Side Pocket (Qty/Type)")
            paj_p = s1.checkbox("Pajama Pocket")
            shl_p = s2.checkbox("Shalwar Pocket")
            
            # Fitting & Stitching
            st.write("**Fitting & Stitching**")
            fit = st.radio("Fitting Type", ["Normal", "Loose", "Smart"], horizontal=True)
            db_stitch = s1.checkbox("Double Stitching")
            gum_silai = s2.checkbox("Gum Silaai (Hidden)")
            
            # Design Info
            design_name = st.text_input("Design/Pattern Name")
            design_no = st.text_input("Design Number")
            saada = st.checkbox("Plain (Saada)")
            shl_ghera = st.text_input("Shalwar Ghera Details")

        st.markdown("---")
        # Footer: Extra info
        st.markdown("#### 💡 Extra Details")
        f1, f2 = st.columns([1, 2])
        c_field = f1.text_input("Extra Requirement Label", placeholder="e.g. Button Color")
        c_val = f2.text_input("Requirement Value")
        
        verbal = st.text_area("🗒️ Verbal Instructions (Jo client ne zubani bataya)")
        
        c_bot1, c_bot2 = st.columns(2)
        p_mode = c_bot1.selectbox("Payment Mode", ["Cash", "EasyPaisa", "JazzCash", "Bank Transfer"])
        d_date = c_bot2.date_input("Delivery Commitment Date")

        if st.form_submit_button("✅ SAVE COMPLETE ORDER"):
            # Data Formatting
            m_data = {
                "Length": len_s, "Sleeves": slv, "Shoulder": shl, "Collar": col, "Chest": chst,
                "L_Chest": l_chst, "Waist": wst, "Hip": hip, "Shalwar_L": shl_len, "Bottom": shl_bot,
                "Paj_L": paj_len, "Paj_W": paj_wst, "Paj_H": paj_hip, "Thigh": paj_thi, "Paj_B": paj_bot,
                "Fly": fly, "Shirt_L": shirt_len
            }
            s_data = {
                "Collar": "Shirt" if shirt_col else ("Sherwani" if sherwani_col else "Standard"),
                "Sleeve": "Cuff" if cuff_slv else ("Kurta" if kurta_slv else "Standard"),
                "Ghera": "Round" if gol_dam else ("Square" if chk_dam else "Standard"),
                "Chest_P": chst_p, "Side_P": side_p, "Paj_P": paj_p, "Shl_P": shl_p,
                "Fitting": fit, "Double_Stitch": db_stitch, "Gum_Silai": gum_silai,
                "Design": design_name, "Design_No": design_no, "Plain": saada, "Shl_Ghera": shl_ghera
            }
            
            conn = get_connection()
            rem = total - adv
            extra = f"{c_field}: {c_val}" if c_field else ""
            
            conn.execute('''INSERT INTO clients 
                (user_id, name, phone, total, advance, remaining, pay_method, order_date, delivery_date, m_data, s_data, extra_req, verbal_notes) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (user_id, name, phone, total, adv, rem, p_mode, date.today(), d_date, json.dumps(m_data), json.dumps(s_data), extra, verbal))
            conn.commit()
            st.success(f"Order for {name} saved successfully!")
