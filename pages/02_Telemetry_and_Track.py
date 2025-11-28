# pages/02_Telemetry_and_Track.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils import styling, loader

styling.inject_base_css()
styling.render_banner()

st.title("Telemetry and Track Visuals")

df = loader.sidebar_data_selector()
cols = list(df.columns)
mapping = st.session_state.get("mapping", {})

def default_idx(name_key, fallback="<none>"):
    name = mapping.get(name_key)
    if name and name in cols:
        return 1 + cols.index(name)
    return 0

speed_col = st.sidebar.selectbox("Speed", ["<none>"] + cols, index=default_idx("speed_col"))
distance_col = st.sidebar.selectbox("Distance / LapDist", ["<none>"] + cols, index=0)
time_col = st.sidebar.selectbox("Timestamp", ["<none>"] + cols, index=default_idx("time_col"))
throttle_col = st.sidebar.selectbox("Throttle %", ["<none>"] + cols, index=default_idx("throttle_col"))
brake_col = st.sidebar.selectbox("Brake", ["<none>"] + cols, index=default_idx("brake_col"))
lat_col = st.sidebar.selectbox("Latitude", ["<none>"] + cols, index=default_idx("lat_col"))
lon_col = st.sidebar.selectbox("Longitude", ["<none>"] + cols, index=default_idx("lon_col"))

# update mapping
st.session_state["mapping"].update(
    dict(
        speed_col=None if speed_col == "<none>" else speed_col,
        distance_col=None if distance_col == "<none>" else distance_col,
        time_col=None if time_col == "<none>" else time_col,
        throttle_col=None if throttle_col == "<none>" else throttle_col,
        brake_col=None if brake_col == "<none>" else brake_col,
        lat_col=None if lat_col == "<none>" else lat_col,
        lon_col=None if lon_col == "<none>" else lon_col,
        lap_id_col=mapping.get("lap_id_col"),
    )
)

if speed_col != "<none>" and distance_col != "<none>":
    st.subheader("Speed vs Distance")
    fig = px.line(
        df.sort_values(distance_col),
        x=distance_col,
        y=speed_col,
        labels={distance_col: "Distance", speed_col: "Speed"},
    )
    st.plotly_chart(fig, use_container_width=True)

if time_col != "<none>":
    st.subheader("Throttle / Brake vs Time")
    df_ts = df.sort_values(time_col)
    fig = go.Figure()
    if throttle_col != "<none>":
        fig.add_trace(
            go.Scatter(x=df_ts[time_col], y=df_ts[throttle_col],
                       name="Throttle", mode="lines")
        )
    if brake_col != "<none>":
        fig.add_trace(
            go.Scatter(x=df_ts[time_col], y=df_ts[brake_col],
                       name="Brake", mode="lines")
        )
    fig.update_layout(xaxis_title=time_col)
    st.plotly_chart(fig, use_container_width=True)

if lat_col != "<none>" and lon_col != "<none>":
    st.subheader("GPS Track Map")
    fig_map = px.scatter(
        df,
        x=lon_col,
        y=lat_col,
        color=df[speed_col] if speed_col != "<none>" else None,
        labels={lon_col: "Longitude", lat_col: "Latitude"},
    )
    fig_map.update_yaxes(scaleanchor="x", scaleratio=1)
    st.plotly_chart(fig_map, use_container_width=True)
