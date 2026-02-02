import streamlit as st
import pandas as pd
from database import get_connection

def show_global_stats():
    conn = get_connection()
    st.header("🌍 Platform Overview")
    
    # Platform ki total kamai (Summary)
    total_sales = pd.read_sql("SELECT SUM(total) as t FROM clients", conn).iloc[0,0] or 0
    total_shops = pd.read_sql("SELECT COUNT(*) as c FROM users WHERE role='admin'", conn).iloc[0,0]
    
    c1, c2 = st.columns(2)
    c1.metric("Total Registered Shops", total_shops)
    c2.metric("Total Business Volume", f"Rs.{total_sales:,.0f}")

    st.markdown("---")
    st.subheader("💳 Shop Fee Status")
    shops = pd.read_sql("SELECT id, shop_name, email, fee_status FROM users WHERE role='admin'", conn)
    st.table(shops)

def show_shop_reports(user_id):
    conn = get_connection()
    st.header("📊 My Performance")
    df = pd.read_sql(f"SELECT order_date, total FROM clients WHERE user_id={user_id}", conn)
    if not df.empty:
        st.line_chart(df.set_index('order_date'))
    else:
        st.info("Start adding orders to see charts!")
