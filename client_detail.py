import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from database import DB_NAME, get_connection, add_client, create_quick_order, quick_search_customers

def show_client_management():
    st.title("👥 Client Management")
    
    # Get user_id from session
    user_id = st.session_state.get('user_id', 1)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Add New Client", "Search Clients", "Quick Order", "Client Profiles"])
    
    with tab1:
        # Existing client add form
        st.subheader("Add New Client")
        with st.form("add_client_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name*")
                phone = st.text_input("Phone Number*")
                email = st.text_input("Email")
            
            with col2:
                address = st.text_area("Address", height=100)
                notes = st.text_area("Additional Notes", placeholder="Measurement preferences, special instructions, etc.")
            
            # Add measurement template section
            st.subheader("📏 Measurement Template (Optional)")
            m_col1, m_col2, m_col3 = st.columns(3)
            
            with m_col1:
                length = st.text_input("Length", placeholder="42.5")
                chest = st.text_input("Chest", placeholder="40")
                shoulder = st.text_input("Shoulder", placeholder="20")
            
            with m_col2:
                sleeves = st.text_input("Sleeves", placeholder="25.5")
                waist = st.text_input("Waist", placeholder="36")
                hip = st.text_input("Hip", placeholder="38")
            
            with m_col3:
                collar = st.text_input("Collar", placeholder="17")
                shalwar_len = st.text_input("Shalwar Length", placeholder="40")
                bottom = st.text_input("Bottom", placeholder="22")
            
            submitted = st.form_submit_button("Add Client")
            
            if submitted:
                if name and phone:
                    # Create measurement template if provided
                    measurement_template = {}
                    if any([length, chest, shoulder, sleeves, waist, hip, collar, shalwar_len, bottom]):
                        measurement_template = {
                            'length': length,
                            'chest': chest,
                            'shoulder': shoulder,
                            'sleeves': sleeves,
                            'waist': waist,
                            'hip': hip,
                            'collar': collar,
                            'shalwar_len': shalwar_len,
                            'bottom': bottom
                        }
                    
                    # Add client with measurement template
                    client_id = add_client(
                        name=name, 
                        phone=phone, 
                        email=email, 
                        address=address,
                        notes=notes,
                        measurement_template=measurement_template,
                        user_id=user_id
                    )
                    
                    if client_id:
                        st.success(f"✅ Client {name} added successfully!")
                        st.balloons()
                        
                        # Show quick actions
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("📝 Create Order for This Client"):
                                st.session_state.prefilled_customer = {
                                    'name': name,
                                    'phone': phone,
                                    'email': email,
                                    'address': address
                                }
                                st.rerun()
                        
                        with col_b:
                            if st.button("➕ Add Another Client"):
                                st.rerun()
                    else:
                        st.error("Client with this phone number already exists!")
                else:
                    st.error("❌ Name and Phone are required fields")
    
    with tab2:
        # Advanced Search
        st.subheader("🔍 Search Clients")
        
        search_col1, search_col2, search_col3 = st.columns(3)
        
        with search_col1:
            search_name = st.text_input("Search by Name")
            min_orders = st.number_input("Minimum Orders", min_value=0, value=0)
        
        with search_col2:
            search_phone = st.text_input("Search by Phone")
            last_order_days = st.number_input("Last Order Within (days)", min_value=0, value=0)
        
        with search_col3:
            sort_by = st.selectbox("Sort By", 
                                  ["Name (A-Z)", "Name (Z-A)", "Recent Orders", "Total Spent", "Balance Due"])
            
            show_only_with_balance = st.checkbox("Show only clients with balance due")
        
        if st.button("🔍 Search Clients", type="primary", use_container_width=True):
            clients = search_clients(
                name=search_name, 
                phone=search_phone, 
                min_orders=min_orders, 
                last_order_days=last_order_days,
                user_id=user_id
            )
            
            if clients:
                df = pd.DataFrame(clients)
                
                # Apply balance filter
                if show_only_with_balance:
                    if 'total_balance' in df.columns:
                        df = df[df['total_balance'] > 0]
                    elif 'balance' in df.columns:
                        df = df[df['balance'] > 0]
                
                # Apply sorting
                if sort_by == "Name (A-Z)":
                    df = df.sort_values('name', ascending=True)
                elif sort_by == "Name (Z-A)":
                    df = df.sort_values('name', ascending=False)
                elif sort_by == "Recent Orders":
                    if 'last_order_date' in df.columns:
                        df = df.sort_values('last_order_date', ascending=False)
                elif sort_by == "Total Spent":
                    if 'total_spent' in df.columns:
                        df = df.sort_values('total_spent', ascending=False)
                elif sort_by == "Balance Due":
                    if 'total_balance' in df.columns:
                        df = df.sort_values('total_balance', ascending=False)
                
                # Display with better formatting
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "name": "Name",
                        "phone": "Phone",
                        "email": "Email",
                        "total_orders": st.column_config.NumberColumn("Total Orders", format="%d"),
                        "total_spent": st.column_config.NumberColumn("Total Spent", format="₹%.0f"),
                        "total_balance": st.column_config.NumberColumn("Balance Due", format="₹%.0f"),
                        "last_order_date": "Last Order"
                    }
                )
                
                # Summary stats
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                with col_sum1:
                    st.metric("Total Clients", len(df))
                with col_sum2:
                    total_spent = df['total_spent'].sum() if 'total_spent' in df.columns else 0
                    st.metric("Total Spent", f"₹{total_spent:,.0f}")
                with col_sum3:
                    total_balance = df['total_balance'].sum() if 'total_balance' in df.columns else 0
                    st.metric("Total Balance Due", f"₹{total_balance:,.0f}")
                
                # Export option
                st.divider()
                col_exp1, col_exp2 = st.columns(2)
                
                with col_exp1:
                    if st.button("📥 Export to CSV", use_container_width=True):
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"clients_export_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                with col_exp2:
                    if st.button("📊 View Statistics", use_container_width=True):
                        show_client_statistics(df)
            
            else:
                st.info("No clients found matching your criteria")
    
    with tab3:
        # Quick Order for Existing Customer
        st.subheader("⚡ Quick Order - Existing Customer")
        
        col_search1, col_search2 = st.columns([3, 1])
        
        with col_search1:
            search_term = st.text_input("Enter customer name or phone to search", 
                                       placeholder="Type name or phone number...")
        
        with col_search2:
            show_all = st.checkbox("Show All", value=False)
        
        if search_term or show_all:
            if show_all:
                customers = get_all_clients(user_id)
            else:
                customers = quick_search_customers(search_term, user_id)
            
            if customers:
                # Display customers in cards
                cols = st.columns(2)
                for idx, customer in enumerate(customers[:10]):  # Limit to 10 for performance
                    with cols[idx % 2]:
                        with st.container(border=True):
                            st.markdown(f"**{customer['name']}**")
                            st.markdown(f"📱 {customer['phone']}")
                            if customer.get('email'):
                                st.markdown(f"📧 {customer['email']}")
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("📝 Quick Order", key=f"order_{customer['id']}"):
                                    st.session_state.quick_order_customer = customer
                                    st.rerun()
                            with col_btn2:
                                if st.button("👁️ Profile", key=f"profile_{customer['id']}"):
                                    show_client_profile(customer['id'], user_id)
                
                # If customer selected for quick order
                if 'quick_order_customer' in st.session_state:
                    customer = st.session_state.quick_order_customer
                    
                    st.divider()
                    st.subheader(f"Quick Order for {customer['name']}")
                    
                    with st.form("quick_order_form"):
                        col_o1, col_o2 = st.columns(2)
                        
                        with col_o1:
                            order_type = st.selectbox("Order Type", 
                                                     ["Shirt", "Pant", "Suit", "Sherwani", "Blazer", "Other"])
                            quantity = st.number_input("Quantity", min_value=1, value=1)
                        
                        with col_o2:
                            delivery_date = st.date_input("Delivery Date", 
                                                         value=datetime.now() + timedelta(days=7))
                            urgent = st.checkbox("🚨 Urgent Order")
                        
                        special_instructions = st.text_area("Special Instructions")
                        
                        col_sub1, col_sub2 = st.columns(2)
                        
                        with col_sub1:
                            if st.form_submit_button("✅ Create Quick Order", use_container_width=True):
                                order_id = create_quick_order(
                                    customer_id=customer['id'],
                                    order_type=order_type,
                                    quantity=quantity,
                                    urgent=urgent,
                                    delivery_date=delivery_date.strftime("%Y-%m-%d"),
                                    special_instructions=special_instructions,
                                    user_id=user_id
                                )
                                
                                if order_id:
                                    st.success(f"✅ Quick order created successfully! Order ID: {order_id}")
                                    del st.session_state.quick_order_customer
                                    st.rerun()
                        
                        with col_sub2:
                            if st.button("❌ Cancel", use_container_width=True):
                                del st.session_state.quick_order_customer
                                st.rerun()
            
            else:
                st.info("No customers found")
    
    with tab4:
        # Client Profiles - Show all clients with quick actions
        st.subheader("📋 All Clients")
        
        all_clients = get_all_clients(user_id)
        
        if all_clients:
            # Search within all clients
            search_profile = st.text_input("Search in all clients", key="profile_search")
            
            if search_profile:
                all_clients = [c for c in all_clients 
                              if search_profile.lower() in c['name'].lower() 
                              or search_profile in c.get('phone', '')]
            
            # Display in a table with actions
            for client in all_clients:
                with st.expander(f"👤 {client['name']} - 📱 {client.get('phone', 'N/A')}"):
                    col_info, col_actions = st.columns([2, 1])
                    
                    with col_info:
                        st.write(f"**Email:** {client.get('email', 'N/A')}")
                        st.write(f"**Address:** {client.get('address', 'N/A')}")
                        st.write(f"**Total Orders:** {client.get('total_orders', 0)}")
                        st.write(f"**Last Order:** {client.get('last_order_date', 'Never')}")
                        
                        if client.get('measurement_template'):
                            st.write("**📏 Saved Measurements:**")
                            template = client['measurement_template']
                            if isinstance(template, str):
                                try:
                                    import json
                                    template = json.loads(template)
                                except:
                                    template = {}
                            
                            if template:
                                for key, value in template.items():
                                    if value:
                                        st.write(f"  • {key}: {value}")
                    
                    with col_actions:
                        if st.button("📝 New Order", key=f"new_order_{client['id']}"):
                            st.session_state.prefilled_customer = {
                                'name': client['name'],
                                'phone': client.get('phone', ''),
                                'email': client.get('email', ''),
                                'address': client.get('address', '')
                            }
                            st.rerun()
                        
                        if st.button("📞 Contact", key=f"contact_{client['id']}"):
                            phone = client.get('phone', '')
                            if phone:
                                st.info(f"Call/WhatsApp: {phone}")
                        
                        if st.button("📊 View Details", key=f"details_{client['id']}"):
                            show_client_profile(client['id'], user_id)
        
        else:
            st.info("No clients in database. Add your first client above!")

# =============== DATABASE FUNCTIONS ===============

def search_clients(name="", phone="", min_orders=0, last_order_days=0, user_id=1):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        c.id,
        c.name,
        c.phone,
        c.email,
        c.address,
        c.notes,
        c.measurement_template,
        COUNT(o.id) as total_orders,
        SUM(o.total_bill) as total_spent,
        SUM(o.balance) as total_balance,
        MAX(o.order_date) as last_order_date
    FROM clients c
    LEFT JOIN orders o ON c.id = o.client_id AND o.user_id = ?
    WHERE c.user_id = ?
    """
    
    params = [user_id, user_id]
    
    if name:
        query += " AND c.name LIKE ?"
        params.append(f"%{name}%")
    
    if phone:
        query += " AND c.phone LIKE ?"
        params.append(f"%{phone}%")
    
    query += " GROUP BY c.id"
    
    if min_orders > 0:
        query += " HAVING COUNT(o.id) >= ?"
        params.append(min_orders)
    
    cursor.execute(query, params)
    clients = cursor.fetchall()
    
    # Filter by last order days if specified
    if last_order_days > 0:
        cutoff_date = (datetime.now() - timedelta(days=last_order_days)).strftime("%Y-%m-%d")
        clients = [c for c in clients if c[10] and c[10] >= cutoff_date]
    
    # Convert to list of dictionaries
    columns = [description[0] for description in cursor.description]
    result = []
    
    for client in clients:
        client_dict = dict(zip(columns, client))
        
        # Parse measurement template if it's a JSON string
        if client_dict.get('measurement_template'):
            try:
                import json
                template = client_dict['measurement_template']
                if isinstance(template, str):
                    client_dict['measurement_template'] = json.loads(template)
            except:
                client_dict['measurement_template'] = {}
        
        result.append(client_dict)
    
    conn.close()
    return result

def get_all_clients(user_id=1):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        c.id,
        c.name,
        c.phone,
        c.email,
        c.address,
        c.measurement_template,
        COUNT(o.id) as total_orders,
        MAX(o.order_date) as last_order_date
    FROM clients c
    LEFT JOIN orders o ON c.id = o.client_id AND o.user_id = ?
    WHERE c.user_id = ?
    GROUP BY c.id
    ORDER BY c.name
    """
    
    cursor.execute(query, (user_id, user_id))
    clients = cursor.fetchall()
    
    columns = [description[0] for description in cursor.description]
    result = []
    
    for client in clients:
        client_dict = dict(zip(columns, client))
        
        # Parse measurement template
        if client_dict.get('measurement_template'):
            try:
                import json
                template = client_dict['measurement_template']
                if isinstance(template, str):
                    client_dict['measurement_template'] = json.loads(template)
            except:
                client_dict['measurement_template'] = {}
        
        result.append(client_dict)
    
    conn.close()
    return result

def show_client_profile(client_id, user_id=1):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get client details
    cursor.execute("""
        SELECT c.*, 
               COUNT(o.id) as total_orders,
               SUM(o.total_bill) as total_spent,
               SUM(o.balance) as total_balance,
               MAX(o.order_date) as last_order_date
        FROM clients c
        LEFT JOIN orders o ON c.id = o.client_id AND o.user_id = ?
        WHERE c.id = ? AND c.user_id = ?
        GROUP BY c.id
    """, (user_id, client_id, user_id))
    
    client = cursor.fetchone()
    
    if client:
        columns = [description[0] for description in cursor.description]
        client_dict = dict(zip(columns, client))
        
        # Create a popup-like container
        with st.container(border=True):
            st.subheader(f"👤 {client_dict['name']}'s Profile")
            
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.write(f"**📱 Phone:** {client_dict['phone']}")
                if client_dict.get('email'):
                    st.write(f"**📧 Email:** {client_dict['email']}")
                st.write(f"**📍 Address:** {client_dict.get('address', 'N/A')}")
            
            with col_info2:
                st.write(f"**📦 Total Orders:** {client_dict['total_orders']}")
                st.write(f"**💰 Total Spent:** ₹{client_dict.get('total_spent', 0):,.0f}")
                st.write(f"**⚖️ Balance Due:** ₹{client_dict.get('total_balance', 0):,.0f}")
                st.write(f"**📅 Last Order:** {client_dict.get('last_order_date', 'Never')}")
            
            # Show measurement template
            if client_dict.get('measurement_template'):
                st.subheader("📏 Saved Measurements")
                
                template = client_dict['measurement_template']
                if isinstance(template, str):
                    try:
                        import json
                        template = json.loads(template)
                    except:
                        template = {}
                
                if template:
                    cols = st.columns(3)
                    col_idx = 0
                    for key, value in template.items():
                        if value:
                            with cols[col_idx % 3]:
                                st.metric(key.replace('_', ' ').title(), value)
                            col_idx += 1
            
            # Show recent orders
            st.subheader("📋 Recent Orders")
            cursor.execute("""
                SELECT o.id, o.order_no, o.order_date, o.delivery_date, 
                       o.status, o.total_bill, o.balance
                FROM orders o
                WHERE o.client_id = ? AND o.user_id = ?
                ORDER BY o.order_date DESC
                LIMIT 5
            """, (client_id, user_id))
            
            recent_orders = cursor.fetchall()
            
            if recent_orders:
                for order in recent_orders:
                    st.write(f"**Order #{order[1]}** - {order[2]} | Status: {order[4]} | Amount: ₹{order[5]}")
            else:
                st.info("No orders yet")
            
            # Action buttons
            col_act1, col_act2, col_act3 = st.columns(3)
            
            with col_act1:
                if st.button("📝 New Order", use_container_width=True):
                    st.session_state.prefilled_customer = {
                        'name': client_dict['name'],
                        'phone': client_dict['phone'],
                        'email': client_dict.get('email', ''),
                        'address': client_dict.get('address', '')
                    }
                    st.rerun()
            
            with col_act2:
                if st.button("✏️ Edit Profile", use_container_width=True):
                    st.info("Edit feature coming soon!")
            
            with col_act3:
                if st.button("📞 Contact", use_container_width=True):
                    phone = client_dict['phone']
                    st.info(f"Call/WhatsApp: {phone}")
    
    conn.close()

def show_client_statistics(df):
    """Show statistics about clients"""
    with st.expander("📊 Client Statistics", expanded=True):
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            avg_orders = df['total_orders'].mean() if 'total_orders' in df.columns else 0
            st.metric("Average Orders per Client", f"{avg_orders:.1f}")
        
        with col_stat2:
            repeat_clients = len(df[df['total_orders'] > 1]) if 'total_orders' in df.columns else 0
            st.metric("Repeat Clients", repeat_clients)
        
        with col_stat3:
            new_clients = len(df[df['total_orders'] == 0]) if 'total_orders' in df.columns else 0
            st.metric("New Clients (No orders yet)", new_clients)
        
        # Top clients by spending
        if 'total_spent' in df.columns:
            st.subheader("🏆 Top 5 Clients by Spending")
            top_clients = df.nlargest(5, 'total_spent')[['name', 'total_spent', 'total_orders']]
            st.dataframe(top_clients, use_container_width=True)
