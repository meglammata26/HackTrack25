# pages/02_Telemetry_and_Track.py

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from f1_api import load_sample_barber_telemetry
from data_utils import clean_numeric

st.set_page_config(
    page_title="📊 Telemetry & Track Visualization — R1 Barber",
    layout="wide",
)

st.title("📊 Telemetry & Track Visualization — R1 Barber 🏁")

st.markdown(
    """
This page lets you explore **Barber telemetry**:

- View speed, throttle, brake, etc. vs distance or time  
- Filter by lap and driver  
- Quickly sanity-check uploaded telemetry  
"""
)

st.sidebar.header("📁 Data Source")

data_source = st.sidebar.radio(
    "Choose telemetry data source:",
    ["Sample Barber CSV", "Upload CSV"],
)

uploaded_file = None
if data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload telemetry CSV", type=["csv"])

@st.cache_data(show_spinner=True)
def _load_data(source: str, file) -> pd.DataFrame:
    if source == "Sample Barber CSV":
        df = load_sample_barber_telemetry()
    else:
        if file is None:
            return pd.DataFrame()
        df = pd.read_csv(file)
    return df


df_raw = _load_data(data_source, uploaded_file)

if df_raw.empty:
    st.info("Load a dataset via the sidebar to view telemetry.")
    st.stop()

st.subheader("📄 Raw Telemetry (preview)")
st.dataframe(df_raw.head())

df = clean_numeric(df_raw)

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
non_numeric_cols = [c for c in df.columns if c not in numeric_cols]

# Guess some common columns if present
lap_col = None
for candidate in ["lap", "Lap", "lap_number"]:
    if candidate in df.columns:
        lap_col = candidate
        break

driver_col = None
for candidate in ["driver", "Driver", "car"]:
    if candidate in df.columns:
        driver_col = candidate
        break

distance_col = None
for candidate in ["distance", "Distance", "dist_m"]:
    if candidate in df.columns:
        distance_col = candidate
        break

time_col = None
for candidate in ["time_s", "Time_s", "session_time_s"]:
    if candidate in df.columns:
        time_col = candidate
        break

st.markdown("---")
st.subheader("🎛️ Filters")

col1, col2, col3 = st.columns(3)

with col1:
    if lap_col and lap_col in df.columns:
        laps = sorted(df[lap_col].dropna().unique())
        selected_laps = st.multiselect(
            f"Filter by {lap_col}", laps, default=laps[:3]
        )
        if selected_laps:
            df = df[df[lap_col].isin(selected_laps)]

with col2:
    if driver_col and driver_col in df.columns:
        drivers = sorted(df[driver_col].dropna().unique())
        selected_drivers = st.multiselect(
            f"Filter by {driver_col}", drivers, default=drivers[:2]
        )
        if selected_drivers:
            df = df[df[driver_col].isin(selected_drivers)]

with col3:
    x_axis = st.selectbox(
        "X-axis",
        [c for c in [distance_col, time_col] if c is not None] or numeric_cols,
    )

st.markdown("---")
st.subheader("📈 Telemetry Signals")

y_candidates = [c for c in numeric_cols if c != x_axis]
default_y = [c for c in y_candidates if "speed" in c.lower()] or y_candidates[:3]

y_selected = st.multiselect(
    "Telemetry channels to plot",
    y_candidates,
    default=default_y,
)

if not y_selected:
    st.warning("Select at least one telemetry channel to plot.")
    st.stop()

plot_df = df[[x_axis] + y_selected].sort_values(by=x_axis)
plot_df = plot_df.set_index(x_axis)

st.line_chart(plot_df)

st.markdown("---")
st.subheader("🔎 Descriptive Stats")

st.write(df[y_selected].describe())
