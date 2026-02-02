import streamlit as st
import json
from datetime import date
from database import get_connection

def add_order_ui(user_id, t):
    st.markdown(f"### 📝 {t['new_order']}")
    
    with st.form("professional_order_form"):
        # Basic Info
        c1, c2, c3, c4 = st.columns(4)
        name = c1.text_input(t['cust_name'])
        phone = c2.text_input(t['phone'])
        total = c3.number_input(t['total'], min_value=0)
        adv = c4.number_input(t['advance'], min_value=0)

        st.markdown("---")
        # Layout: Measurements (Left) vs Styles (Right)
        col_m, col_s = st.columns(2)

        with col_m:
            st.markdown(f"#### 📏 {t['meas']}")
            m1, m2 = st.columns(2)
            l_len = m1.text_input(t['len']); l_slv = m2.text_input(t['slv'])
            l_shl = m1.text_input(t['shl']); l_col = m2.text_input(t['col'])
            l_chst = m1.text_input(t['chst']); l_ghera = m2.text_input(t['l_chst'])
            l_wst = m1.text_input(t['wst']); l_hip = m2.text_input(t['hip'])
            st.write("---")
            l_shl_l = m1.text_input(t['shl_len']); l_shl_b = m2.text_input(t['shl_bot'])
            l_paj_l = m1.text_input(t['paj_len']); l_paj_w = m2.text_input(t['paj_wst'])

        with col_s:
            st.markdown(f"#### 🎨 {t['styles']}")
            s1, s2 = st.columns(2)
            shirt_col = s1.checkbox(t['sh_col']); sher_col = s2.checkbox(t['sw_col'])
            cuf_slv = s1.checkbox(t['cuf']); kur_slv = s2.checkbox(t['kur_slv'])
            gol_dam = s1.checkbox(t['round']); chk_dam = s2.checkbox(t['square'])
            db_st = s1.checkbox(t['double']); gum_st = s2.checkbox(t['gum'])
            fit = st.radio(t['fit'], ["Normal", "Loose", "Smart"], horizontal=True)
            
            st.markdown("---")
            verbal = st.text_area(t['verbal'])
            pay = st.selectbox(t['pay_mode'], ["Cash", "EasyPaisa", "JazzCash", "Bank Transfer"])
            dd = st.date_input(t['del_date'])

        # IMPORTANT: Added Submit Button to fix error
        submit_button = st.form_submit_button(t['save'])

        if submit_button:
            if name and phone:
                conn = get_connection()
                rem = total - adv
                m_data = {"Length": l_len, "Sleeves": l_slv, "Shoulder": l_shl, "Collar": l_col}
                s_data = {"Fitting": fit, "Double_Stitch": db_st, "Gum_Silai": gum_st}
                
                conn.execute('''INSERT INTO clients 
                    (user_id, name, phone, total, advance, remaining, pay_method, order_date, delivery_date, m_data, s_data, verbal_notes, status) 
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (user_id, name, phone, total, adv, rem, pay, date.today(), dd, json.dumps(m_data), json.dumps(s_data), verbal, 'Pending'))
                conn.commit()
                st.success(f"✅ Order for {name} saved!")
            else:
                st.error("Please enter Name and Phone!")
