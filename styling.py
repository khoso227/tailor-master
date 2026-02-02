import streamlit as st

def apply_styling(theme='Dark'):
    # Professional Navy & Sky Blue Theme
    navy_bg = "#0f172a" 
    sidebar_navy = "#1e293b"
    text_white = "#ffffff"
    sky_blue = "#38bdf8"
    
    st.markdown(f"""
    <style>
    /* Force Sidebar Background & Text */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_navy} !important;
        border-right: 2px solid {sky_blue} !important;
    }}
    
    /* Force Sidebar Text, Icons and Labels to White */
    [data-testid="stSidebar"] * {{
        color: {text_white} !important;
        font-weight: 600 !important;
    }}

    /* Active Menu Selection Highlight */
    [data-testid="stSidebarNavItems"] .st-emotion-cache-6qob1r {{
        background-color: {sky_blue} !important;
        color: #000000 !important;
        border-radius: 8px;
    }}

    /* Main App Background */
    .stApp {{
        background-color: {navy_bg};
        color: {text_white};
    }}

    /* Metrics (The 3 boxes on top) */
    div[data-testid="stMetric"] {{
        background-color: {sidebar_navy};
        border: 2px solid {sky_blue};
        border-radius: 12px;
        padding: 15px;
    }}

    /* Inputs Visibility */
    input, textarea, select {{
        background-color: #334155 !important;
        color: white !important;
        border: 1px solid {sky_blue} !important;
    }}

    h1, h2, h3, h4 {{ color: {sky_blue} !important; }}
    </style>
    """, unsafe_allow_html=True)
