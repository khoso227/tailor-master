import streamlit as st
import random

def apply_styling():
    """Apply Navy Blue Professional theme with 30 Wallpapers support"""
    
    # Initialize session states for theme and wallpaper
    if 'theme' not in st.session_state:
        st.session_state.theme = 'night'
    if 'wallpaper' not in st.session_state:
        st.session_state.wallpaper = None

    # 15 Day Wallpapers
    DAY_WALLPAPERS = [
        "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=1600",
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1600",
        "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1600",
        "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?w=1600",
        "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=1600",
        "https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=1600",
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600",
        "https://images.unsplash.com/photo-1476820865390-c52aeebb9891?w=1600",
        "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=1600",
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1600",
        "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1600",
        "https://images.unsplash.com/photo-1488866022504-f2584929ca5f?w=1600",
        "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=1600",
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600",
        "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=1600"
    ]
    
    # 15 Night Wallpapers (Tailoring & Dark Texture)
    NIGHT_WALLPAPERS = [
        "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=1600",
        "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1600",
        "https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?w=1600",
        "https://images.unsplash.com/photo-1465101162946-4377e57745c3?w=1600",
        "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1600",
        "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1600",
        "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1600",
        "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?w=1600",
        "https://images.unsplash.com/photo-1475274047050-1d0c0975c63e?w=1600",
        "https://images.unsplash.com/photo-1476820865390-c52aeebb9891?w=1600",
        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1600",
        "https://images.unsplash.com/photo-1533563909201-c6a05d8b4c3b?w=1600",
        "https://images.unsplash.com/photo-1512403754473-27835f7b9984?w=1600",
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1600",
        "https://images.unsplash.com/photo-1562157873-818bc0726f68?w=1600"
    ]

    # Sidebar Theme Control
    with st.sidebar:
        st.markdown("---")
        st.subheader("🎨 Theme Settings")
        col1, col2 = st.columns(2)
        if col1.button("☀️ Day Mode"):
            st.session_state.theme = 'day'
            st.session_state.wallpaper = random.choice(DAY_WALLPAPERS)
            st.rerun()
        if col2.button("🌙 Night Mode"):
            st.session_state.theme = 'night'
            st.session_state.wallpaper = random.choice(NIGHT_WALLPAPERS)
            st.rerun()
        
        if st.button("🔄 Shuffle Wallpaper"):
            st.session_state.wallpaper = random.choice(DAY_WALLPAPERS if st.session_state.theme == 'day' else NIGHT_WALLPAPERS)
            st.rerun()

    # Default wallpaper if none selected
    if st.session_state.wallpaper is None:
        st.session_state.wallpaper = NIGHT_WALLPAPERS[0]

    # Theme Variable Colors (Professional Navy Blue)
    if st.session_state.theme == 'day':
        overlay = "rgba(255, 255, 255, 0.9)"
        card_bg = "rgba(255, 255, 255, 0.95)"
        text_color = "#1e293b"
        accent = "#0284c7"
    else:
        overlay = "rgba(15, 23, 42, 0.85)" # Navy Blue Overlay
        card_bg = "rgba(30, 41, 59, 0.85)" # Dark Navy Cards
        text_color = "#f1f5f9"
        accent = "#38bdf8" # Sky Blue Accent

    # Apply CSS
    st.markdown(f"""
    <style>
    /* Background setup */
    .stApp {{
        background: linear-gradient({overlay}, {overlay}), url('{st.session_state.wallpaper}');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    
    /* Main Content Container */
    .main .block-container {{
        background-color: {card_bg};
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        color: {text_color} !important;
    }}

    /* Text and Sidebar Styling */
    h1, h2, h3, h4, p, span, label, div {{ color: {text_color} !important; }}
    [data-testid="stSidebar"] {{
        background-color: rgba(2, 6, 23, 0.7) !important;
        backdrop-filter: blur(15px);
    }}
    [data-testid="stSidebar"] * {{ color: {accent} !important; font-weight: bold; }}

    /* Button Styling */
    .stButton>button {{
        background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100%;
    }}

    /* Metrics and Tables */
    div[data-testid="stMetric"] {{
        background-color: rgba(15, 23, 42, 0.5);
        border: 1px solid {accent};
        border-radius: 10px;
        padding: 15px;
    }}
    .stDataFrame {{ border: 1px solid {accent}; border-radius: 10px; overflow: hidden; }}
    </style>
    <div style="text-align:center; color:#94a3b8; font-size:10px; font-weight:bold; letter-spacing:2px; margin-bottom:10px;">
        POWERED BY SAHIL & ARMAN IT SOLUTIONS
    </div>
    """, unsafe_allow_html=True)
