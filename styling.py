import streamlit as st

def apply_styling(theme_choice, lang):
    # Colors
    if theme_choice == "🌙 Night Mode":
        bg, side_bg, text, accent = "#0f172a", "#1e293b", "#ffffff", "#38bdf8"
    else:
        bg, side_bg, text, accent = "#f8fafc", "#ffffff", "#1e293b", "#0284c7"

    # RTL (Right to Left) logic for Urdu
    alignment = "right" if lang == "Urdu" else "left"
    direction = "rtl" if lang == "Urdu" else "ltr"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
    
    * {{ font-family: 'Noto Sans Arabic', sans-serif; direction: {direction}; }}
    
    .stApp {{ background-color: {bg} !important; color: {text} !important; text-align: {alignment}; }}
    
    [data-testid="stSidebar"] {{
        background-color: {side_bg} !important;
        border-right: 2px solid {accent} !important;
        text-align: left; /* Sidebar stays left for standard UI */
    }}
    
    [data-testid="stSidebar"] * {{ color: {text} !important; font-weight: 700 !important; }}

    div[data-testid="stMetric"] {{
        background-color: {side_bg}; border: 2px solid {accent};
        border-radius: 12px; padding: 15px; text-align: center;
    }}

    input, textarea, select {{
        background-color: {side_bg} !important; color: {text} !important;
        border: 1px solid {accent} !important; text-align: {alignment};
    }}

    h1, h2, h3, h4 {{ color: {accent} !important; }}
    </style>
    """, unsafe_allow_html=True)
