# pages/05_Gazoo_AI_Race_Engineer.py
import streamlit as st
from utils import styling, loader, ai_engine

styling.inject_base_css()
styling.render_banner()

st.title("Gazoo AI Race Engineer")

df = loader.sidebar_data_selector()
mapping = st.session_state.get("mapping", {})

speed_col = mapping.get("speed_col")
throttle_col = mapping.get("throttle_col")
brake_col = mapping.get("brake_col")
lap_id_col = mapping.get("lap_id_col")

st.markdown(
    """
Gazoo AI is running in **offline mode**:

- No API keys  
- No cloud calls  
- No rate limits or cost  
- Uses telemetry statistics + heuristics to simulate a race engineer  
"""
)

if "ai_query" not in st.session_state:
    st.session_state["ai_query"] = ""

user_question = st.text_area(
    "Ask Gazoo AI:",
    value=st.session_state["ai_query"],
    height=120,
    key="ai_query",
    placeholder="Example: Where am I losing time? Which corners are inconsistent?",
)

if st.button("Analyze Telemetry"):
    response = ai_engine.offline_gazoo_response(
        df,
        user_question,
        speed_col=speed_col,
        throttle_col=throttle_col,
        brake_col=brake_col,
        lap_id_col=lap_id_col,
    )
    st.markdown(response)
