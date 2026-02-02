import streamlit as st

def apply_styling(theme='Dark'):
    # Professional Navy & Slate Colors
    bg = "#1e293b" if theme == 'Dark' else "#f8fafc"
    sidebar = "#0f172a" if theme == 'Dark' else "#ffffff"
    card = "#334155" if theme == 'Dark' else "#ffffff"
    text = "#f1f5f9" if theme == 'Dark' else "#0f172a"
    accent = "#38bdf8" # Sky Blue accent
    
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {text}; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar}; border-right: 1px solid #475569; }}
    
    /* Metrics Box - Navy Theme */
    div[data-testid="stMetric"] {{
        background-color: {card};
        border: 2px solid {accent};
        border-radius: 12px;
        padding: 15px;
    }}
    
    /* Input Fields Visibility */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {{
        background-color: {sidebar} !important;
        color: white !important;
        border: 1px solid {accent} !important;
    }}

    h1, h2, h3 {{ color: {accent} !important; font-weight: 800; }}
    
    .company-header {{
        text-align: center; color: #94a3b8; font-size: 11px;
        font-weight: bold; letter-spacing: 2px; margin-bottom: 20px;
    }}
    </style>
    <div class="company-header">SAHIL & ARMAN IT SOLUTIONS</div>
    """, unsafe_allow_html=True)
