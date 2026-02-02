import streamlit as st

def apply_styling(theme_choice):
    if theme_choice == "🌙 Night Mode":
        bg = "#0f172a"      # Deep Navy
        side_bg = "#1e293b" # Lighter Navy for Sidebar
        text = "#ffffff"    # Pure White text
        accent = "#38bdf8"  # Sky Blue headings
    else:
        bg = "#f8fafc"      # Soft White
        side_bg = "#ffffff" # Pure White Sidebar
        text = "#1e293b"    # Dark Navy text
        accent = "#0284c7"  # Deep Blue headings

    st.markdown(f"""
    <style>
    /* Main App Styling */
    .stApp {{ background-color: {bg} !important; color: {text} !important; }}
    
    /* Sidebar Styling - Chamkadar and Clear */
    [data-testid="stSidebar"] {{
        background-color: {side_bg} !important;
        border-right: 2px solid {accent} !important;
    }}
    
    /* Sidebar Text visibility */
    [data-testid="stSidebar"] * {{
        color: {text} !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }}

    /* Metrics (The 3 boxes) */
    div[data-testid="stMetric"] {{
        background-color: {side_bg};
        border: 2px solid {accent};
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

    /* Input Fields */
    input, textarea, select {{
        background-color: {side_bg} !important;
        color: {text} !important;
        border: 1px solid {accent} !important;
    }}

    h1, h2, h3, h4 {{ color: {accent} !important; font-weight: 800; }}
    
    /* Buttons */
    .stButton>button {{
        background-color: {accent} !important;
        color: white !important;
        font-weight: bold !important;
    }}
    </style>
    """, unsafe_allow_html=True)
