import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

def show_global_stats():
    conn = get_connection()
    st.header("🌍 Global Revenue Overview")
    df = pd.read_sql("SELECT shop_name, fee_status FROM users WHERE role='admin'", conn)
    sales = pd.read_sql("SELECT total, remaining FROM clients", conn)
    
    c1, c2 = st.columns(2)
    c1.metric("Total Partners", len(df))
    c2.metric("Total Business Vol.", f"Rs.{sales['total'].sum():,.0f}")
    st.dataframe(df, use_container_width=True)

def show_shop_reports(user_id):
    conn = get_connection()
    st.header("📊 My Business Reports")
    df = pd.read_sql(f"SELECT order_date, total, remaining, pay_method FROM clients WHERE user_id={user_id}", conn)
    
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.write("📈 Sales Progress")
            fig = px.area(df, x='order_date', y='total', color_discrete_sequence=['#38bdf8'])
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.write("💳 Payment Methods Used")
            pay_fig = px.pie(df, names='pay_method', hole=.4)
            st.plotly_chart(pay_fig, use_container_width=True)
            
        st.subheader("💰 Recent History")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Pehle kuch orders add karein taaki reports generate ho sakein.")
