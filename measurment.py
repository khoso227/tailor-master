import streamlit as st
from datetime import date
import json
from database import get_connection, add_client

def show_order_form(conn, ln=None):
    st.markdown("### 📏 AZAD TAILOR - Complete Measurement Form")
    
    user_id = st.session_state.get('user_id', 1)
    
    # Quick add existing customer option
    with st.expander("⚡ Quick Add - Existing Customer", expanded=False):
        search_term = st.text_input("Search customer by name or phone")
        
        if search_term:
            from database import quick_search_customers
            customers = quick_search_customers(search_term, user_id)
            
            if customers:
                selected_option = st.selectbox(
                    "Select Customer",
                    options=[f"{c['name']} ({c['phone']})" + (f" - {c.get('email', '')}" if c.get('email') else "") for c in customers],
                    key="quick_customer_select"
                )
                
                if selected_option:
                    # Pre-fill form with customer details
                    selected_customer = [c for c in customers 
                                       if f"{c['name']} ({c['phone']})" + (f" - {c.get('email', '')}" if c.get('email') else "") == selected_option][0]
                    
                    # Auto-fill customer details
                    client_name = selected_customer['name']
                    phone_number = selected_customer['phone']
                    
                    if st.button("Use This Customer"):
                        st.session_state.prefilled_customer = {
                            'name': client_name,
                            'phone': phone_number,
                            'email': selected_customer.get('email', ''),
                            'address': selected_customer.get('address', '')
                        }
                        st.rerun()
            else:
                st.info("No customers found")
    
    # Check for pre-filled customer data
    prefilled = st.session_state.get('prefilled_customer', {})
    
    with st.form("complete_order_form", clear_on_submit=True):
        # --- SECTION 1: SLIP HEADER ---
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        
        with col_h1:
            order_no = st.text_input("Order No.*", placeholder="e.g. 1793", 
                                    value=f"ORD{date.today().strftime('%Y%m%d')}")
        
        with col_h2:
            booking_date = st.date_input("B/Date (Booking Date)*", value=date.today())
        
        with col_h3:
            delivery_date = st.date_input("D/Date (Delivery Date)*", 
                                         value=date.today())
        
        with col_h4:
            total_suits = st.number_input("No. of Suits*", min_value=1, step=1, value=1)

        col_u1, col_u2 = st.columns(2)
        client_name = col_u1.text_input("Client Name*", value=prefilled.get('name', ''))
        phone_number = col_u2.text_input("WhatsApp Number*", value=prefilled.get('phone', ''))

        # Address field
        address = st.text_area("Address", value=prefilled.get('address', ''))
        
        st.divider()

        # --- SECTION 2: MEASUREMENTS (Inches) ---
        st.subheader("📐 Measurements (Inches)")
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            length = st.text_input("Length", placeholder="e.g. 42 1/2")
            chest = st.text_input("Chest")
            s_length = st.text_input("Shalwar Length", placeholder="40")
            p_hip = st.text_input("Hip (Pajama)")
            shirt_len = st.text_input("Front Shirt Length")

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
            p_waist = st.text_input("Waist (Pajama)")
            fly = st.text_input("Fly (Asan)")

        st.divider()

        # --- SECTION 3: STYLE & DESIGN OPTIONS ---
        st.subheader("✂️ Style & Design Options")
        s1, s2, s3, s4 = st.columns(4)

        with s1:
            st.write("**Neck**")
            shirt_collar = st.checkbox("Shirt Collar")
            sherwani_collar = st.checkbox("Sherwani Collar")
            sada = st.checkbox("Sada")
            design = st.checkbox("Design")
            design_no = st.text_input("Design Number", placeholder="e.g. D123")

        with s2:
            st.write("**Sleeves/Daman**")
            cuff_sleeves = st.checkbox("Cuff Aasteen")
            kurta_sleeves = st.checkbox("Kurta Aasteen")
            gol_daman = st.checkbox("Gol Daman")
            chakor_daman = st.checkbox("Chakor Daman")
            shalwar_ghera = st.checkbox("Shalwar Ghera")

        with s3:
            st.write("**Pockets**")
            side_pocket = st.checkbox("Side Pocket")
            front_pocket = st.checkbox("Front Pocket")
            shalwar_pocket = st.checkbox("Shalwar Pocket")
            pajama_pocket = st.checkbox("Pajama Pocket")
            losing = st.checkbox("Losing (Extra Loose)")

        with s4:
            st.write("**Fitting/Silai**")
            smart_fit = st.checkbox("Smart Fit")
            normal_fit = st.checkbox("Normal Fit")
            gum_silai = st.checkbox("Gum Silai")
            double_silai = st.checkbox("Double Silai")
            st.write("")
            side_pocket_qty = st.number_input("Side Pocket Qty", 0, 2, 0)

        st.divider()

        # --- SECTION 4: BILL & NOTES ---
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            total_bill = st.number_input("Total Bill*", min_value=0, step=10, value=0)
        
        with col_p2:
            advance_paid = st.number_input("Advance Payment", min_value=0, step=10, value=0)
        
        with col_p3:
            balance_due = total_bill - advance_paid
            st.metric("Balance Due", f"₹{balance_due}")

        verbal_notes = st.text_area("🗣️ Verbal Summary / Special Notes", 
                                     placeholder="E.g. 17-6-1/4 swa, ya koi aur makhsoos nishani...")

        # Urgent order option
        urgent_order = st.checkbox("🚨 Mark as Urgent Order")

        # --- SECTION 5: SUBMIT BUTTON ---
        submitted = st.form_submit_button("✅ SAVE COMPLETE ORDER")
        
        if submitted:
            if not client_name or not order_no or not phone_number:
                st.error("⚠️ Order Number, Client Name and Phone Number are required!")
            
            elif total_bill <= 0:
                st.error("❌ Total Bill must be greater than 0")
            
            else:
                # First, add or get client
                client_id = add_client(
                    name=client_name, 
                    phone=phone_number, 
                    email=prefilled.get('email', ''), 
                    address=address,
                    notes="",
                    user_id=user_id
                )
                
                if client_id is None:
                    # Client already exists, get existing client ID
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM clients WHERE phone = ? AND user_id = ?", 
                                     (phone_number, user_id))
                        existing_client = cursor.fetchone()
                        client_id = existing_client[0] if existing_client else None
                    except:
                        client_id = None
                
                if client_id:
                    # Measurements aur Styles ko ek saath JSON mein pack karna
                    m_data_obj = {
                        "num_suits": total_suits,
                        "measurements": {
                            "Length": length, "Sleeves": sleeves, "Shoulder": shoulder, "Collar": collar,
                            "Chest": chest, "Lower Chest": l_chest, "Waist": waist, "Hip": hip,
                            "Shalwar Length": s_length, "Bottom": bottom, "Pajama Length": p_length,
                            "Pajama Waist": p_waist, "Pajama Hip": p_hip, "Thigh": thigh,
                            "Pajama Bottom": p_bottom, "Fly": fly, "Shirt Length": shirt_len
                        },
                        "styles": {
                            "Shirt Collar": shirt_collar, "Sherwani Collar": sherwani_collar, 
                            "Sada": sada, "Design": design, "Design No": design_no,
                            "Cuff Sleeves": cuff_sleeves, "Kurta Sleeves": kurta_sleeves,
                            "Gol Daman": gol_daman, "Chakor Daman": chakor_daman,
                            "Side Pocket": side_pocket, "Side Pocket Qty": side_pocket_qty,
                            "Front Pocket": front_pocket, "Shalwar Pocket": shalwar_pocket,
                            "Pajama Pocket": pajama_pocket, "Shalwar Ghera": shalwar_ghera,
                            "Losing": losing, "Normal Fit": normal_fit, "Smart Fit": smart_fit,
                            "Gum Silai": gum_silai, "Double Silai": double_silai
                        }
                    }
                    
                    m_data_json = json.dumps(m_data_obj)

                    try:
                        cursor = conn.cursor()
                        
                        # Check which database structure we have
                        cursor.execute("PRAGMA table_info(orders)")
                        columns = [col[1] for col in cursor.fetchall()]
                        
                        if 'client_id' in columns:
                            # New database structure
                            cursor.execute("""
                                INSERT INTO orders (
                                    user_id, client_id, client_name, client_phone, 
                                    order_date, delivery_date, status, suits, 
                                    order_no, total_bill, advance, balance, 
                                    measurement_data, notes, address, is_synced
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                user_id, client_id, client_name, phone_number,
                                booking_date.strftime("%Y-%m-%d"),
                                delivery_date.strftime("%Y-%m-%d"),
                                'Urgent' if urgent_order else 'Pending',
                                total_suits,
                                order_no,
                                total_bill,
                                advance_paid,
                                balance_due,
                                m_data_json,
                                verbal_notes,
                                address,
                                0  # is_synced
                            ))
                            
                            order_id = cursor.lastrowid
                            
                            # If advance paid, add to payments table
                            if advance_paid > 0:
                                cursor.execute("""
                                    INSERT INTO payments (order_id, amount, payment_date, payment_method, notes)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (
                                    order_id,
                                    advance_paid,
                                    booking_date.strftime("%Y-%m-%d"),
                                    "Cash",
                                    f"Advance payment for order #{order_no}"
                                ))
                        
                        else:
                            # Old database structure (for backward compatibility)
                            cursor.execute("""
                                INSERT INTO orders 
                                (user_id, client_name, client_phone, total_bill, paid_amount, balance, 
                                 order_date, status, measurement_data, notes, order_no, is_synced) 
                                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                            """, (
                                user_id, client_name, phone_number, 
                                total_bill, advance_paid, balance_due, 
                                booking_date.strftime("%Y-%m-%d"), 
                                'Urgent' if urgent_order else 'Pending', 
                                m_data_json, verbal_notes, order_no, 0
                            ))
                        
                        conn.commit()
                        
                        st.success(f"🎉 Order #{order_no} for {client_name} ({total_suits} Suits) saved successfully!")
                        st.balloons()
                        
                        # Clear pre-filled data
                        if 'prefilled_customer' in st.session_state:
                            del st.session_state.prefilled_customer
                        
                        # Show next steps
                        with st.expander("📋 Next Steps & Actions", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("📄 View This Order"):
                                    st.session_state.current_order_id = order_id if 'order_id' in locals() else None
                                    st.rerun()
                            
                            with col2:
                                if st.button("➕ Add Another Order"):
                                    st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Database Error: {e}")
                        st.info("💡 Tip: Please check database structure or contact support.")
                
                else:
                    st.error("❌ Could not create or find client record")

# Alternative function name for compatibility
def add_order_ui(user_id=None):
    conn = get_connection()
    show_order_form(conn)
    conn.close()
