import streamlit as st
import random

DAY_WP = ["https://images.unsplash.com/photo-1558769132-cb1aea458c5e", "https://images.unsplash.com/photo-1520004434532-668416a08753", "https://images.unsplash.com/photo-1544441893-675973e31985", "https://images.unsplash.com/photo-1594932224828-b4b059b6f684", "https://images.unsplash.com/photo-1612423284934-2850a4ea6b0f", "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f", "https://images.unsplash.com/photo-1534126511673-b68991578f6a", "https://images.unsplash.com/photo-1516762689617-e1cffcef479d", "https://images.unsplash.com/photo-1542060717-d79d9e463a8a", "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5"]
NIGHT_WP = ["https://images.unsplash.com/photo-1472457897821-70d3819a0e24", "https://images.unsplash.com/photo-1514306191717-452ec28c7814", "https://images.unsplash.com/photo-1537832816519-689ad163238b", "https://images.unsplash.com/photo-1490481651871-ab68de25d43d", "https://images.unsplash.com/photo-1556905085-86a42173d520", "https://images.unsplash.com/photo-1512436991641-6745cdb1723f", "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3", "https://images.unsplash.com/photo-1441986300917-64674bd600d8", "https://images.unsplash.com/photo-1555529771-835f59fc5efe", "https://images.unsplash.com/photo-1506157786151-b8491531f063"]

def apply_style(ln):
    with st.sidebar:
        st.session_state.lang = st.selectbox("Language", ["English", "Urdu"], index=0 if st.session_state.lang=="English" else 1)
        mood = st.radio("UI Mode", ["Day Mood ☀️", "Night Mood 🌙"])
        if st.button(ln['shuffle']):
            st.session_state.bg_choice = random.choice(DAY_WP if "Day" in mood else NIGHT_WP)
    
    if 'bg_choice' not in st.session_state: st.session_state.bg_choice = DAY_WP[0]
    overlay = "rgba(255, 255, 255, 0.90)" if "Day" in mood else "rgba(0, 0, 0, 0.85)"
    txt = "#111" if "Day" in mood else "#fff"

    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{st.session_state.bg_choice}"); background-size: cover; background-attachment: fixed; }}
        .main-container {{ background-color: {overlay}; padding: 30px; border-radius: 15px; color: {txt}; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
        h1, h2, h3, p, label {{ color: {txt} !important; {'text-align: right;' if st.session_state.lang=='Urdu' else ''} }}
        </style>
    """, unsafe_allow_html=True)
