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
import streamlit as st

def apply_styling(theme_choice, lang, wp_url=None):
    # Colors logic
    if theme_choice == "🌙 Night Mode":
        bg, side_bg, text, accent = "#0f172a", "#1e293b", "#ffffff", "#38bdf8"
        overlay = "rgba(15, 23, 42, 0.85)" # Dark overlay for readability
    else:
        bg, side_bg, text, accent = "#f8fafc", "#ffffff", "#1e293b", "#0284c7"
        overlay = "rgba(248, 250, 252, 0.9)" # Light overlay

    direction = "rtl" if lang == "Urdu" else "ltr"
    alignment = "right" if lang == "Urdu" else "left"

    # Background Image Styling
    bg_style = ""
    if wp_url:
        bg_style = f"""
        background-image: url('{wp_url}');
        background-size: cover;
        background-attachment: fixed;
        """

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
    * {{ font-family: 'Noto Sans Arabic', sans-serif; direction: {direction}; }}

    .stApp {{
        {bg_style}
        background-color: {bg};
    }}

    /* Main Content Overlay for readability on Wallpapers */
    .main .block-container {{
        background: {overlay};
        border-radius: 20px;
        padding: 40px !important;
        margin-top: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }}

    [data-testid="stSidebar"] {{
        background-color: {side_bg} !important;
        border-right: 2px solid {accent} !important;
    }}
    
    [data-testid="stSidebar"] * {{ color: {text} !important; font-weight: 700 !important; }}

    div[data-testid="stMetric"] {{
        background: {side_bg}; border: 2px solid {accent};
        border-radius: 12px; padding: 15px; text-align: center;
    }}

    input, textarea, select {{
        background-color: {side_bg} !important; color: {text} !important;
        border: 1px solid {accent} !important; text-align: {alignment};
    }}

    h1, h2, h3, h4 {{ color: {accent} !important; font-weight: 800; }}
    </style>
    """, unsafe_allow_html=True)
