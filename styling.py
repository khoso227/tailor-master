import streamlit as st

def apply_styling(theme='Dark'):
    # Professional Colors (Not Pitch Black)
    main_bg = "#1e293b" if theme == 'Dark' else "#f1f5f9"
    sidebar_bg = "#0f172a" if theme == 'Dark' else "#ffffff"
    text_color = "#f8fafc" if theme == 'Dark' else "#1e293b"
    card_bg = "#334155" if theme == 'Dark' else "#ffffff"
    
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {main_bg}; color: {text_color}; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg}; border-right: 1px solid #475569; }}
        .stMetric {{ background-color: {card_bg}; border: 1px solid #475569; padding: 20px; border-radius: 12px; }}
        div.stButton > button {{ 
            background-color: #38bdf8; color: white; border-radius: 8px; 
            font-weight: bold; width: 100%; border: none; height: 45px;
        }}
        h1, h2, h3, label {{ color: {text_color} !important; }}
        .stDataFrame {{ border-radius: 10px; overflow: hidden; border: 1px solid #475569; }}
        </style>
        <div style="text-align:center; color:#94a3b8; font-size:10px; font-weight:bold; letter-spacing:2px; margin-bottom:10px;">
            POWERED BY SAHIL & ARMAN IT SOLUTIONS
        </div>
    """, unsafe_allow_html=True)
