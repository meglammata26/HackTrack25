# pages/02_Telemetry_and_Track.py

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import streamlit as st

from f1_api import load_sample_barber_telemetry
from data_utils import clean_numeric

# Optional Plotly
try:
    import plotly.express as px
except Exception:
    px = None


SESSION_LABEL = "R1"  # Hard-coded for this page


# ---------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Telemetry & Track Visualization — Barber (R1)",
    layout="wide",
)

st.title("Telemetry & Track Visualization — Barber R1 ")
st.markdown(
    """
This page shows:
- Clean lap summary for **R1**  
- Lap durations using earliest start / latest end  
- Junk laps, out-laps, fragments removed (< 75 sec)  
- Per-sample signals  
- GPS track map  
- Telemetry heatmap  
"""
)


# ---------------------------------------------------------------------
# Helpers — Load lap and telemetry data
# ---------------------------------------------------------------------

@st.cache_data(show_spinner=True)
def load_r1_lap_files() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load R1 lap_start, lap_end, lap_time CSV files."""
    base = Path("barber")
    start_path = base / "R1_barber_lap_start.csv"
    end_path = base / "R1_barber_lap_end.csv"
    time_path = base / "R1_barber_lap_time.csv"

    missing = [p for p in (start_path, end_path, time_path) if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing R1 lap files: " + ", ".join(str(p) for p in missing)
        )

    return (
        pd.read_csv(start_path),
        pd.read_csv(end_path),
        pd.read_csv(time_path),
    )


@st.cache_data(show_spinner=True)
def build_r1_lap_summary() -> pd.DataFrame:
    """Generate cleaned lap summary for R1."""
    start_df, end_df, time_df = load_r1_lap_files()

    # Parse timestamps
    for df in (start_df, end_df, time_df):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    group_keys = ["lap", "vehicle_id", "vehicle_number", "outing"]

    # Earliest start per lap
    start_agg = (
        start_df.groupby(group_keys, as_index=False)["timestamp"]
        .min()
        .rename(columns={"timestamp": "timestamp_start"})
    )

    # Latest end per lap
    end_agg = (
        end_df.groupby(group_keys, as_index=False)["timestamp"]
        .max()
        .rename(columns={"timestamp": "timestamp_end"})
    )

    # Last lap-time per lap (optional)
    time_agg = (
        time_df.groupby(group_keys, as_index=False)["timestamp"]
        .max()
        .rename(columns={"timestamp": "timestamp_lap"})
    )

    # Merge aggregates
    lap = (
        start_agg.merge(end_agg, on=group_keys, how="inner")
                 .merge(time_agg, on=group_keys, how="left")
    )

    # Compute duration
    lap["duration_s"] = (
        lap["timestamp_end"] - lap["timestamp_start"]
    ).dt.total_seconds()

    # -------------------------------------------------------------
    # OPTION 1 FILTER: Remove out-laps (duration < 75 sec)
    # -------------------------------------------------------------
    lap = lap[(lap["duration_s"] >= 75.0) & (lap["duration_s"] < 400.0)]

    # Remove timestamp anomalies
    lap = lap[lap["timestamp_end"] > lap["timestamp_start"]]

    lap["session"] = SESSION_LABEL

    return lap.sort_values(["vehicle_id", "lap"]).reset_index(drop=True)


def zscore(series: pd.Series) -> pd.Series:
    m = series.mean()
    s = series.std()
    if s == 0 or np.isnan(s):
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - m) / s


@st.cache_data(show_spinner=True)
def load_sample_telemetry_r1() -> pd.DataFrame:
    """Load sample telemetry restricted to R1."""
    df = load_sample_barber_telemetry()
    df = clean_numeric(df)

    if "meta_session" in df.columns:
        df = df[df["meta_session"] == SESSION_LABEL]

    # Coerce columns
    df["telemetry_value"] = pd.to_numeric(df.get("telemetry_value"), errors="coerce")
    df["timestamp"] = pd.to_datetime(df.get("timestamp"), errors="coerce")

    return df


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------

st.sidebar.header("Controls")

view_mode = st.sidebar.radio(
    "View mode",
    ["Lap Summary", "Per-sample Telemetry"],
)

lap_df = build_r1_lap_summary()

vehicle_options = sorted(lap_df["vehicle_id"].unique().tolist())
selected_vehicles = st.sidebar.multiselect(
    "Vehicle(s)",
    vehicle_options,
    default=vehicle_options,
)
lap_df = lap_df[lap_df["vehicle_id"].isin(selected_vehicles)]


# ---------------------------------------------------------------------
# LAP SUMMARY VIEW
# ---------------------------------------------------------------------

if view_mode == "Lap Summary":
    st.subheader("Lap Summary — Session R1")

    if lap_df.empty:
        st.warning("No laps to display.")
    else:
        valid = lap_df.dropna(subset=["duration_s"])

        # Summary metrics
        best = valid["duration_s"].min()
        worst = valid["duration_s"].max()
        avg = valid["duration_s"].mean()

        c1, c2, c3 = st.columns(3)
        c1.metric("Best Lap (s)", f"{best:.3f}")
        c2.metric("Average Lap (s)", f"{avg:.3f}")
        c3.metric("Worst Lap (s)", f"{worst:.3f}")

        # Outlier detection
        valid = valid.copy()
        valid["z_duration"] = zscore(valid["duration_s"])
        outliers = valid[valid["z_duration"].abs() > 2]

        with st.expander("Outlier Laps (|z| > 2)"):
            if outliers.empty:
                st.write("No outlier laps.")
            else:
                st.dataframe(
                    outliers[
                        [
                            "session",
                            "lap",
                            "vehicle_id",
                            "vehicle_number",
                            "duration_s",
                            "timestamp_start",
                            "timestamp_end",
                            "z_duration",
                        ]
                    ]
                )

        st.markdown("### Lap Table")
        st.dataframe(
            lap_df[
                [
                    "session",
                    "lap",
                    "outing",
                    "vehicle_id",
                    "vehicle_number",
                    "timestamp_start",
                    "timestamp_end",
                    "duration_s",
                ]
            ]
        )

        st.markdown("### Lap Duration vs Lap Number")
        if px:
            fig = px.line(
                lap_df,
                x="lap",
                y="duration_s",
                color="vehicle_id",
                markers=True,
                title="Lap Duration — R1",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(lap_df.set_index("lap")["duration_s"])


# ---------------------------------------------------------------------
# PER-SAMPLE TELEMETRY VIEW
# ---------------------------------------------------------------------

if view_mode == "Per-sample Telemetry":
    st.subheader(" Per-sample Telemetry — Session R1")

    sample_df = load_sample_telemetry_r1()

    if sample_df.empty:
        st.warning("No sample telemetry for R1.")
    else:
        tab_signals, tab_map, tab_heatmap = st.tabs(
            ["Signals vs Time", "Track Map", "Telemetry Heatmap"]
        )

        # -----------------------------------------------------------
        # Signals vs Time
        # -----------------------------------------------------------
        with tab_signals:
            st.markdown("###  Signals vs Time")

            laps_available = sorted(sample_df["lap"].dropna().unique().tolist())
            names = sorted(sample_df["telemetry_name"].dropna().unique().tolist())

            col1, col2 = st.columns(2)
            with col1:
                selected_laps = st.multiselect(
                    "Select laps",
                    laps_available,
                    default=laps_available[:3],
                )
            with col2:
                selected_signals = st.multiselect(
                    "Telemetry channels",
                    names,
                    default=names[:2],
                )

            if not selected_laps or not selected_signals:
                st.info("Select laps and channels.")
            else:
                sub = sample_df[
                    (sample_df["lap"].isin(selected_laps)) &
                    (sample_df["telemetry_name"].isin(selected_signals))
                ].copy()

                sub = sub.sort_values(["telemetry_name", "lap", "timestamp"])
                sub["t_rel_s"] = sub.groupby(
                    ["telemetry_name", "lap"]
                )["timestamp"].transform(
                    lambda x: (x - x.min()).dt.total_seconds()
                )

                if px:
                    fig = px.line(
                        sub,
                        x="t_rel_s",
                        y="telemetry_value",
                        color="lap",
                        facet_row="telemetry_name",
                        title="Telemetry vs Time",
                    )
                    fig.update_yaxes(matches=None)
                    st.plotly_chart(fig, use_container_width=True)

        # -----------------------------------------------------------
        # Track Map
        # -----------------------------------------------------------
        with tab_map:
            st.markdown("### Track Map (GPS)")

            lat_col = next(
                (c for c in ["VBOX_Lat_Min", "VBOX_Lat", "lat"] if c in sample_df.columns),
                None,
            )
            lon_col = next(
                (c for c in ["VBOX_Long_Minutes", "VBOX_Long", "lon"] if c in sample_df.columns),
                None,
            )

            if not lat_col or not lon_col:
                st.info(
                    "GPS columns not found (expected VBOX_Lat_Min and VBOX_Long_Minutes)."
                )
            else:
                laps_available = sorted(sample_df["lap"].unique().tolist())
                lap_sel = st.selectbox("Select lap", laps_available)

                lap_pts = sample_df[
                    (sample_df["lap"] == lap_sel) &
                    sample_df[lat_col].notna() &
                    sample_df[lon_col].notna()
                ].copy()

                map_df = pd.DataFrame({"lat": lap_pts[lat_col], "lon": lap_pts[lon_col]})

                if px and not map_df.empty:
                    fig = px.scatter_mapbox(
                        map_df,
                        lat="lat",
                        lon="lon",
                        zoom=14,
                        height=500,
                    )
                    fig.update_traces(mode="lines+markers")
                    fig.update_layout(mapbox_style="open-street-map")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.map(map_df)

        # -----------------------------------------------------------
        # Telemetry Heatmap
        # -----------------------------------------------------------
        with tab_heatmap:
            st.markdown("### Telemetry Heatmap")

            tele_stats = (
                sample_df.groupby("telemetry_name")["telemetry_value"]
                .agg(["count", "std"])
                .reset_index()
                .dropna(subset=["std"])
                .sort_values("std", ascending=False)
            )

            default_signals = tele_stats["telemetry_name"].head(10).tolist()

            sig_sel = st.multiselect(
                "Select signals",
                tele_stats["telemetry_name"],
                default=default_signals,
            )

            if not sig_sel:
                st.info("Select at least one signal.")
            else:
                heat = (
                    sample_df[sample_df["telemetry_name"].isin(sig_sel)]
                    .groupby(["lap", "telemetry_name"])["telemetry_value"]
                    .mean()
                    .reset_index()
                )

                pivot = heat.pivot_table(
                    index="lap",
                    columns="telemetry_name",
                    values="telemetry_value",
                )

                if px:
                    fig = px.imshow(
                        pivot.values,
                        x=pivot.columns,
                        y=pivot.index,
                        color_continuous_scale="Viridis",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(pivot.style.background_gradient(cmap="viridis"))
