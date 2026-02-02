import streamlit as st
import pandas as pd
import sqlite3
import random
import datetime
import urllib.parse
from services import analytics

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Tailor Master Pro",
    page_icon="🧵",
    layout="wide"
)

conn = sqlite3.connect("tailor_master.db", check_same_thread=False)

# ---------------- WALLPAPER SYSTEM ----------------
def set_wallpaper():
    hour = datetime.datetime.now().hour

    if 6 <= hour < 18:
        wp = f"assets/wallpapers/day{random.randint(1,10)}.jpg"
    else:
        wp = f"assets/wallpapers/night{random.randint(1,10)}.jpg"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("{wp}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_wallpaper()

# ---------------- AUTH GUARD ----------------
if not st.session_state.get("auth"):
    st.warning("Please login first")
    st.stop()

# ---------------- SUPER ADMIN ----------------
if st.session_state.u_role == "super_admin":

    st.sidebar.title("🛡 SUPER ADMIN")
    menu = st.sidebar.radio(
        "ADMIN PANEL",
        ["Partner Payments", "Global Stats"]
    )

    if menu == "Partner Payments":
        st.header("💳 Partner Management")

        shops = pd.read_sql(
            "SELECT id, shop_name, phone, fee_status FROM users WHERE role='admin'",
            conn
        )
        st.dataframe(shops, use_container_width=True)

        shop_map = dict(zip(shops['id'], shops['shop_name']))
        sid = st.selectbox(
            "Select Shop",
            shop_map.keys(),
            format_func=lambda x: shop_map[x]
        )

        if st.button("📲 Send WhatsApp Payment Reminder"):
            s_data = conn.execute(
                "SELECT shop_name, phone FROM users WHERE id=?",
                (sid,)
            ).fetchone()

            if s_data:
                msg = f"Dear {s_data[0]}, your Tailor Master Pro subscription payment is pending."
                url = f"https://wa.me/{s_data[1]}?text={urllib.parse.quote(msg)}"
                st.markdown(f"[👉 Click to Send Reminder]({url})")
            else:
                st.error("Invalid shop selected")

    elif menu == "Global Stats":
        analytics.show_global_stats(conn)

# ---------------- SHOPKEEPER ----------------
else:
    st.sidebar.title("🏪 SHOP PANEL")

    menu = st.sidebar.radio(
        "MENU",
        ["Dashboard", "New Order", "Reports", "Security"]
    )

    # -------- Fee Lock --------
    fee_status = conn.execute(
        "SELECT fee_status FROM users WHERE id=?",
        (st.session_state.u_id,)
    ).fetchone()[0]

    if fee_status != "paid":
        st.error("⚠ Subscription pending. Please contact Sahil & Arman IT Company.")
        st.stop()

    # -------- Dashboard --------
    if menu == "Dashboard":
        st.header(f"📊 Dashboard — {st.session_state.u_shop}")

        stats = pd.read_sql(
            """
            SELECT 
                SUM(total) t,
                SUM(advance) a,
                SUM(remaining) r
            FROM clients
            WHERE user_id=?
            """,
            conn,
            params=(st.session_state.u_id,)
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Sales", f"Rs. {stats['t'].iloc[0] or 0:,.0f}")
        c2.metric("✅ Received", f"Rs. {stats['a'].iloc[0] or 0:,.0f}")
        c3.metric("⏳ Outstanding", f"Rs. {stats['r'].iloc[0] or 0:,.0f}")

        df = pd.read_sql(
            """
            SELECT name, phone, remaining, status
            FROM clients
            WHERE user_id=?
            ORDER BY remaining DESC
            """,
            conn,
            params=(st.session_state.u_id,)
        )
        st.dataframe(df, use_container_width=True)

    # -------- New Order --------
    elif menu == "New Order":
        add_order_ui(st.session_state.u_id)

    # -------- Reports --------
    elif menu == "Reports":
        analytics.show_shop_reports(conn, st.session_state.u_id)

    # -------- Security --------
    elif menu == "Security":
        st.header("🔐 Account Security")

        u_data = conn.execute(
            """
            SELECT shop_name, email, phone, fee_status
            FROM users WHERE id=?
            """,
            (st.session_state.u_id,)
        ).fetchone()

        st.markdown(
            f"""
            **Shop:** {u_data[0]}  
            **Email:** {u_data[1]}  
            **Phone:** {u_data[2]}  
            **Subscription:** {u_data[3]}
            """
        )

# ---------------- LOGOUT ----------------
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

# ---------------- FOOTER ----------------
st.markdown(
    "<center><small>Powered by <b>Sahil & Arman IT Company</b></small></center>",
    unsafe_allow_html=True
)
