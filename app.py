# app.py
import streamlit as st
from utils import styling, loader

styling.set_page_config()
styling.inject_base_css()
styling.render_banner()

st.title("Overview")

df = loader.sidebar_data_selector()

st.markdown(
    """
This app is a **Toyota Gazoo Racing Barber Telemetry ML Lab**:

- Load TRD Barber telemetry (sample or full R1/R2)  
- Auto-pivot long-format telemetry into wide format  
- Explore telemetry & track maps  
- Run regression, classification, and clustering  
- Use an **offline Gazoo AI race engineer** for insights
"""
)

st.subheader("Data preview")
st.write(df.head())
st.write(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")

styling.render_track_card()
