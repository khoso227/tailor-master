import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

def show_reports():
    st.header("📊 Business Growth Analytics")
    conn = get_connection()
    df = pd.read_sql("SELECT order_date, total, remaining FROM clients", conn)
    
    if not df.empty:
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # Sales Chart
        st.subheader("Sales Trend (Revenue)")
        fig = px.area(df, x='order_date', y='total', title="Daily Revenue Flow", color_discrete_sequence=['#d4af37'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Recovery Chart
        st.subheader("Recovery vs Pending")
        fig2 = px.pie(values=[df['total'].sum(), df['remaining'].sum()], 
                      names=['Total Revenue', 'Pending Recovery'],
                      color_discrete_sequence=['#2ecc71', '#e74c3c'])
        st.plotly_chart(fig2)
    else:
        st.info("Analytics dikhane ke liye pehle data add karein.")
