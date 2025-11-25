# pages/03_Regression_and_Classification.py
import streamlit as st
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score, confusion_matrix
import pandas as pd

from utils import styling, loader

styling.inject_base_css()
styling.render_banner()

st.title("Regression & Fast/Slow Classification")

df = loader.sidebar_data_selector()
numeric_cols = df.select_dtypes(include="number").columns.tolist()

mapping = st.session_state.get("mapping", {})
lap_id_col = mapping.get("lap_id_col")

target_col = st.sidebar.selectbox("Numeric target", numeric_cols)
test_size = st.sidebar.slider("Test size", 0.1, 0.5, 0.2, 0.05)
n_estimators = st.sidebar.slider("Random Forest trees", 50, 400, 200, 50)
fast_quantile = st.sidebar.slider("Fast quantile (lower is faster)", 0.1, 0.9, 0.3, 0.05)

drop_cols = []
if lap_id_col:
    drop_cols.append(lap_id_col)

X, y, feature_cols = loader.build_ml_matrices(df, target_col, drop_cols)

st.write(f"ML matrix: {X.shape[0]} samples × {X.shape[1]} features (target: `{target_col}`)")

st.header("Random Forest Regression")

if st.button("Train regression model"):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    reg = RandomForestRegressor(n_estimators=n_estimators, random_state=42, n_jobs=-1)
    reg.fit(X_train, y_train)
    y_pred = reg.predict(X_test)

    st.subheader("Metrics")
    st.write(f"R²: {r2_score(y_test, y_pred):.3f}")
    st.write(f"MAE: {mean_absolute_error(y_test, y_pred):.3f}")

    importances = reg.feature_importances_
    fi_df = (
        pd.DataFrame({"feature": feature_cols, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    fig = px.bar(fi_df.head(20), x="feature", y="importance",
                 title="Top predictive features")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

st.header("Fast/Slow classifier")

threshold = y.quantile(fast_quantile)
y_bin = (y <= threshold).astype(int)
st.write(f"Fast threshold on `{target_col}`: {threshold:.3f} (quantile {fast_quantile:.2f})")

if st.button("Train classifier"):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_bin, test_size=test_size, random_state=42
    )
    clf = RandomForestClassifier(n_estimators=n_estimators, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    st.subheader("Accuracy")
    st.write(f"{acc:.3f}")

    st.subheader("Confusion matrix")
    st.dataframe(
        pd.DataFrame(
            cm,
            index=["True slow (0)", "True fast (1)"],
            columns=["Pred slow (0)", "Pred fast (1)"],
        )
    )
