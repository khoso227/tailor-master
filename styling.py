import streamlit as st

def apply_styling(theme='Dark'):
    # Professional Navy Theme
    navy_bg = "#0f172a" 
    sidebar_bg = "#1e293b"
    sky_blue = "#38bdf8"
    text_white = "#ffffff"
    
    st.markdown(f"""
    <style>
    /* 1. Sidebar Background & Text */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 2px solid {sky_blue} !important;
    }}
    
    /* 2. All Sidebar Text & Icons to Bright White */
    [data-testid="stSidebar"] * {{
        color: {text_white} !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }}

    /* 3. Main Screen Background */
    .stApp {{ background-color: {navy_bg}; color: {text_white}; }}

    /* 4. Logout Button Styling (Red & Visible) */
    .stButton>button {{
        background-color: #ef4444 !important; /* Red */
        color: white !important;
        border-radius: 8px !important;
        width: 100% !important;
        font-weight: bold !important;
    }}
    
    /* 5. Menu Selection Highlight */
    .st-emotion-cache-6qob1r {{
        background-color: {sky_blue} !important;
        color: #000000 !important;
    }}

    /* 6. Inputs & Text Areas */
    input, textarea, select {{
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid {sky_blue} !important;
    }}

    h1, h2, h3, h4 {{ color: {sky_blue} !important; font-weight: 800; }}
    </style>
    """, unsafe_allow_html=True)
