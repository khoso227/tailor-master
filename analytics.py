import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from database import get_connection

def show_global_stats():
    conn = get_connection()
    st.header("🌍 Global Business Intelligence")
    
    # 1. Platform Metrics
    shops = pd.read_sql("SELECT shop_name, fee_status, id FROM users WHERE role='admin'", conn)
    clients = pd.read_sql("SELECT total, remaining, order_date FROM clients", conn)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Partners", len(shops))
    col2.metric("Gross Platform Vol.", f"Rs.{clients['total'].sum():,.0f}")
    col3.metric("Total Outstanding", f"Rs.{clients['remaining'].sum():,.0f}")

    # 2. Daily Income per Shop (The part you requested)
    st.subheader("📅 Today's Income Analysis (Per Shop)")
    today = date.today().strftime('%Y-%m-%d')
    query = f"""
        SELECT u.shop_name, SUM(c.total) as daily_revenue, u.fee_status 
        FROM users u 
        LEFT JOIN clients c ON u.id = c.user_id 
        WHERE c.order_date = '{today}' OR c.order_date IS NULL
        GROUP BY u.shop_name
    """
    daily_df = pd.read_sql(query, conn)
    st.dataframe(daily_df.fillna(0), use_container_width=True)

    # 3. Shop Fee Management
    st.subheader("💳 License Fee Management")
    st.table(shops[['shop_name', 'fee_status']])

def show_shop_reports(user_id):
    conn = get_connection()
    st.header("📊 Detailed Sales Analysis")
    df = pd.read_sql(f"SELECT order_date, total, remaining FROM clients WHERE user_id={user_id}", conn)
    
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(df, x='order_date', y='total', title="Revenue by Date", color_discrete_sequence=['#38bdf8'])
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.pie(values=[df['total'].sum(), df['remaining'].sum()], names=['Earned', 'Pending'], hole=.4)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No sales data available yet to generate reports.")
