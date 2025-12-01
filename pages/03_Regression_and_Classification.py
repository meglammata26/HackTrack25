# pages/03_Regression_and_Classification.py

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    root_mean_squared_error,   # NEW ✔
)
from sklearn.model_selection import train_test_split

from f1_api import load_sample_barber_telemetry
from data_utils import clean_numeric, add_fast_slow_label

# ======================================================================
# PAGE CONFIG
# ======================================================================

st.set_page_config(
    page_title="📈 Regression & Classification — Barber Telemetry ML",
    layout="wide",
)

st.title("📈 Regression & Classification — Barber Telemetry ML")

st.markdown(
    """
Use this page to build **machine learning models** on Barber telemetry data:

- Predict numeric targets (e.g., lap times, speeds) with **Regression**
- Classify laps as **Fast vs Slow** with **Classification**
"""
)

# ======================================================================
# LOAD DATA
# ======================================================================

st.sidebar.header("📁 Data Source")

data_source = st.sidebar.radio(
    "Choose telemetry data source:",
    ["Sample Barber CSV", "Upload CSV"],
)

uploaded = None
if data_source == "Upload CSV":
    uploaded = st.sidebar.file_uploader("Upload telemetry CSV", type=["csv"])


@st.cache_data(show_spinner=True)
def _load_data(source: str, file) -> pd.DataFrame:
    if source == "Sample Barber CSV":
        return load_sample_barber_telemetry()
    else:
        if file is None:
            return pd.DataFrame()
        return pd.read_csv(file)


df_raw = _load_data(data_source, uploaded)

if df_raw.empty:
    st.info("Load a dataset using the sidebar to train ML models.")
    st.stop()

st.subheader("📄 Telemetry Data (Preview)")
st.dataframe(df_raw.head())

df = clean_numeric(df_raw)

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if not numeric_cols:
    st.error("No numeric columns found after cleaning.")
    st.stop()

# ======================================================================
# PROBLEM SETUP
# ======================================================================

st.markdown("---")

col_mode, col_target = st.columns([1, 2])

with col_mode:
    problem_type = st.radio("Problem type", ["Regression", "Classification"])

with col_target:
    target_col = st.selectbox(
        "Target column (y)",
        numeric_cols,
        index=0,
    )

feature_cols = st.multiselect(
    "Feature columns (X)",
    [c for c in numeric_cols if c != target_col],
    default=[c for c in numeric_cols if c != target_col][:5],
)

if not feature_cols:
    st.warning("Select at least one feature to continue.")
    st.stop()

test_size = st.slider("Test size (fraction)", 0.1, 0.5, 0.2, 0.05)
random_state = st.number_input("Random seed", value=42)

X = df[feature_cols].copy()
y = df[target_col].copy()

# ======================================================================
# REGRESSION
# ======================================================================

def run_regression():
    st.header("🤖 Regression Models")

    model_name = st.selectbox(
        "Regression model",
        ["Linear Regression", "Ridge Regression", "Lasso Regression", "Random Forest"],
    )

    # Model parameters
    if model_name in ["Ridge Regression", "Lasso Regression"]:
        alpha = st.slider("alpha (regularization strength)", 0.0001, 10.0, 1.0)
    elif model_name == "Random Forest":
        n_estimators = st.slider("n_estimators", 10, 500, 200)
        max_depth = st.slider("max_depth", 2, 50, 10)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Model selection
    if model_name == "Linear Regression":
        model = LinearRegression()
    elif model_name == "Ridge Regression":
        model = Ridge(alpha=alpha)
    elif model_name == "Lasso Regression":
        model = Lasso(alpha=alpha)
    else:
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
        )

    if st.button("Train Regression Model"):
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Metrics (updated RMSE!)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = root_mean_squared_error(y_test, y_pred)   # NEW ✔

        st.subheader("📏 Regression Metrics")
        c1, c2, c3 = st.columns(3)
        c1.metric("R²", f"{r2:.3f}")
        c2.metric("MAE", f"{mae:.3f}")
        c3.metric("RMSE", f"{rmse:.3f}")

        # Plot true vs predicted
        st.subheader("🔍 True vs Predicted (line plot)")
        chart_df = pd.DataFrame({
            "y_true": y_test.values,
            "y_pred": y_pred,
        })
        st.line_chart(chart_df)

        # Feature importance for Random Forest only
        if isinstance(model, RandomForestRegressor):
            importances = pd.DataFrame({
                "feature": feature_cols,
                "importance": model.feature_importances_,
            }).sort_values("importance", ascending=False)

            st.subheader("🌲 Feature Importance (Random Forest)")
            st.bar_chart(importances.set_index("feature"))


# ======================================================================
# CLASSIFICATION
# ======================================================================

def run_classification():
    st.header("🏁 Fast vs Slow Classification")

    # Generate fast/slow label if missing
    label_col = st.text_input("Label column name", value="is_fast_lap")

    if label_col not in df.columns:
        st.info(
            f"Generating {label_col} from target '{target_col}' "
            "using median split: laps < median are fast (1)."
        )
        df_labeled = add_fast_slow_label(df, target_col, label_col)
    else:
        df_labeled = df.copy()

    y_cls = df_labeled[label_col].astype(int)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_cls,
        test_size=test_size,
        random_state=random_state,
        stratify=y_cls,
    )

    # Hyperparameters
    n_estimators = st.slider("n_estimators", 50, 500, 200)
    max_depth = st.slider("max_depth", 2, 50, 10)
    min_samples_leaf = st.slider("min_samples_leaf", 1, 20, 2)

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
        n_jobs=-1,
    )

    if st.button("Train Classifier"):
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)

        st.subheader("📏 Classification Metrics")
        c1, c2, c3 = st.columns(3)
        c1.metric("Accuracy", f"{acc:.3f}")
        c2.metric("Precision", f"{prec:.3f}")
        c3.metric("Recall", f"{rec:.3f}")

        # Distribution of test labels
        st.subheader("🔢 Class distribution (y_test)")
        st.bar_chart(y_test.value_counts(normalize=True))

        # Feature importance
        importances = model.feature_importances_
        imp_df = pd.DataFrame({
            "feature": feature_cols,
            "importance": importances
        }).sort_values("importance", ascending=False)

        st.subheader("🌲 Feature Importances (Random Forest)")
        st.bar_chart(imp_df.set_index("feature"))


# ======================================================================
# MAIN
# ======================================================================

if problem_type == "Regression":
    run_regression()
else:
    run_classification()
