import streamlit as st
import random

def apply_style(ln=None):  # ADDED PARAMETER HERE
    """Apply custom CSS styles with day/night mode and wallpaper support"""
    
    # Initialize session state for theme
    if 'theme' not in st.session_state:
        st.session_state.theme = 'day'  # Default theme
    
    # Initialize session state for wallpaper
    if 'wallpaper' not in st.session_state:
        st.session_state.wallpaper = None
    
    # Wallpaper collection
    DAY_WALLPAPERS = [
        # Nature (1-5)
        "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=1600",
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1600",
        "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1600",
        "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?w=1600",
        "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=1600",
        
        # Greenery (6-10)
        "https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=1600",
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600",
        "https://images.unsplash.com/photo-1476820865390-c52aeebb9891?w=1600",
        "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=1600",
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1600",
        
        # Sky Colors (11-15)
        "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1600",
        "https://images.unsplash.com/photo-1488866022504-f2584929ca5f?w=1600",
        "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=1600",
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600",
        "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=1600"
    ]
    
    NIGHT_WALLPAPERS = [
        # Galaxy/Space (1-5)
        "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=1600",
        "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1600",
        "https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?w=1600",
        "https://images.unsplash.com/photo-1465101162946-4377e57745c3?w=1600",
        "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1600",
        
        # Night City (6-10)
        "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1600",
        "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1600",
        "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?w=1600",
        "https://images.unsplash.com/photo-1475274047050-1d0c0975c63e?w=1600",
        "https://images.unsplash.com/photo-1476820865390-c52aeebb9891?w=1600",
        
        # Tailor Weapons/Instruments (11-15)
        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1600",  # Sewing machine
        "https://images.unsplash.com/photo-1533563909201-c6a05d8b4c3b?w=1600",  # Measuring tape
        "https://images.unsplash.com/photo-1512403754473-27835f7b9984?w=1600",  # Scissors
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1600",  # Fabric rolls
        "https://images.unsplash.com/photo-1562157873-818bc0726f68?w=1600"   # Thread spools
    ]
    
    # If ln parameter is provided, it might be for language or location
    # You can use it if needed, for example:
    if ln:
        # Store language in session state if needed
        if 'language' not in st.session_state:
            st.session_state.language = ln
    
    # Theme toggle in sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("🎨 Theme Settings")
        
        # Theme selector
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌞 Day", use_container_width=True):
                st.session_state.theme = 'day'
                st.session_state.wallpaper = random.choice(DAY_WALLPAPERS)
                st.rerun()
        with col2:
            if st.button("🌙 Night", use_container_width=True):
                st.session_state.theme = 'night'
                st.session_state.wallpaper = random.choice(NIGHT_WALLPAPERS)
                st.rerun()
        
        # Shuffle wallpaper button
        if st.button("🔄 Shuffle Wallpaper", use_container_width=True):
            if st.session_state.theme == 'day':
                st.session_state.wallpaper = random.choice(DAY_WALLPAPERS)
            else:
                st.session_state.wallpaper = random.choice(NIGHT_WALLPAPERS)
            st.rerun()
    
    # Get current wallpaper
    if st.session_state.wallpaper is None:
        if st.session_state.theme == 'day':
            st.session_state.wallpaper = DAY_WALLPAPERS[0]
        else:
            st.session_state.wallpaper = NIGHT_WALLPAPERS[0]
    
    # Apply theme-specific styles
    if st.session_state.theme == 'night':
        night_mode_css(st.session_state.wallpaper)
    else:
        day_mode_css(st.session_state.wallpaper)

# The rest of your code remains the same...
