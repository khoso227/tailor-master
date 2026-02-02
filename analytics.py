import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

def show_global_stats():
    """Super Admin View: Poore system ki malumat aur shopkeepers ki details"""
    st.header("🌍 Global System Overview")
    conn = get_connection()
    
    # --- 1. Summary Metrics ---
    # Gin-na ke total kitni dukanen hain
    total_shops = pd.read_sql("SELECT COUNT(*) as c FROM users WHERE role='admin'", conn).iloc[0,0]
    # Poore platform par kitne ka business hua
    total_rev = pd.read_sql("SELECT SUM(total) as t FROM clients", conn).iloc[0,0] or 0
    
    c1, c2 = st.columns(2)
    c1.metric("Registered Partner Shops", total_shops)
    c2.metric("Total Platform Business", f"Rs.{total_rev:,.0f}")

    st.markdown("---")
    
    # --- 2. Active Shops Table with Contact & Expiry ---
    st.subheader("👥 Active Shops & Contact Details")
    # Yeh query shopkeeper ka Mobile, Email, Expiry Date aur Status sab dikhayegi
    query = """
        SELECT id, shop_name, phone, email, fee_status, expiry_date, status 
        FROM users 
        WHERE role='admin'
    """
    shops_df = pd.read_sql(query, conn)
    
    if not shops_df.empty:
        # Dataframe use karne se admin asani se search aur filter kar sakta hai
        st.dataframe(shops_df, use_container_width=True)
    else:
        st.info("Abhi tak koi dukan register nahi hui.")

def show_shop_reports(user_id):
    """Shopkeeper View: Dukan-dar ke liye karobar ke analytics aur charts"""
    st.header("📊 Business Analytics & Reports")
    conn = get_connection()
    
    # Data nikalna charts banane ke liye
    df = pd.read_sql(f"SELECT order_date, total, remaining, pay_method FROM clients WHERE user_id={user_id}", conn)
    
    if df.empty:
        st.info("📊 Reports banane ke liye pehle kuch orders add karein.")
        return

    # --- 1. Visual Charts ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("📈 **Sales Progress (Karobar ki Raftar)**")
        # Area chart se pata chalta hai ke kis din kitni sale hui
        fig = px.area(df, x='order_date', y='total', 
                     color_discrete_sequence=['#38bdf8'],
                     labels={'order_date': 'Date', 'total': 'Amount'})
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("💳 **Payment Methods (Adaigi ka Tariqa)**")
        # Pie chart se pata chalta hai ke Cash zyada aa raha hai ya Online
        fig2 = px.pie(df, names='pay_method', hole=0.4,
                      color_discrete_sequence=px.colors.sequential.RdBu)
        fig2.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    # --- 2. Detailed Summary Table ---
    st.markdown("---")
    st.subheader("📝 Recent Transactions Summary")
    st.dataframe(df.tail(10), use_container_width=True)
