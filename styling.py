import streamlit as st

def apply_styling(theme='Dark'):
    # Navy Professional Palette
    bg = "#0f172a" if theme == 'Dark' else "#f8fafc"
    card = "#1e293b" if theme == 'Dark' else "#ffffff"
    text = "#f1f5f9" if theme == 'Dark' else "#1e293b"
    accent = "#38bdf8"
    
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {text}; }}
    [data-testid="stSidebar"] {{ background-color: #020617; border-right: 1px solid #334155; }}
    
    /* Field Labels visibility */
    label {{ color: {accent} !important; font-weight: bold !important; font-size: 14px !important; }}
    
    /* Inputs Styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {{
        background-color: #0f172a !important;
        color: white !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }}
    
    /* Section Headers */
    h3, h4 {{ color: white !important; border-bottom: 2px solid {accent}; padding-bottom: 5px; }}
    
    /* Metric Boxes */
    div[data-testid="stMetric"] {{
        background-color: {card};
        border-left: 5px solid {accent};
        padding: 10px;
        border-radius: 10px;
    }}
    </style>
    <div style="text-align:center; color:#475569; font-size:10px; font-weight:bold; letter-spacing:2px; padding:10px;">
        SAHIL & ARMAN IT SOLUTIONS | VERSION 10.0
    </div>
    """, unsafe_allow_html=True)
