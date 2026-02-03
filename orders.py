import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_all_orders, update_order_status, get_order_status_history, get_today_summary

def show_orders_page():
    st.title("📋 Orders Management")
    
    # Get current user ID from session (default to 1 for admin)
    user_id = st.session_state.get('user_id', 1)
    
    # Tab layout
    tab1, tab2 = st.tabs(["Order Tracking", "Today's Summary"])
    
    with tab1:
        # Order Status Workflow Section
        st.subheader("Order Status Tracking")
        
        # Status filter
        col_filter1, col_filter2 = st.columns([2, 1])
        
        with col_filter1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Pending", "Cutting", "Stitching", "Fitting", "Ready", "Delivered", "Urgent"]
            )
        
        # Search functionality
        with col_filter2:
            search_term = st.text_input("Search (Name/Order No)", "")
        
        # Get all orders
        orders = get_all_orders(user_id=user_id, status_filter=status_filter if status_filter != "All" else None)
        
        if not orders:
            st.info("No orders found")
        
        else:
            # Convert to DataFrame
            df = pd.DataFrame(orders)
            
            # Apply search filter
            if search_term:
                search_mask = (
                    df['client_name'].str.contains(search_term, case=False, na=False) |
                    df['order_no'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['client_phone'].astype(str).str.contains(search_term, case=False, na=False)
                )
                df = df[search_mask]
            
            if df.empty:
                st.info("No orders match your search criteria")
            
            else:
                # Display orders with status update option
                for _, order in df.iterrows():
                    # Determine status color
                    status_colors = {
                        'Pending': '⚪',
                        'Cutting': '🔵', 
                        'Stitching': '🟡',
                        'Fitting': '🟠',
                        'Ready': '🟢',
                        'Delivered': '✅',
                        'Urgent': '🚨'
                    }
                    
                    status_icon = status_colors.get(order.get('status', 'Pending'), '⚪')
                    
                    with st.expander(f"{status_icon} Order #{order.get('id', '')} - {order.get('client_name', 'N/A')} - {order.get('status', 'Pending')}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Order No:** {order.get('order_no', 'N/A')}")
                            st.write(f"**Order Date:** {order.get('order_date', 'N/A')}")
                            st.write(f"**Delivery Date:** {order.get('delivery_date', 'N/A')}")
                            st.write(f"**Suits:** {order.get('suits', 1)}")
                            st.write(f"**Total Bill:** ₹{order.get('total_bill', 0)}")
                            st.write(f"**Advance:** ₹{order.get('advance', 0)}")
                            st.write(f"**Balance:** ₹{order.get('balance', 0)}")
                            
                            if order.get('notes'):
                                st.write(f"**Notes:** {order.get('notes')}")
                        
                        with col2:
                            # Status update dropdown
                            current_status = order.get('status', 'Pending')
                            status_options = ["Pending", "Cutting", "Stitching", "Fitting", "Ready", "Delivered", "Urgent"]
                            
                            # Handle case where current status might not be in standard options
                            if current_status not in status_options:
                                status_options = [current_status] + [s for s in ["Pending", "Cutting", "Stitching", "Fitting", "Ready", "Delivered", "Urgent"] if s != current_status]
                            
                            new_status = st.selectbox(
                                "Update Status",
                                status_options,
                                index=status_options.index(current_status),
                                key=f"status_{order.get('id')}"
                            )
                            
                            update_notes = st.text_area(
                                "Status Notes (Optional)",
                                key=f"notes_{order.get('id')}",
                                height=60
                            )
                            
                            col_btn1, col_btn2 = st.columns(2)
                            
                            with col_btn1:
                                if st.button("Update", key=f"update_{order.get('id')}"):
                                    update_order_status(order.get('id'), new_status, update_notes)
                                    st.success(f"Status updated to {new_status}")
                                    st.rerun()
                            
                            with col_btn2:
                                if st.button("History", key=f"history_{order.get('id')}"):
                                    history = get_order_status_history(order.get('id'))
                                    if history:
                                        st.write("### Status History")
                                        for h in history:
                                            st.write(f"**{h.get('status', 'N/A')}** - {h.get('timestamp', 'N/A')}")
                                            if h.get('notes'):
                                                st.write(f"*Notes:* {h.get('notes')}")
                                    else:
                                        st.info("No status history available")
                            
                            # Quick actions
                            st.markdown("---")
                            if st.button("📱 Contact", key=f"contact_{order.get('id')}"):
                                phone = order.get('client_phone', '')
                                if phone:
                                    st.info(f"Call/WhatsApp: {phone}")
                                else:
                                    st.warning("No phone number available")
    
    with tab2:
        # Today's summary card
        st.subheader("📊 Today's Summary")
        
        summary = get_today_summary(user_id=user_id)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Today's Orders", summary['today_orders'])
        
        with col2:
            st.metric("Today's Deliveries", summary['today_deliveries'])
        
        with col3:
            st.metric("Today's Revenue", f"₹{summary['today_revenue']}")
        
        with col4:
            st.metric("Payments Received", f"₹{summary['today_payments']}")
        
        # Pending and Outstanding
        col5, col6 = st.columns(2)
        
        with col5:
            st.metric("Pending Orders", summary['pending_orders'])
        
        with col6:
            st.metric("Total Outstanding", f"₹{summary['total_outstanding']}")
        
        # Show today's orders in a table
        st.subheader("📋 Today's Orders")
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_orders = [o for o in orders if o.get('order_date') == today]
        
        if today_orders:
            today_df = pd.DataFrame(today_orders)
            
            # Select only important columns for display
            display_cols = ['client_name', 'order_no', 'status', 'total_bill', 'advance', 'balance']
            available_cols = [col for col in display_cols if col in today_df.columns]
            
            if available_cols:
                st.dataframe(today_df[available_cols], use_container_width=True)
        else:
            st.info("No orders placed today")
        
        # Delivery alerts
        st.subheader("🚨 Upcoming Deliveries")
        
        # Get orders with delivery in next 3 days
        upcoming_deliveries = []
        for order in orders:
            delivery_date = order.get('delivery_date')
            if delivery_date:
                try:
                    delivery_dt = datetime.strptime(delivery_date, "%Y-%m-%d")
                    days_diff = (delivery_dt - datetime.now()).days
                    if 0 <= days_diff <= 3 and order.get('status') != 'Delivered':
                        upcoming_deliveries.append(order)
                except:
                    pass
        
        if upcoming_deliveries:
            for order in upcoming_deliveries:
                st.warning(
                    f"**{order.get('client_name')}** - Order #{order.get('order_no')} "
                    f"due on {order.get('delivery_date')} ({order.get('status')})"
                )
        else:
            st.info("No upcoming deliveries in next 3 days")
