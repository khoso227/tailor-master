import streamlit as st

def apply_styling(theme='Dark'):
    # Colors optimized for visibility
    bg = "#0e1117" if theme == 'Dark' else "#f0f2f6"
    card = "#1a1c24" if theme == 'Dark' else "#ffffff"
    text = "#ffffff" if theme == 'Dark' else "#000000"
    border = "#30363d" if theme == 'Dark' else "#d1d5db"

    st.markdown(f"""
    <style>
    /* Global Styles */
    .stApp {{ background-color: {bg}; color: {text}; }}
    [data-testid="stSidebar"] {{ background-color: {card}; border-right: 2px solid {border}; }}
    
    /* chamakdar headers */
    h1, h2, h3 {{ color: #38bdf8 !important; font-weight: 800 !important; }}
    label {{ color: {text} !important; font-size: 16px !important; font-weight: 600 !important; }}
    
    /* Metrics Box */
    [data-testid="stMetric"] {{
        background-color: {card};
        border: 2px solid #38bdf8;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    [data-testid="stMetricValue"] {{ color: #22c55e !important; font-size: 28px !important; }}
    
    /* Dataframe Header Visibility */
    .stDataFrame thead tr th {{ background-color: #38bdf8 !important; color: black !important; }}
    
    .company-tag {{
        text-align: center; color: #94a3b8; font-size: 12px; font-weight: bold;
        letter-spacing: 3px; margin-bottom: 20px; border-bottom: 1px solid #334155;
    }}
    </style>
    <div class="company-tag">SAHIL & ARMAN IT SOLUTIONS</div>
    """, unsafe_allow_html=True)
