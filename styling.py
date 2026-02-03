import streamlit as st
import random

def apply_styling():
    if 'theme' not in st.session_state: st.session_state.theme = 'night'
    if 'wallpaper' not in st.session_state: st.session_state.wallpaper = None

    DAY_WALLPAPERS = [
        "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=1600", "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1600",
        "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1600", "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?w=1600",
        "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=1600", "https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=1600",
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600", "https://images.unsplash.com/photo-1476820865390-c52aeebb9891?w=1600",
        "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=1600", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1600",
        "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1600", "https://images.unsplash.com/photo-1488866022504-f2584929ca5f?w=1600",
        "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=1600", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600",
        "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=1600"
    ]
    
    NIGHT_WALLPAPERS = [
        "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=1600", "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1600",
        "https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?w=1600", "https://images.unsplash.com/photo-1465101162946-4377e57745c3?w=1600",
        "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1600", "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1600",
        "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1600", "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?w=1600",
        "https://images.unsplash.com/photo-1475274047050-1d0c0975c63e?w=1600", "https://images.unsplash.com/photo-1476820865390-c52aeebb9891?w=1600",
        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1600", "https://images.unsplash.com/photo-1533563909201-c6a05d8b4c3b?w=1600",
        "https://images.unsplash.com/photo-1512403754473-27835f7b9984?w=1600", "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1600",
        "https://images.unsplash.com/photo-1562157873-818bc0726f68?w=1600"
    ]

    with st.sidebar:
        st.markdown("---")
        st.subheader("🎨 UI Theme")
        c1, c2 = st.columns(2)
        if c1.button("☀️ Day"):
            st.session_state.theme = 'day'
            st.session_state.wallpaper = random.choice(DAY_WALLPAPERS)
            st.rerun()
        if c2.button("🌙 Night"):
            st.session_state.theme = 'night'
            st.session_state.wallpaper = random.choice(NIGHT_WALLPAPERS)
            st.rerun()
        if st.button("🔄 Shuffle"):
            st.session_state.wallpaper = random.choice(DAY_WALLPAPERS if st.session_state.theme == 'day' else NIGHT_WALLPAPERS)
            st.rerun()

    if st.session_state.wallpaper is None:
        st.session_state.wallpaper = NIGHT_WALLPAPERS[0]

    # Render CSS
    overlay = "rgba(255, 255, 255, 0.9)" if st.session_state.theme == 'day' else "rgba(0, 0, 0, 0.85)"
    text_color = "#2c3e50" if st.session_state.theme == 'day' else "white"
    card_bg = "rgba(255, 255, 255, 0.95)" if st.session_state.theme == 'day' else "rgba(30, 30, 40, 0.85)"

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient({overlay}, {overlay}), url('{st.session_state.wallpaper}');
        background-size: cover; background-attachment: fixed;
    }}
    .main .block-container {{
        background-color: {card_bg}; border-radius: 15px; padding: 2rem; color: {text_color} !important;
    }}
    h1, h2, h3, h4, p, span, label, .stMetric {{ color: {text_color} !important; }}
    .stButton>button {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white !important; border-radius: 8px; }}
    [data-testid="stSidebar"] {{ background-color: rgba(0,0,0,0.5) !important; backdrop-filter: blur(10px); }}
    </style>
    """, unsafe_allow_html=True)
