import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

# =====================================================
# SUPER ADMIN : GLOBAL SYSTEM ANALYTICS
# =====================================================
def show_global_stats(conn=None):
    """
    Super Admin View:
    - Total Shops
    - Paid / Pending Shops
    - Total Platform Business
    - Shop Contact & Expiry Details
    """

    st.header("🌍 Global System Overview")

    # Connection auto-handle
    if conn is None:
        conn = get_connection()

    # -------- Summary Metrics --------
    stats = pd.read_sql("""
        SELECT
            COUNT(*) total_shops,
            SUM(CASE WHEN fee_status='paid' THEN 1 ELSE 0 END) paid_shops,
            SUM(CASE WHEN fee_status!='paid' THEN 1 ELSE 0 END) pending_shops
        FROM users
        WHERE role='admin'
    """, conn)

    total_rev = pd.read_sql(
        "SELECT SUM(total) t FROM clients",
        conn
    ).iloc[0, 0] or 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏪 Partner Shops", stats['total_shops'][0])
    c2.metric("✅ Paid Shops", stats['paid_shops'][0])
    c3.metric("⚠ Pending Shops", stats['pending_shops'][0])
    c4.metric("💰 Platform Business", f"Rs.{total_rev:,.0f}")

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
            expiry_date,
            status
        FROM users
        WHERE role='admin'
        ORDER BY shop_name
    """, conn)

    if shops_df.empty:
        st.info("Abhi tak koi shop register nahi hui.")
    else:
        st.dataframe(shops_df, use_container_width=True)


# =====================================================
# SHOPKEEPER : BUSINESS REPORTS & CHARTS
# =====================================================
def show_shop_reports(conn, user_id):
    """
    Shopkeeper View:
    - Sales Progress Chart
    - Payment Method Chart
    - Recent Transactions Table
    """

    st.header("📊 Business Analytics & Reports")

    df = pd.read_sql("""
        SELECT
            order_date,
            total,
            advance,
            remaining,
            pay_method,
            status
        FROM clients
        WHERE user_id=?
        ORDER BY order_date
    """, conn, params=(user_id,))

    if df.empty:
        st.info("📊 Reports ke liye pehle orders add karein.")
        return

    # -------- Charts --------
    col1, col2 = st.columns(2)

    with col1:
        st.write("📈 Sales Progress")
        fig1 = px.area(
            df,
            x="order_date",
            y="total",
            labels={"order_date": "Date", "total": "Amount"}
        )
        fig1.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.write("💳 Payment Methods")
        fig2 = px.pie(
            df,
            names="pay_method",
            hole=0.4
        )
        fig2.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    # -------- Recent Transactions --------
    st.markdown("---")
    st.subheader("🧾 Recent Transactions")
    st.dataframe(
        df.tail(10),
        use_container_width=True
    )
