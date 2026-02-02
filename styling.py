import streamlit as st

def apply_styling(theme='Dark'):
    # Navy Blue Theme Colors
    bg = "#1e293b" if theme == 'Dark' else "#f8fafc"
    sidebar_bg = "#0f172a" if theme == 'Dark' else "#ffffff"
    text = "#f1f5f9" if theme == 'Dark' else "#0f172a"
    accent = "#38bdf8" # Bright Sky Blue
    
    st.markdown(f"""
    <style>
    /* Main Background */
    .stApp {{ background-color: {bg}; color: {text}; }}
    
    /* Sidebar Text & Icons Visibility */
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg}; border-right: 1px solid #334155; }}
    [data-testid="stSidebar"] * {{ color: {text} !important; font-weight: 600 !important; font-size: 15px; }}
    
    /* Radio Button (Menu) Visibility */
    div[data-testid="stSidebarNav"] li {{ background-color: transparent; }}
    .st-emotion-cache-6qob1r {{ background-color: {accent} !important; color: black !important; }}

    /* Cards/Metrics */
    div[data-testid="stMetric"] {{
        background-color: {sidebar_bg};
        border: 2px solid {accent};
        border-radius: 12px;
        padding: 15px;
    }}
    
    h1, h2, h3 {{ color: {accent} !important; font-weight: 800; }}
    
    /* Error Message Fix */
    .stAlert {{ background-color: #1e293b; border: 1px solid {accent}; color: white; }}
    </style>
    <div style="text-align:center; color:#64748b; font-size:10px; font-weight:bold; letter-spacing:2px;">
        SAHIL & ARMAN IT SOLUTIONS
    </div>
    """, unsafe_allow_html=True)
