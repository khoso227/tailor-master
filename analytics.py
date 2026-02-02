import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

def show_shop_reports(user_id):
    st.header("📊 Business Performance")
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM clients WHERE user_id={user_id}", conn)
    
    if df.empty:
        st.warning("Reports ke liye pehle orders add karein.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.write("💰 Sales Trend")
        fig = px.area(df, x='order_date', y='total', color_discrete_sequence=['#38bdf8'])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.write("💳 Payment Breakdown")
        fig2 = px.pie(df, names='pay_method', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
