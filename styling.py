import streamlit as st
import random

def apply_custom_styles():
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
        "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w-1600",
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

def day_mode_css(wallpaper_url):
    """Apply day mode CSS with wallpaper"""
    st.markdown(f"""
    <style>
    /* Background with wallpaper */
    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.95)), 
                    url('{wallpaper_url}');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    
    /* Main container */
    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: rgba(248, 249, 250, 0.95);
        backdrop-filter: blur(10px);
    }}
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6 {{
        color: #2c3e50;
    }}
    
    p, span, div, label {{
        color: #34495e;
    }}
    
    /* Button styling */
    .stButton > button {{
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
    }}
    
    .stButton > button:hover {{
        background-color: #2980b9;
        transform: translateY(-2px);
    }}
    
    /* Metric cards */
    .stMetric {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    
    /* Dataframe styling */
    .dataframe {{
        border-radius: 10px;
        background-color: white;
    }}
    
    /* Form styling */
    .stForm {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e9ecef;
    }}
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input {{
        background-color: white;
        border: 1px solid #ced4da;
        border-radius: 6px;
    }}
    
    /* Success/Error messages */
    .stAlert {{
        border-radius: 8px;
        border: none;
    }}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: #f1f1f1;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: #888;
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: #555;
    }}
    </style>
    """, unsafe_allow_html=True)

def night_mode_css(wallpaper_url):
    """Apply night mode CSS with dark theme and wallpaper"""
    st.markdown(f"""
    <style>
    /* Background with wallpaper (darker overlay for night) */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.9)), 
                    url('{wallpaper_url}');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: white !important;
    }}
    
    /* Main container - dark glass effect */
    .main .block-container {{
        background-color: rgba(30, 30, 40, 0.85);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* Sidebar styling - dark glass */
    section[data-testid="stSidebar"] {{
        background-color: rgba(20, 20, 30, 0.9) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* ALL TEXT WHITE IN NIGHT MODE */
    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th, strong, em, 
    .stMarkdown, .stText, .stCode, .stDataFrame, .stMetric, .stAlert {{
        color: white !important;
    }}
    
    /* Specific white text for different elements */
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: white !important;
    }}
    
    .stDataFrame td, .stDataFrame th {{
        color: white !important;
    }}
    
    .stMetric label, .stMetric div {{
        color: white !important;
    }}
    
    /* Button styling - neon glow effect */
    .stButton > button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }}
    
    /* Metric cards - dark glass */
    .stMetric {{
        background-color: rgba(40, 40, 60, 0.7);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }}
    
    /* Dataframe styling - dark */
    .dataframe {{
        border-radius: 10px;
        background-color: rgba(40, 40, 60, 0.7) !important;
        color: white !important;
    }}
    
    .dataframe th {{
        background-color: rgba(60, 60, 80, 0.9) !important;
        color: white !important;
    }}
    
    .dataframe td {{
        background-color: rgba(40, 40, 60, 0.7) !important;
        color: white !important;
    }}
    
    /* Form styling - dark glass */
    .stForm {{
        background-color: rgba(40, 40, 60, 0.7);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* Input fields - dark theme */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input {{
        background-color: rgba(30, 30, 40, 0.8);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px;
    }}
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {{
        color: rgba(255, 255, 255, 0.5) !important;
    }}
    
    /* Checkbox and radio buttons */
    .stCheckbox, .stRadio {{
        color: white !important;
    }}
    
    .stCheckbox > label, .stRadio > label {{
        color: white !important;
    }}
    
    /* Select boxes */
    .stSelectbox > div > div > select {{
        background-color: rgba(30, 30, 40, 0.8);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    
    /* Slider */
    .stSlider > div > div > div > div {{
        background-color: rgba(255, 255, 255, 0.1);
    }}
    
    .stSlider > div > div > div > div > div {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }}
    
    /* Success/Error messages */
    .stAlert {{
        border-radius: 8px;
        border: none;
        background-color: rgba(30, 30, 40, 0.9) !important;
        color: white !important;
    }}
    
    .element-container .stAlert {{
        background-color: rgba(30, 30, 40, 0.9) !important;
    }}
    
    /* Tabs */
    .stTabs {{
        background-color: transparent;
    }}
    
    .stTabs > div > div > button {{
        color: white !important;
        background-color: rgba(40, 40, 60, 0.7) !important;
    }}
    
    .stTabs > div > div > button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: rgba(102, 126, 234, 0.8) !important;
        color: white !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: rgba(40, 40, 60, 0.7) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    
    /* Custom scrollbar for night mode */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(30, 30, 40, 0.8);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }}
    
    /* Fix for plotly charts background */
    .js-plotly-plot .plotly .modebar {{
        background-color: rgba(30, 30, 40, 0.8) !important;
    }}
    
    /* Table borders */
    table {{
        border-color: rgba(255, 255, 255, 0.1) !important;
    }}
    
    th, td {{
        border-color: rgba(255, 255, 255, 0.1) !important;
    }}
    
    /* Code blocks */
    .stCode {{
        background-color: rgba(20, 20, 30, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    
    /* Divider */
    hr {{
        border-color: rgba(255, 255, 255, 0.1) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Helper function to get current theme
def get_current_theme():
    return st.session_state.get('theme', 'day')

# Helper function to get current wallpaper
def get_current_wallpaper():
    return st.session_state.get('wallpaper', None)

# Helper function to set theme
def set_theme(theme_name):
    st.session_state.theme = theme_name
