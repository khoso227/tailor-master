import streamlit as st
from datetime import date
import json
from database import get_connection, add_client

def show_order_form(conn, ln=None):
    st.markdown("### 📏 AZAD TAILOR - Complete Measurement Form")
    
    user_id = st.session_state.get('user_id', 1)
    
    # Quick add existing customer option
    if 'prefilled_customer' not in st.session_state:
        st.session_state.prefilled_customer = {}
    
    with st.expander("⚡ Quick Add - Existing Customer", expanded=False):
        search_term = st.text_input("Search customer by name or phone", key="quick_search")
        
        if search_term:
            try:
                from database import quick_search_customers
                customers = quick_search_customers(search_term, user_id)
                
                if customers:
                    customer_options = [f"{c['name']} ({c['phone']})" + (f" - {c.get('email', '')}" if c.get('email') else "") for c in customers]
                    selected_option = st.selectbox(
                        "Select Customer",
                        options=customer_options,
                        key="quick_customer_select"
                    )
                    
                    if selected_option:
                        # Find selected customer
                        selected_customer = [c for c in customers if f"{c['name']} ({c['phone']})" + (f" - {c.get('email', '')}" if c.get('email') else "") == selected_option][0]
                        
                        # Auto-fill using session state
                        if st.button("Use This Customer", key="use_customer_btn"):
                            st.session_state.prefilled_customer = {
                                'name': selected_customer['name'],
                                'phone': selected_customer['phone'],
                                'email': selected_customer.get('email', ''),
                                'address': selected_customer.get('address', '')
                            }
                            st.rerun()
                else:
                    st.info("No customers found")
            except:
                st.info("Customer search feature coming soon")
    
    # Check for pre-filled customer data
    prefilled = st.session_state.prefilled_customer
    
    # Initialize session state for order success
    if 'order_saved' not in st.session_state:
        st.session_state.order_saved = False
        st.session_state.saved_order_details = {}
    
    # If order was just saved, show success message
    if st.session_state.order_saved:
        show_order_success(st.session_state.saved_order_details)
        return
    
    # Main form
    with st.form("complete_order_form", clear_on_submit=True):
        # --- SECTION 1: SLIP HEADER ---
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        
        with col_h1:
            order_no = st.text_input("Order No.*", placeholder="e.g. 1793", 
                                    value=f"ORD{date.today().strftime('%Y%m%d%H%M')}")
        
        with col_h2:
            booking_date = st.date_input("B/Date (Booking Date)*", value=date.today())
        
        with col_h3:
            # Default delivery date: 7 days from today
            default_delivery = date.today() if ln else date.fromordinal(date.today().toordinal() + 7)
            delivery_date = st.date_input("D/Date (Delivery Date)*", value=default_delivery)
        
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
            side_pocket_qty = st.number_input("Side Pocket Qty", 0, 2, 0)

        st.divider()

        # --- SECTION 4: BILL & NOTES ---
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            total_bill = st.number_input("Total Bill*", min_value=0, step=10, value=0)
        
        with col_p2:
            advance_paid = st.number_input("Advance Payment", min_value=0, step=10, value=0)
        
        with col_p3:
            # Calculate balance (display only, not interactive)
            balance_due = total_bill - advance_paid
            # Display balance as text instead of st.metric()
            st.write("**Balance Due:**")
            st.markdown(f"<h3 style='color: #e74c3c;'>₹{balance_due}</h3>", unsafe_allow_html=True)

        verbal_notes = st.text_area("🗣️ Verbal Summary / Special Notes", 
                                     placeholder="E.g. 17-6-1/4 swa, ya koi aur makhsoos nishani...")

        # Urgent order option
        urgent_order = st.checkbox("🚨 Mark as Urgent Order")

        # --- SECTION 5: FORM SUBMIT BUTTON (MUST USE st.form_submit_button) ---
        submitted = st.form_submit_button("✅ SAVE COMPLETE ORDER")
        
        if submitted:
            # Validate inputs
            if not client_name or not order_no or not phone_number:
                st.error("⚠️ Order Number, Client Name and Phone Number are required!")
            
            elif total_bill <= 0:
                st.error("❌ Total Bill must be greater than 0")
            
            else:
                # Save order
                success, order_details = save_order_to_db(
                    user_id=user_id,
                    client_name=client_name,
                    phone_number=phone_number,
                    order_no=order_no,
                    booking_date=booking_date,
                    delivery_date=delivery_date,
                    total_suits=total_suits,
                    address=address,
                    length=length,
                    sleeves=sleeves,
                    shoulder=shoulder,
                    collar=collar,
                    chest=chest,
                    l_chest=l_chest,
                    waist=waist,
                    hip=hip,
                    s_length=s_length,
                    bottom=bottom,
                    p_length=p_length,
                    p_waist=p_waist,
                    p_hip=p_hip,
                    thigh=thigh,
                    p_bottom=p_bottom,
                    fly=fly,
                    shirt_len=shirt_len,
                    shirt_collar=shirt_collar,
                    sherwani_collar=sherwani_collar,
                    sada=sada,
                    design=design,
                    design_no=design_no,
                    cuff_sleeves=cuff_sleeves,
                    kurta_sleeves=kurta_sleeves,
                    gol_daman=gol_daman,
                    chakor_daman=chakor_daman,
                    shalwar_ghera=shalwar_ghera,
                    side_pocket=side_pocket,
                    side_pocket_qty=side_pocket_qty,
                    front_pocket=front_pocket,
                    shalwar_pocket=shalwar_pocket,
                    pajama_pocket=pajama_pocket,
                    losing=losing,
                    smart_fit=smart_fit,
                    normal_fit=normal_fit,
                    gum_silai=gum_silai,
                    double_silai=double_silai,
                    total_bill=total_bill,
                    advance_paid=advance_paid,
                    balance_due=balance_due,
                    verbal_notes=verbal_notes,
                    urgent_order=urgent_order,
                    conn=conn
                )
                
                if success:
                    # Store success state and details
                    st.session_state.order_saved = True
                    st.session_state.saved_order_details = order_details
                    # Clear pre-filled data
                    if 'prefilled_customer' in st.session_state:
                        del st.session_state.prefilled_customer
                    # Rerun to show success page
                    st.rerun()
                else:
                    st.error("Failed to save order. Please try again.")

def save_order_to_db(**kwargs):
    """Save order to database and return success status"""
    try:
        user_id = kwargs['user_id']
        client_name = kwargs['client_name']
        phone_number = kwargs['phone_number']
        conn = kwargs['conn']
        
        # First, add or get client
        client_id = add_client(
            name=client_name, 
            phone=phone_number, 
            email="", 
            address=kwargs.get('address', ''),
            notes="",
            user_id=user_id
        )
        
        if client_id is None:
            # Client already exists, get existing client ID
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM clients WHERE phone = ? AND user_id = ?", 
                         (phone_number, user_id))
            existing_client = cursor.fetchone()
            client_id = existing_client[0] if existing_client else None
        
        if not client_id:
            return False, {"error": "Could not create or find client record"}
        
        # Create measurement data object
        m_data_obj = {
            "num_suits": kwargs['total_suits'],
            "measurements": {
                "Length": kwargs.get('length', ''),
                "Sleeves": kwargs.get('sleeves', ''),
                "Shoulder": kwargs.get('shoulder', ''),
                "Collar": kwargs.get('collar', ''),
                "Chest": kwargs.get('chest', ''),
                "Lower Chest": kwargs.get('l_chest', ''),
                "Waist": kwargs.get('waist', ''),
                "Hip": kwargs.get('hip', ''),
                "Shalwar Length": kwargs.get('s_length', ''),
                "Bottom": kwargs.get('bottom', ''),
                "Pajama Length": kwargs.get('p_length', ''),
                "Pajama Waist": kwargs.get('p_waist', ''),
                "Pajama Hip": kwargs.get('p_hip', ''),
                "Thigh": kwargs.get('thigh', ''),
                "Pajama Bottom": kwargs.get('p_bottom', ''),
                "Fly": kwargs.get('fly', ''),
                "Shirt Length": kwargs.get('shirt_len', '')
            },
            "styles": {
                "Shirt Collar": kwargs.get('shirt_collar', False),
                "Sherwani Collar": kwargs.get('sherwani_collar', False),
                "Sada": kwargs.get('sada', False),
                "Design": kwargs.get('design', False),
                "Design No": kwargs.get('design_no', ''),
                "Cuff Sleeves": kwargs.get('cuff_sleeves', False),
                "Kurta Sleeves": kwargs.get('kurta_sleeves', False),
                "Gol Daman": kwargs.get('gol_daman', False),
                "Chakor Daman": kwargs.get('chakor_daman', False),
                "Side Pocket": kwargs.get('side_pocket', False),
                "Side Pocket Qty": kwargs.get('side_pocket_qty', 0),
                "Front Pocket": kwargs.get('front_pocket', False),
                "Shalwar Pocket": kwargs.get('shalwar_pocket', False),
                "Pajama Pocket": kwargs.get('pajama_pocket', False),
                "Shalwar Ghera": kwargs.get('shalwar_ghera', False),
                "Losing": kwargs.get('losing', False),
                "Normal Fit": kwargs.get('normal_fit', False),
                "Smart Fit": kwargs.get('smart_fit', False),
                "Gum Silai": kwargs.get('gum_silai', False),
                "Double Silai": kwargs.get('double_silai', False)
            }
        }
        
        m_data_json = json.dumps(m_data_obj)
        cursor = conn.cursor()
        
        # Check database structure
        cursor.execute("PRAGMA table_info(orders)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'client_id' in columns:
            # New structure
            cursor.execute("""
                INSERT INTO orders (
                    user_id, client_id, client_name, client_phone, 
                    order_date, delivery_date, status, suits, 
                    order_no, total_bill, advance, balance, 
                    measurement_data, notes, address, is_synced
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, client_id, client_name, phone_number,
                kwargs['booking_date'].strftime("%Y-%m-%d"),
                kwargs['delivery_date'].strftime("%Y-%m-%d"),
                'Urgent' if kwargs.get('urgent_order', False) else 'Pending',
                kwargs['total_suits'],
                kwargs['order_no'],
                kwargs['total_bill'],
                kwargs['advance_paid'],
                kwargs['balance_due'],
                m_data_json,
                kwargs.get('verbal_notes', ''),
                kwargs.get('address', ''),
                0
            ))
            
            order_id = cursor.lastrowid
            
            # If advance paid, add to payments table
            if kwargs['advance_paid'] > 0:
                cursor.execute("""
                    INSERT INTO payments (order_id, amount, payment_date, payment_method, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    order_id,
                    kwargs['advance_paid'],
                    kwargs['booking_date'].strftime("%Y-%m-%d"),
                    "Cash",
                    f"Advance payment for order #{kwargs['order_no']}"
                ))
        
        else:
            # Old structure
            cursor.execute("""
                INSERT INTO orders 
                (user_id, client_name, client_phone, total_bill, paid_amount, balance, 
                 order_date, status, measurement_data, notes, order_no, is_synced) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                user_id, client_name, phone_number, 
                kwargs['total_bill'], kwargs['advance_paid'], kwargs['balance_due'], 
                kwargs['booking_date'].strftime("%Y-%m-%d"), 
                'Urgent' if kwargs.get('urgent_order', False) else 'Pending', 
                m_data_json, kwargs.get('verbal_notes', ''), kwargs['order_no'], 0
            ))
            
            order_id = cursor.lastrowid
        
        conn.commit()
        
        # Return success with order details
        order_details = {
            "order_id": order_id,
            "order_no": kwargs['order_no'],
            "client_name": client_name,
            "suits": kwargs['total_suits'],
            "total_bill": kwargs['total_bill'],
            "balance_due": kwargs['balance_due']
        }
        
        return True, order_details
    
    except Exception as e:
        st.error(f"❌ Database Error: {str(e)}")
        return False, {"error": str(e)}

def show_order_success(order_details):
    """Show success message and next steps"""
    st.success(f"🎉 Order #{order_details['order_no']} for {order_details['client_name']} ({order_details['suits']} Suits) saved successfully!")
    st.balloons()
    
    st.markdown("---")
    st.subheader("📋 Next Steps")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 View This Order", key="view_order_btn", use_container_width=True):
            # Store order_id in session to view later
            st.session_state.view_order_id = order_details['order_id']
            st.session_state.order_saved = False
            st.rerun()
    
    with col2:
        if st.button("🖨️ Print Slip", key="print_slip_btn", use_container_width=True):
            st.info("Print feature coming soon!")
            # Reset for new order
            st.session_state.order_saved = False
            st.rerun()
    
    with col3:
        if st.button("➕ Add Another Order", key="add_another_btn", use_container_width=True):
            # Reset for new order
            st.session_state.order_saved = False
            st.rerun()
    
    # Quick stats
    st.markdown("---")
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("Order Total", f"₹{order_details['total_bill']:,}")
    with col_stats2:
        st.metric("Balance Due", f"₹{order_details['balance_due']:,}")
    with col_stats3:
        st.metric("Order Status", "Pending")

# Alternative function name for compatibility
def add_order_ui(user_id=None):
    """Alternative function name for compatibility"""
    conn = get_connection()
    show_order_form(conn)
    conn.close()
