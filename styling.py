import streamlit as st

def apply_styling(shop_name):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    .main {{ background-color: #0f1116; font-family: 'Poppins', sans-serif; }}
    
    /* Sahil & Arman Logo Header */
    .company-header {{
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; font-size: 14px; font-weight: bold; letter-spacing: 2px;
    }}
    
    .shop-title {{
        color: #d4af37; font-size: 40px; font-weight: 800; text-align: center;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5); margin-bottom: 20px;
    }}

    .stMetric {{
        background: rgba(255, 255, 255, 0.05); padding: 15px;
        border-radius: 12px; border: 1px solid #3a7bd5;
    }}

    .whatsapp-btn {{
        background-color: #25d366; color: white !important; padding: 10px 20px;
        border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;
    }}
    </style>
    
    <div class="company-header">POWERED BY SAHIL & ARMAN IT COMPANY</div>
    <div class="shop-title">{shop_name}</div>
    """, unsafe_allow_html=True)