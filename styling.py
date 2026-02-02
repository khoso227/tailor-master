import streamlit as st

def apply_styling(shop_name):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .main {{ background-color: #0f1116; font-family: 'Inter', sans-serif; }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }}
    
    .sidebar-header {{
        padding: 20px; text-align: center;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 15px; margin-bottom: 20px;
        border: 1px solid #334155;
    }}
    
    .user-badge {{
        background-color: #238636; color: white;
        padding: 2px 10px; border-radius: 20px;
        font-size: 10px; font-weight: bold;
    }}

    .company-tag {{
        position: fixed; bottom: 10px; left: 10px;
        font-size: 10px; color: #8b949e; letter-spacing: 1px;
    }}
    
    .shop-title {{
        color: #d4af37; font-size: 30px; font-weight: 800; text-align: center;
        margin-top: 20px; text-transform: uppercase;
    }}
    </style>
    
    <div class="company-tag">POWERED BY SAHIL & ARMAN IT CO</div>
    <div class="shop-title">{shop_name}</div>
    """, unsafe_allow_html=True)

def sidebar_header(name, role):
    st.sidebar.markdown(f"""
    <div class="sidebar-header">
        <div style="font-size: 24px;">👔</div>
        <div style="color: white; font-weight: 600; font-size: 16px;">{name}</div>
        <span class="user-badge">{role.upper()}</span>
    </div>
    """, unsafe_allow_html=True)
