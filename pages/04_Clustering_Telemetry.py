# pages/04_Clustering_Telemetry.py

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans

from f1_api import load_sample_barber_telemetry
from data_utils import clean_numeric

st.set_page_config(
    page_title="🔍 Clustering Telemetry — Barber ML Lab",
    layout="wide",
)

st.title("🔍 Clustering Telemetry")

st.markdown(
    """
This page lets you cluster telemetry samples into groups based on
numeric features (e.g. speed, throttle, brake, G-forces, etc.).
"""
)

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
    st.info("Load a dataset via the sidebar to run clustering.")
    st.stop()

st.subheader("📄 Telemetry (preview)")
st.dataframe(df_raw.head())

df = clean_numeric(df_raw)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if not numeric_cols:
    st.error("No numeric columns found after cleaning.")
    st.stop()

feature_cols = st.multiselect(
    "Features to use for clustering",
    numeric_cols,
    default=numeric_cols[:5],
)

if not feature_cols:
    st.warning("Select at least one feature.")
    st.stop()

n_clusters = st.slider("Number of clusters (k)", 2, 10, 4, 1)
random_state = st.number_input("Random seed", value=42, step=1)

X = df[feature_cols].copy().dropna()
if X.empty:
    st.error("No valid rows after dropping NaNs for selected features.")
    st.stop()

if st.button("Run KMeans clustering"):
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto")
    labels = model.fit_predict(X)

    df_clustered = X.copy()
    df_clustered["cluster"] = labels

    st.subheader("📊 Cluster counts")
    st.bar_chart(df_clustered["cluster"].value_counts().sort_index())

    st.subheader("📉 Cluster centroids")
    centroids = pd.DataFrame(model.cluster_centers_, columns=feature_cols)
    centroids["cluster"] = np.arange(n_clusters)
    st.dataframe(centroids)

    st.subheader("📈 Example 2D projection")
    if len(feature_cols) >= 2:
        x_col = feature_cols[0]
        y_col = feature_cols[1]
        st.write(f"Scatter of **{x_col}** vs **{y_col}** colored by cluster.")
        proj_df = df_clustered[[x_col, y_col, "cluster"]].copy()
        st.scatter_chart(proj_df, x=x_col, y=y_col, color="cluster")
    else:
        st.info("Select at least two features to see a 2D scatter plot.")
