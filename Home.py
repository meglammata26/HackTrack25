from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Toyota Gazoo Racing — Barber Telemetry ML Lab",
    layout="wide",
)

st.title("Barber Telemetry ML Lab")

st.markdown(
    """
Welcome to your **Toyota Gazoo Racing Barber Telemetry ML Lab**.  
This app lets you:

- Explore telemetry & track visualizations  
- Run regression models to predict numeric targets (lap time, speed, etc.)  
- Classify laps as **fast vs slow** using ML  
- Experiment with clustering on telemetry features  

Use the sidebar or the **Pages** menu to move between:
- **Telemetry & Track** (02…)  
- **Regression & Classification** (03…)  
- **Clustering Telemetry** (04…)
"""
)

st.markdown("---")

st.subheader("ℹHow to use")

st.markdown(
    """
1. Go to **Telemetry & Track** to load or upload telemetry data.  
2. Inspect signals like speed, throttle, brake, etc.  
3. Then open **Regression & Classification** to train ML models.  
4. Optionally, open **Clustering Telemetry** to segment laps or sections.

You can start with the **sample Barber CSV** or upload your own CSV that matches your schema.
"""
)

st.info(
    "Tip: If something crashes or a column name doesn’t match, "
    "open the CSV in a spreadsheet or `st.dataframe` and adjust the code to your column names."
)
