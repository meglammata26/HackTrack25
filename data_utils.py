"""
Shared data utilities for the Barber Telemetry ML Lab.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd


def clean_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert numeric-looking columns to numeric dtypes and drop completely empty columns.
    Does not mutate the original dataframe.
    """
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            # Try numeric conversion, but silently ignore if not possible
            try:
                df[col] = pd.to_numeric(df[col])
            except Exception:
                pass
    df = df.dropna(axis=1, how="all")
    return df


def add_fast_slow_label(
    df: pd.DataFrame,
    target_col: str,
    label_col: str = "is_fast_lap",
    threshold: str | float = "median",
) -> pd.DataFrame:
    """
    Add a binary fast/slow label based on a numeric column (typically lap time).

    If threshold == "median":
        Laps with target_col < median are labeled 1 (fast), others 0 (slow).
    Otherwise, threshold can be a numeric value.
    """
    df = df.copy()
    if target_col not in df.columns:
        raise ValueError(f"Column '{target_col}' not found in dataframe.")

    if threshold == "median":
        thr_value = df[target_col].median()
    else:
        thr_value = float(threshold)

    df[label_col] = (df[target_col] < thr_value).astype(int)
    return df


def pivot_trd_long_to_wide(
    df_long: pd.DataFrame,
    index_cols: Iterable[str],
    channel_col: str,
    value_col: str,
) -> pd.DataFrame:
    """
    Generic long → wide pivot helper for telemetry-style data.

    Example expected schema:
        - index_cols: ["lap", "distance"] or ["lap", "time_s"]
        - channel_col: "channel" (e.g. values like "speed", "throttle", "brake")
        - value_col: "value"

    Returns a wide dataframe with one row per index combination and
    one column per channel.
    """
    missing = [c for c in (*index_cols, channel_col, value_col) if c not in df_long.columns]
    if missing:
        raise ValueError(f"Missing required columns for pivot: {missing}")

    df_pivot = (
        df_long
        .pivot_table(
            index=list(index_cols),
            columns=channel_col,
            values=value_col,
            aggfunc="mean",
        )
        .reset_index()
    )

    # Flatten MultiIndex columns if needed
    if isinstance(df_pivot.columns, pd.MultiIndex):
        df_pivot.columns = [
            "_".join([str(x) for x in col if x != ""])
            for col in df_pivot.columns.values
        ]

    return df_pivot


def train_test_indices(
    n_samples: int, test_size: float = 0.2, random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simple helper to generate train/test boolean masks or indices.

    Returns (train_idx, test_idx) as arrays of indices.
    """
    rng = np.random.default_rng(random_state)
    indices = np.arange(n_samples)
    rng.shuffle(indices)

    split = int((1.0 - test_size) * n_samples)
    train_idx = indices[:split]
    test_idx = indices[split:]
    return train_idx, test_idx
