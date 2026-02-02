import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

def show_global_stats():
    conn = get_connection()
    st.header("🌍 Platform Global Analytics")
    
    # Global Metrics
    data = pd.read_sql("SELECT shop_name, fee_status, id FROM users WHERE role='admin'", conn)
    clients = pd.read_sql("SELECT total, remaining, order_date FROM clients", conn)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Shops", len(data))
    c2.metric("Total Platform Revenue", f"Rs.{clients['total'].sum():,.0f}")
    c3.metric("Total Outstanding", f"Rs.{clients['remaining'].sum():,.0f}")

    st.subheader("💳 Shop Fee Status")
    st.dataframe(data[['shop_name', 'fee_status']], use_container_width=True)

def show_shop_reports(user_id):
    conn = get_connection()
    df = pd.read_sql(f"SELECT order_date, total, remaining FROM clients WHERE user_id={user_id}", conn)
    
    if not df.empty:
        st.subheader("📈 My Sales Growth")
        fig = px.line(df, x='order_date', y='total', title="Revenue over time")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("💰 Financial Balance")
        fig2 = px.pie(values=[df['total'].sum() - df['remaining'].sum(), df['remaining'].sum()], 
                      names=['Received', 'Pending'], hole=.4)
        st.plotly_chart(fig2)
    else:
        st.info("No data yet to show reports.")
