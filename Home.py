from __future__ import annotations

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

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

# ==========================================================
# Animated Barber Track Section (with trail)
# ==========================================================

def animated_barber_mock_track():
    """Animated Barber Motorsports Park lap with trailing line."""
    t = np.linspace(0, 2 * np.pi, 350)
    radius = 1 + 0.25 * np.sin(3 * t) + 0.1 * np.sin(7 * t)

    x = radius * np.cos(t) * 1.2
    y = radius * np.sin(t)

    df = pd.DataFrame({
        "x": x,
        "y": y,
        "frame": np.arange(len(t))
    })

    fig = px.scatter(
        df,
        x="x",
        y="y",
        animation_frame="frame",
        range_x=[-2, 2],
        range_y=[-2, 2],
        height=420,
    )

    # trailing line track path
    fig.add_scatter(
        x=df["x"],
        y=df["y"],
        mode="lines",
        line=dict(color="#0044CC", width=3),
        showlegend=False,
    )

    fig.update_traces(marker=dict(size=12, color="#FF0000"))

    fig.update_layout(
        title="Animated Track — Barber Motorsports Park",
        xaxis_title="",
        yaxis_title="",
        showlegend=False,
        margin=dict(l=0, r=0, t=40, b=0),
    )

    st.plotly_chart(fig, use_container_width=True)


st.subheader("Animated Track — Barber Motorsports Park")
animated_barber_mock_track()

st.markdown("---")

# ==========================================================
# How to Use
# ==========================================================

st.subheader("How to use")

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
