"""
F1 / Barber telemetry loading utilities.

This version is updated to directly load your existing
barber/barber_sample.csv instead of expecting a data/ folder.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


# ---------- Local CSV loading ----------

@st.cache_data(show_spinner=True)
def load_sample_barber_telemetry(
    csv_path: str = "barber/barber_sample.csv",
) -> pd.DataFrame:
    """
    Load a sample Barber telemetry CSV.

    Updated: This now points to your actual file:
        barber/barber_sample.csv
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Sample telemetry CSV not found at: {path.resolve()}\n\n"
            "Either place your CSV there, or update 'csv_path' in load_sample_barber_telemetry()."
        )

    df = pd.read_csv(path)
    return df


# ---------- Optional fastf1 integration ----------

def _try_import_fastf1():
    try:
        import fastf1  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "fastf1 is not installed. Install with:\n\n"
            "    pip install fastf1\n\n"
            "Comment out or avoid calling load_f1_session_telemetry if you don't need it."
        ) from exc
    return fastf1


@st.cache_data(show_spinner=True)
def load_f1_session_telemetry(
    year: int,
    gp_name: str,
    session_name: str = "R",
    enable_cache: bool = True,
) -> pd.DataFrame:
    """
    Download F1 telemetry for a given session using fastf1.

    Example:
        df = load_f1_session_telemetry(2024, "Bahrain", "R")

    Returns a dataframe with one row per telemetry sample per car.
    """
    fastf1 = _try_import_fastf1()

    if enable_cache:
        fastf1.Cache.enable_cache("fastf1_cache")

    session = fastf1.get_session(year, gp_name, session_name)
    session.load()

    records = []
    for car in session.car_data:
        tel = session.car_data[car]
        df_car = tel.copy()
        df_car["car"] = car
        df_car["session_time_s"] = df_car["Time"].dt.total_seconds()
        records.append(df_car)

    full_df = pd.concat(records, ignore_index=True)
    return full_df
