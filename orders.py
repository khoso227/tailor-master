import streamlit as st
from datetime import date
import json
from database import get_connection, add_client, quick_search_customers

def add_order_ui(user_id):
    conn = get_connection()
    
    st.markdown("### 📏 AZAD TAILOR - Digital Measurement Form")
    
    # --- 1. QUICK SEARCH SECTION ---
    with st.expander("⚡ Quick Search - Purana Customer", expanded=False):
        search_term = st.text_input("Naam ya Phone likhen...", key="q_search")
        if search_term:
            customers = quick_search_customers(search_term, user_id)
            if customers:
                options = [f"{c['name']} ({c['phone']})" for c in customers]
                selected = st.selectbox("Customer Select Karein", options)
                if st.button("Details Fill Karein"):
                    c_data = [c for c in customers if f"{c['name']} ({c['phone']})" == selected][0]
                    st.session_state.prefill = c_data
                    st.rerun()
            else: st.info("Koi record nahi mila.")

    prefill = st.session_state.get('prefill', {})

    # --- 2. THE MAIN FORM ---
    with st.form("azad_order_form", clear_on_submit=True):
        # Header Info
        h1, h2, h3, h4 = st.columns(4)
        order_no = h1.text_input("Order No*", value=f"ORD-{date.today().strftime('%H%M%S')}")
        b_date = h2.date_input("Booking Date", value=date.today())
        d_date = h3.date_input("Delivery Date", value=date.fromordinal(date.today().toordinal() + 7))
        suits = h4.number_input("No. of Suits*", min_value=1, value=1)

        u1, u2 = st.columns(2)
        c_name = u1.text_input("Customer Name*", value=prefill.get('name', ''))
        c_phone = u2.text_input("WhatsApp Number*", value=prefill.get('phone', ''))
        address = st.text_area("Address", value=prefill.get('address', ''))

        st.divider()
        
        # Measurements
        st.subheader("📐 Measurements (Inches)")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            length = st.text_input("Length"); chest = st.text_input("Chest")
            s_len = st.text_input("Shalwar Len"); shirt_len = st.text_input("Front Shirt Len")
        with m2:
            sleeves = st.text_input("Sleeves"); l_chest = st.text_input("Lower Chest")
            bottom = st.text_input("Bottom (Pancha)"); thigh = st.text_input("Thigh (Raan)")
        with m3:
            shoulder = st.text_input("Shoulder"); waist = st.text_input("Waist")
            p_len = st.text_input("Pajama Len"); p_bot = st.text_input("Pajama Bottom")
        with m4:
            collar = st.text_input("Collar"); hip = st.text_input("Hip / Ghera")
            p_wst = st.text_input("Waist (Pajama)"); fly = st.text_input("Fly (Asan)")

        st.divider()

        # Styles
        st.subheader("✂️ Style Options")
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            shirt_col = st.checkbox("Shirt Collar"); sher_col = st.checkbox("Sherwani Collar")
        with s2:
            cuf = st.checkbox("Cuff Aasteen"); kurta = st.checkbox("Kurta Aasteen")
            gol = st.checkbox("Gol Daman")
        with s3:
            s_pock = st.checkbox("Side Pocket"); f_pock = st.checkbox("Front Pocket")
        with s4:
            fit = st.radio("Fitting", ["Normal", "Smart", "Loose"], horizontal=True)
            gum = st.checkbox("Gum Silai")

        st.divider()

        # Billing
        b1, b2, b3 = st.columns(3)
        total = b1.number_input("Total Bill*", min_value=0)
        adv = b2.number_input("Advance", min_value=0)
        rem = total - adv
        b3.metric("Remaining Balance", f"Rs.{rem}")
        
        notes = st.text_area("🗣️ Verbal Summary / Special Notes")

        if st.form_submit_button("✅ SAVE COMPLETE ORDER"):
            if c_name and c_phone and total > 0:
                # Add/Get Client
                client_id = add_client(c_name, c_phone, "", address, "", user_id)
                if not client_id:
                    client_id = conn.execute("SELECT id FROM clients WHERE phone=?", (c_phone,)).fetchone()[0]
                
                # Prepare Measurement JSON
                m_json = json.dumps({
                    "measurements": {"len": length, "slv": sleeves, "shl": shoulder, "col": collar, "chst": chest, "wst": waist, "hip": hip, "s_len": s_len, "thigh": thigh, "fly": fly},
                    "styles": {"shirt_col": shirt_col, "sher_col": sher_col, "cuff": cuf, "kurta": kurta, "gol": gol, "fitting": fit}
                })

                conn.execute("""INSERT INTO orders (user_id, client_id, client_name, client_phone, order_no, order_date, delivery_date, suits, total_bill, advance, balance, measurement_data, notes, address) 
                             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                             (user_id, client_id, c_name, c_phone, order_no, str(b_date), str(d_date), suits, total, adv, rem, m_json, notes, address))
                conn.commit()
                st.success(f"🎉 Order {order_no} for {c_name} Saved Successfully!")
                st.balloons()
            else:
                st.error("Naam, Phone aur Bill lazmi hai!")

    conn.close()
