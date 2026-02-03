import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import get_connection, DB_NAME

# =====================================================
# MAIN ANALYTICS DASHBOARD - DUAL VIEW (Super Admin & Shopkeeper)
# =====================================================
def show_analytics_dashboard():
    """Main analytics dashboard - automatically detects user role"""
    
    # Get user info from session
    user_id = st.session_state.get('user_id', 1)
    user_role = st.session_state.get('role', 'admin')
    user_email = st.session_state.get('email', '')
    
    st.title("📊 Analytics Dashboard")
    
    # Role-based tabs
    if user_role == 'super_admin':
        # Super Admin View
        tab1, tab2, tab3 = st.tabs(["🏪 Global Overview", "📈 Shop Analytics", "👥 Client Insights"])
        
        with tab1:
            show_global_stats()
        
        with tab2:
            show_shop_comparison()
        
        with tab3:
            show_client_insights(user_id)
    
    else:
        # Regular Shopkeeper View
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Today's Summary", "📈 Business Trends", "💰 Financial Overview", "👥 Customer Analytics"])
        
        with tab1:
            show_today_summary(user_id)
        
        with tab2:
            show_business_trends(user_id)
        
        with tab3:
            show_financial_overview(user_id)
        
        with tab4:
            show_customer_analytics(user_id)


# =====================================================
# SUPER ADMIN FUNCTIONS
# =====================================================
def show_global_stats():
    """Super Admin: Global system overview"""
    
    st.header("🌍 Global System Overview")
    
    conn = get_connection()
    
    # -------- Summary Metrics --------
    stats_query = """
    SELECT
        COUNT(*) as total_shops,
        SUM(CASE WHEN fee_status='paid' THEN 1 ELSE 0 END) as paid_shops,
        SUM(CASE WHEN fee_status!='paid' THEN 1 ELSE 0 END) as pending_shops
    FROM users
    WHERE role='admin' AND status='Active'
    """
    
    stats = pd.read_sql(stats_query, conn)
    
    # Platform business calculation
    business_query = """
    SELECT SUM(o.total_bill) as total_business
    FROM orders o
    JOIN users u ON o.user_id = u.id
    WHERE u.role='admin'
    """
    
    total_rev = pd.read_sql(business_query, conn).iloc[0, 0] or 0
    
    # Recent growth (last 30 days)
    growth_query = """
    SELECT 
        SUM(CASE WHEN o.order_date >= date('now', '-30 days') THEN o.total_bill ELSE 0 END) as monthly_business,
        SUM(CASE WHEN o.order_date >= date('now', '-60 days') AND o.order_date < date('now', '-30 days') 
                THEN o.total_bill ELSE 0 END) as previous_month_business
    FROM orders o
    JOIN users u ON o.user_id = u.id
    WHERE u.role='admin'
    """
    
    growth_df = pd.read_sql(growth_query, conn)
    monthly_growth = 0
    if growth_df['previous_month_business'][0] > 0:
        monthly_growth = ((growth_df['monthly_business'][0] or 0) - growth_df['previous_month_business'][0]) / growth_df['previous_month_business'][0] * 100
    
    # Display metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏪 Partner Shops", int(stats['total_shops'][0]))
    c2.metric("✅ Paid Shops", int(stats['paid_shops'][0]))
    c3.metric("⚠️ Pending Shops", int(stats['pending_shops'][0]))
    c4.metric("💰 Platform Business", f"₹{total_rev:,.0f}", f"{monthly_growth:.1f}%")
    
    st.markdown("---")
    
    # -------- Shops Detail Table --------
    st.subheader("👥 Shops & Contact Details")
    
    shops_df = pd.read_sql("""
        SELECT 
            id,
            shop_name,
            phone,
            email,
            fee_status,
            status,
            created_at
        FROM users
        WHERE role='admin'
        ORDER BY created_at DESC
    """, conn)
    
    if shops_df.empty:
        st.info("No shops registered yet.")
    else:
        # Calculate shop performance
        shop_performance = pd.read_sql("""
            SELECT 
                u.id as shop_id,
                u.shop_name,
                COUNT(o.id) as total_orders,
                SUM(o.total_bill) as total_revenue,
                AVG(o.total_bill) as avg_order_value
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            WHERE u.role='admin'
            GROUP BY u.id, u.shop_name
        """, conn)
        
        # Merge with shops_df
        shops_df = pd.merge(shops_df, shop_performance, left_on='id', right_on='shop_id', how='left')
        shops_df = shops_df[['shop_name', 'phone', 'email', 'fee_status', 'status', 
                            'total_orders', 'total_revenue', 'avg_order_value', 'created_at']]
        
        # Format columns
        shops_df['total_revenue'] = shops_df['total_revenue'].apply(lambda x: f"₹{x:,.0f}" if pd.notnull(x) else "₹0")
        shops_df['avg_order_value'] = shops_df['avg_order_value'].apply(lambda x: f"₹{x:,.0f}" if pd.notnull(x) else "₹0")
        
        st.dataframe(shops_df, use_container_width=True)
    
    conn.close()

def show_shop_comparison():
    """Super Admin: Compare shops performance"""
    
    st.header("📊 Shop Performance Comparison")
    
    conn = get_connection()
    
    # Get shop performance data
    query = """
    SELECT 
        u.shop_name,
        COUNT(o.id) as total_orders,
        SUM(o.total_bill) as total_revenue,
        SUM(CASE WHEN o.status = 'Delivered' THEN 1 ELSE 0 END) as delivered_orders,
        SUM(CASE WHEN o.status != 'Delivered' THEN o.balance ELSE 0 END) as pending_balance,
        AVG(o.total_bill) as avg_order_value,
        MIN(o.order_date) as first_order_date,
        MAX(o.order_date) as last_order_date
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.role='admin'
    GROUP BY u.id, u.shop_name
    HAVING COUNT(o.id) > 0
    ORDER BY total_revenue DESC
    """
    
    shop_data = pd.read_sql(query, conn)
    
    if shop_data.empty:
        st.info("No order data available for comparison.")
        conn.close()
        return
    
    # Top 10 shops by revenue
    st.subheader("🏆 Top 10 Shops by Revenue")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        top_shops = shop_data.nlargest(10, 'total_revenue')
        fig = px.bar(
            top_shops,
            x='shop_name',
            y='total_revenue',
            title="Top Performing Shops",
            color='total_orders',
            labels={'shop_name': 'Shop', 'total_revenue': 'Total Revenue (₹)', 'total_orders': 'Orders'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Metrics card
        avg_order_value = shop_data['avg_order_value'].mean()
        total_platform_revenue = shop_data['total_revenue'].sum()
        total_platform_orders = shop_data['total_orders'].sum()
        
        st.metric("📦 Total Platform Orders", f"{total_platform_orders:,}")
        st.metric("💰 Total Platform Revenue", f"₹{total_platform_revenue:,.0f}")
        st.metric("📊 Average Order Value", f"₹{avg_order_value:,.0f}")
    
    # Performance matrix
    st.subheader("📈 Performance Matrix")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(
            shop_data,
            x='total_orders',
            y='avg_order_value',
            size='total_revenue',
            color='shop_name',
            hover_data=['delivered_orders'],
            title="Orders vs Average Value"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Efficiency metric: Revenue per order
        shop_data['revenue_per_order'] = shop_data['total_revenue'] / shop_data['total_orders']
        fig = px.bar(
            shop_data.nlargest(10, 'revenue_per_order'),
            x='shop_name',
            y='revenue_per_order',
            title="Revenue per Order (Efficiency)",
            color='total_orders'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    conn.close()


# =====================================================
# SHOPKEEPER FUNCTIONS
# =====================================================
def show_today_summary(user_id):
    """Shopkeeper: Today's summary dashboard"""
    
    st.header("📊 Today's Summary")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Today's metrics
    cursor.execute("""
        SELECT 
            COUNT(*) as today_orders,
            SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) as today_deliveries,
            SUM(CASE WHEN status = 'Delivered' THEN total_bill ELSE 0 END) as today_revenue,
            SUM(advance) as today_advance
        FROM orders 
        WHERE user_id = ? AND order_date = ?
    """, (user_id, today))
    
    today_stats = cursor.fetchone()
    
    # Weekly metrics
    cursor.execute("""
        SELECT 
            COUNT(*) as weekly_orders,
            SUM(total_bill) as weekly_revenue,
            SUM(balance) as weekly_balance
        FROM orders 
        WHERE user_id = ? AND order_date >= date('now', '-7 days')
    """, (user_id,))
    
    weekly_stats = cursor.fetchone()
    
    # Pending orders
    cursor.execute("""
        SELECT 
            COUNT(*) as pending_orders,
            SUM(balance) as total_outstanding
        FROM orders 
        WHERE user_id = ? AND status != 'Delivered'
    """, (user_id,))
    
    pending_stats = cursor.fetchone()
    
    # Recent payments
    cursor.execute("""
        SELECT SUM(amount) as today_payments
        FROM payments p
        JOIN orders o ON p.order_id = o.id
        WHERE o.user_id = ? AND p.payment_date = ?
    """, (user_id, today))
    
    today_payments = cursor.fetchone()[0] or 0
    
    conn.close()
    
    # Display metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        today_orders = today_stats[0] or 0 if today_stats else 0
        st.metric("📥 Today's Orders", today_orders)
    
    with col2:
        today_deliveries = today_stats[1] or 0 if today_stats else 0
        st.metric("📤 Today's Deliveries", today_deliveries)
    
    with col3:
        today_revenue = today_stats[2] or 0 if today_stats else 0
        st.metric("💰 Today's Revenue", f"₹{today_revenue:,.0f}")
    
    with col4:
        st.metric("💳 Today's Payments", f"₹{today_payments:,.0f}")
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        weekly_orders = weekly_stats[0] or 0 if weekly_stats else 0
        st.metric("📦 Weekly Orders", weekly_orders)
    
    with col6:
        weekly_revenue = weekly_stats[1] or 0 if weekly_stats else 0
        st.metric("💰 Weekly Revenue", f"₹{weekly_revenue:,.0f}")
    
    with col7:
        pending_orders = pending_stats[0] or 0 if pending_stats else 0
        st.metric("⏳ Pending Orders", pending_orders)
    
    with col8:
        total_outstanding = pending_stats[1] or 0 if pending_stats else 0
        st.metric("📋 Outstanding", f"₹{total_outstanding:,.0f}")
    
    # Today's orders list
    st.subheader("📋 Today's Orders")
    conn = get_connection()
    today_orders_df = pd.read_sql("""
        SELECT 
            o.order_no,
            o.client_name,
            o.status,
            o.total_bill,
            o.advance,
            o.balance,
            o.delivery_date
        FROM orders o
        WHERE o.user_id = ? AND o.order_date = ?
        ORDER BY o.created_at DESC
    """, conn, params=(user_id, today))
    conn.close()
    
    if not today_orders_df.empty:
        st.dataframe(today_orders_df, use_container_width=True)
    else:
        st.info("No orders today")

def show_business_trends(user_id):
    """Shopkeeper: Business trends and charts"""
    
    st.header("📈 Business Trends")
    
    conn = get_connection()
    
    # Last 30 days daily sales
    daily_sales = pd.read_sql("""
        SELECT 
            date(order_date) as date,
            COUNT(*) as order_count,
            SUM(total_bill) as revenue,
            SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) as delivered_count
        FROM orders 
        WHERE user_id = ? AND order_date >= date('now', '-30 days')
        GROUP BY date(order_date)
        ORDER BY date
    """, conn, params=(user_id,))
    
    if daily_sales.empty:
        st.info("No sales data for the last 30 days")
        conn.close()
        return
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Daily Revenue Trend")
        fig = px.line(
            daily_sales,
            x='date',
            y='revenue',
            markers=True,
            title="Revenue Last 30 Days"
        )
        fig.update_layout(xaxis_title="Date", yaxis_title="Revenue (₹)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📦 Orders vs Deliveries")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=daily_sales['date'],
            y=daily_sales['order_count'],
            name='Orders',
            marker_color='blue'
        ))
        fig.add_trace(go.Bar(
            x=daily_sales['date'],
            y=daily_sales['delivered_count'],
            name='Delivered',
            marker_color='green'
        ))
        fig.update_layout(
            title="Daily Orders vs Deliveries",
            xaxis_title="Date",
            yaxis_title="Count",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly comparison
    st.subheader("📅 Monthly Performance")
    
    monthly_data = pd.read_sql("""
        SELECT 
            strftime('%Y-%m', order_date) as month,
            COUNT(*) as orders,
            SUM(total_bill) as revenue,
            AVG(total_bill) as avg_order_value
        FROM orders 
        WHERE user_id = ?
        GROUP BY strftime('%Y-%m', order_date)
        ORDER BY month DESC
        LIMIT 6
    """, conn, params=(user_id,))
    
    if not monthly_data.empty:
        fig = px.bar(
            monthly_data,
            x='month',
            y='revenue',
            color='orders',
            title="Last 6 Months Revenue",
            labels={'month': 'Month', 'revenue': 'Revenue (₹)', 'orders': 'Orders'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Status distribution
    st.subheader("📊 Order Status Distribution")
    status_data = pd.read_sql("""
        SELECT 
            status,
            COUNT(*) as count,
            SUM(total_bill) as total_value
        FROM orders 
        WHERE user_id = ?
        GROUP BY status
    """, conn, params=(user_id,))
    
    if not status_data.empty:
        fig = px.pie(
            status_data,
            values='count',
            names='status',
            hole=0.4,
            title="Orders by Status"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

def show_financial_overview(user_id):
    """Shopkeeper: Financial overview"""
    
    st.header("💰 Financial Overview")
    
    conn = get_connection()
    
    # Financial summary
    finance_data = pd.read_sql("""
        SELECT 
            SUM(total_bill) as total_revenue,
            SUM(advance) as total_advance,
            SUM(balance) as total_balance,
            SUM(CASE WHEN status = 'Delivered' THEN total_bill ELSE 0 END) as realized_revenue,
            COUNT(*) as total_orders
        FROM orders 
        WHERE user_id = ?
    """, conn, params=(user_id,))
    
    if finance_data.empty or finance_data['total_orders'][0] == 0:
        st.info("No financial data available")
        conn.close()
        return
    
    # Display financial metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = finance_data['total_revenue'][0] or 0
        st.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
    
    with col2:
        realized_revenue = finance_data['realized_revenue'][0] or 0
        st.metric("✅ Realized Revenue", f"₹{realized_revenue:,.0f}")
    
    with col3:
        total_advance = finance_data['total_advance'][0] or 0
        st.metric("💳 Total Advance", f"₹{total_advance:,.0f}")
    
    with col4:
        total_balance = finance_data['total_balance'][0] or 0
        st.metric("📋 Outstanding Balance", f"₹{total_balance:,.0f}")
    
    # Payment method analysis
    st.subheader("💳 Payment Analysis")
    
    payment_data = pd.read_sql("""
        SELECT 
            p.payment_method,
            COUNT(*) as transaction_count,
            SUM(p.amount) as total_amount
        FROM payments p
        JOIN orders o ON p.order_id = o.id
        WHERE o.user_id = ?
        GROUP BY p.payment_method
    """, conn, params=(user_id,))
    
    if not payment_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                payment_data,
                values='total_amount',
                names='payment_method',
                title="Revenue by Payment Method"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                payment_data,
                x='payment_method',
                y='transaction_count',
                color='total_amount',
                title="Transactions by Payment Method"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Monthly revenue trend
    st.subheader("📅 Monthly Revenue Trend")
    
    monthly_revenue = pd.read_sql("""
        SELECT 
            strftime('%Y-%m', order_date) as month,
            SUM(total_bill) as revenue,
            SUM(advance) as advance,
            SUM(balance) as balance
        FROM orders 
        WHERE user_id = ?
        GROUP BY strftime('%Y-%m', order_date)
        ORDER BY month DESC
        LIMIT 12
    """, conn, params=(user_id,))
    
    if not monthly_revenue.empty:
        fig = px.line(
            monthly_revenue.sort_values('month'),
            x='month',
            y=['revenue', 'advance', 'balance'],
            title="Monthly Financial Trends",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Amount (₹)",
            legend_title="Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

def show_customer_analytics(user_id):
    """Shopkeeper: Customer analytics"""
    
    st.header("👥 Customer Analytics")
    
    conn = get_connection()
    
    # Top customers by spending
    top_customers = pd.read_sql("""
        SELECT 
            c.name,
            c.phone,
            COUNT(o.id) as order_count,
            SUM(o.total_bill) as total_spent,
            AVG(o.total_bill) as avg_order_value,
            MAX(o.order_date) as last_order_date
        FROM clients c
        JOIN orders o ON c.id = o.client_id
        WHERE o.user_id = ?
        GROUP BY c.id, c.name, c.phone
        HAVING COUNT(o.id) > 0
        ORDER BY total_spent DESC
        LIMIT 10
    """, conn, params=(user_id,))
    
    if not top_customers.empty:
        st.subheader("🏆 Top 10 Customers by Spending")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig = px.bar(
                top_customers,
                x='name',
                y='total_spent',
                color='order_count',
                title="Customer Spending",
                labels={'name': 'Customer', 'total_spent': 'Total Spent (₹)', 'order_count': 'Orders'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Customer metrics
            total_customers = len(top_customers)
            avg_orders_per_customer = top_customers['order_count'].mean()
            avg_spending = top_customers['total_spent'].mean()
            
            st.metric("👥 Total Customers", total_customers)
            st.metric("📦 Avg Orders/Customer", f"{avg_orders_per_customer:.1f}")
            st.metric("💰 Avg Customer Value", f"₹{avg_spending:,.0f}")
        
        # Customer segmentation
        st.subheader("📊 Customer Segmentation")
        
        customer_segments = pd.read_sql("""
            SELECT 
                CASE 
                    WHEN order_count >= 10 THEN 'VIP (>10 orders)'
                    WHEN order_count >= 5 THEN 'Regular (5-9 orders)'
                    WHEN order_count >= 2 THEN 'Repeat (2-4 orders)'
                    ELSE 'New (1 order)'
                END as segment,
                COUNT(*) as customer_count,
                SUM(total_spent) as segment_revenue,
                AVG(total_spent) as avg_segment_value
            FROM (
                SELECT 
                    c.id,
                    COUNT(o.id) as order_count,
                    SUM(o.total_bill) as total_spent
                FROM clients c
                JOIN orders o ON c.id = o.client_id
                WHERE o.user_id = ?
                GROUP BY c.id
            ) customer_stats
            GROUP BY segment
            ORDER BY segment_revenue DESC
        """, conn, params=(user_id,))
        
        if not customer_segments.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    customer_segments,
                    values='segment_revenue',
                    names='segment',
                    title="Revenue by Customer Segment"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    customer_segments,
                    x='segment',
                    y='customer_count',
                    color='avg_segment_value',
                    title="Customers by Segment"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No customer data available")
    
    conn.close()

def show_client_insights(user_id):
    """Super Admin: Client insights across all shops"""
    
    st.header("👥 Platform Client Insights")
    
    conn = get_connection()
    
    # Top clients across platform
    platform_clients = pd.read_sql("""
        SELECT 
            c.name,
            c.phone,
            u.shop_name,
            COUNT(o.id) as order_count,
            SUM(o.total_bill) as total_spent,
            AVG(o.total_bill) as avg_order_value
        FROM clients c
        JOIN orders o ON c.id = o.client_id
        JOIN users u ON o.user_id = u.id
        WHERE u.role='admin'
        GROUP BY c.id, c.name, c.phone, u.shop_name
        HAVING COUNT(o.id) > 0
        ORDER BY total_spent DESC
        LIMIT 20
    """, conn)
    
    if not platform_clients.empty:
        st.subheader("🏆 Top 20 Clients Across Platform")
        st.dataframe(platform_clients, use_container_width=True)
    
    # Client distribution by shop
    client_distribution = pd.read_sql("""
        SELECT 
            u.shop_name,
            COUNT(DISTINCT c.id) as unique_clients,
            COUNT(o.id) as total_orders,
            AVG(o.total_bill) as avg_order_value
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        LEFT JOIN clients c ON o.client_id = c.id
        WHERE u.role='admin'
        GROUP BY u.id, u.shop_name
        HAVING COUNT(o.id) > 0
        ORDER BY unique_clients DESC
    """, conn)
    
    if not client_distribution.empty:
        st.subheader("📊 Client Distribution by Shop")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                client_distribution,
                x='shop_name',
                y='unique_clients',
                title="Unique Clients per Shop",
                labels={'shop_name': 'Shop', 'unique_clients': 'Unique Clients'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(
                client_distribution,
                x='unique_clients',
                y='avg_order_value',
                size='total_orders',
                color='shop_name',
                title="Clients vs Order Value"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    conn.close()
