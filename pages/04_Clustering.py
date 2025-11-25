# pages/04_Clustering.py
import streamlit as st
import plotly.express as px
from sklearn.cluster import KMeans
import pandas as pd

from utils import styling, loader

styling.inject_base_css()
styling.render_banner()

st.title("Driver Style Clustering (KMeans)")

df = loader.sidebar_data_selector()
numeric_cols = df.select_dtypes(include="number").columns.tolist()

mapping = st.session_state.get("mapping", {})
lap_id_col = mapping.get("lap_id_col")

target_col = st.sidebar.selectbox("Drop this column from features", numeric_cols)
n_clusters = st.sidebar.slider("Number of clusters", 2, 6, 3, 1)

drop_cols = []
if lap_id_col:
    drop_cols.append(lap_id_col)

X, _, feature_cols = loader.build_ml_matrices(df, target_col, drop_cols)
X = X.fillna(0)

st.write(f"Clustering matrix: {X.shape[0]} samples × {X.shape[1]} features")

if st.button("Run KMeans"):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)

    st.subheader("Cluster counts")
    st.write(pd.Series(clusters).value_counts().sort_index())

    if len(feature_cols) >= 2:
        fig = px.scatter(
            X,
            x=feature_cols[0],
            y=feature_cols[1],
            color=clusters.astype(str),
            title="Clusters in feature space",
        )
        st.plotly_chart(fig, use_container_width=True)
