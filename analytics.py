import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

def show_global_stats():
    # Super Admin Dashboard
    st.header("🌍 Global System Overview")
    conn = get_connection()
    
    # Summary Metrics
    total_shops = pd.read_sql("SELECT COUNT(*) as c FROM users WHERE role='admin'", conn).iloc[0,0]
    total_revenue = pd.read_sql("SELECT SUM(total) as t FROM clients", conn).iloc[0,0] or 0
    
    c1, c2 = st.columns(2)
    c1.metric("Registered Partner Shops", total_shops)
    c2.metric("Total Platform Business", f"Rs.{total_revenue:,.0f}")

    st.markdown("---")
    st.subheader("👥 Active Shops List")
    shops_df = pd.read_sql("SELECT id, shop_name, email, fee_status FROM users WHERE role='admin'", conn)
    st.table(shops_df)

def show_shop_reports(user_id):
    # Shopkeeper Dashboard
    st.header("📊 Your Business Reports")
    conn = get_connection()
    df = pd.read_sql(f"SELECT order_date, total, remaining, pay_method FROM clients WHERE user_id={user_id}", conn)
    
    if df.empty:
        st.info("Report banane ke liye pehle naye orders add karein.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.write("📈 Sales Progress")
        fig = px.area(df, x='order_date', y='total', color_discrete_sequence=['#38bdf8'])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.write("💳 Payment Methods")
        fig2 = px.pie(df, names='pay_method', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
