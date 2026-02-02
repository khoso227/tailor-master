import streamlit as st

def apply_styling(theme='Dark'):
    bg = "#0f172a" if theme == 'Dark' else "#f8fafc"
    text = "#f1f5f9" if theme == 'Dark' else "#1e293b"
    card = "#1e293b" if theme == 'Dark' else "#ffffff"
    border = "#334155" if theme == 'Dark' else "#e2e8f0"

    st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {text}; }}
    [data-testid="stSidebar"] {{ background-color: {card}; border-right: 1px solid {border}; }}
    .stMetric {{ background-color: {card}; border: 1px solid {border}; padding: 15px; border-radius: 10px; }}
    .stDataFrame {{ background-color: {card}; border-radius: 10px; }}
    h1, h2, h3, p {{ color: {text} !important; }}
    
    .company-header {{
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; text-align: center; font-size: 12px; letter-spacing: 2px;
    }}
    </style>
    <div class="company-header">SAHIL & ARMAN IT SOLUTIONS</div>
    """, unsafe_allow_html=True)
