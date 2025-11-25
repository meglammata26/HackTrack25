# utils/loader.py
import os
import streamlit as st
import pandas as pd
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
BARBER_DIR = os.path.join(ROOT_DIR, "barber")


def pivot_trd_long_to_wide(df: pd.DataFrame) -> pd.DataFrame:
    """
    If the dataframe is in TRD long format (lap, telemetry_name, telemetry_value),
    pivot to wide so each telemetry_name becomes its own column.
    """
    if not {"telemetry_name", "telemetry_value"}.issubset(df.columns):
        return df  # already wide

    idx_cols = []
    if "lap" in df.columns:
        idx_cols.append("lap")
    if "timestamp" in df.columns:
        idx_cols.append("timestamp")

    if not idx_cols:
        # fallback: index by row number
        df = df.reset_index().rename(columns={"index": "row"})
        idx_cols = ["row"]

    # try to parse timestamp if present
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    wide = df.pivot_table(
        index=idx_cols,
        columns="telemetry_name",
        values="telemetry_value",
        aggfunc="mean",
    ).reset_index()

    wide.columns.name = None
    wide.columns = [str(c) for c in wide.columns]
    return wide


@st.cache_data(show_spinner=True)
def load_and_pivot_any(local_path: str | None, uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif local_path is not None:
        df = pd.read_csv(local_path)
    else:
        st.stop()

    df = pivot_trd_long_to_wide(df)
    return df


def guess_columns(df: pd.DataFrame):
    cols = list(df.columns)
    def pick(candidates):
        for c in candidates:
            if c in cols:
                return c
        return None

    mapping = {
        "speed_col": pick(["VBOX_Speed", "Speed", "speed"]),
        "throttle_col": pick(["aps", "Throttle", "throttle"]),
        "brake_col": pick(["pbrake_f", "Brake", "brake", "pbrake_r"]),
        "lat_col": pick(["VBOX_Lat_Min", "Latitude", "lat"]),
        "lon_col": pick(["VBOX_Long_Minutes", "Longitude", "lon"]),
        "lap_id_col": pick(["lap", "Lap"]),
    }
    return mapping


def sidebar_data_selector():
    st.sidebar.header("Data source")

    choice = st.sidebar.radio(
        "Choose telemetry source",
        (
            "Sample Barber subset",
            "R1 telemetry (full)",
            "R2 telemetry (full)",
            "Upload CSV",
        ),
    )

    uploaded_file = None
    local_path = None

    if choice == "Sample Barber subset":
        local_path = os.path.join(BARBER_DIR, "barber_sample.csv")
    elif choice == "R1 telemetry (full)":
        local_path = os.path.join(BARBER_DIR, "R1_barber_telemetry_data.csv")
    elif choice == "R2 telemetry (full)":
        local_path = os.path.join(BARBER_DIR, "R2_barber_telemetry_data.csv")
    else:
        uploaded_file = st.sidebar.file_uploader("Upload TRD CSV", type=["csv"])

    df = load_and_pivot_any(local_path, uploaded_file)

    mapping = guess_columns(df)
    st.session_state["mapping"] = mapping

    return df


def build_ml_matrices(df, target_col, drop_cols=None):
    if drop_cols is None:
        drop_cols = []

    numeric_df = df.select_dtypes(include=[np.number]).copy()
    feature_cols = [c for c in numeric_df.columns if c not in drop_cols + [target_col]]

    X = numeric_df[feature_cols].replace([np.inf, -np.inf], np.nan)
    X = X.fillna(method="ffill").fillna(method="bfill")

    y = df[target_col].replace([np.inf, -np.inf], np.nan)
    y = y.fillna(method="ffill").fillna(method="bfill")

    valid = y.notna()
    X = X.loc[valid]
    y = y.loc[valid]

    return X, y, feature_cols
