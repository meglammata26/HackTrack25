# pages/05_Gazoo_AI_Race_Engineer.py

import streamlit as st
from utils import styling, loader, ai_engine

styling.inject_base_css()
styling.render_banner()

st.title("Gazoo AI Race Engineer")

st.markdown(
    """
### Lap-by-Lap Coaching Mode (Gemini-powered)

Upload or select a GR telemetry file (e.g. `barber_sample.csv`) in the sidebar.  
Gazoo AI will compute per-lap stats (avg speed, throttle, brake, speed variance)
and then give you **driver-focused coaching**.
"""
)

# ----------------------------------------------------------------------
# Load telemetry
# ----------------------------------------------------------------------

df = loader.sidebar_data_selector()

if df is None or df.empty:
    st.info("Select or upload a telemetry CSV from the sidebar to begin.")
    st.stop()

st.markdown("##### Detected columns")
st.code(", ".join(df.columns.astype(str)), language="text")

# ----------------------------------------------------------------------
# Driver question input
# ----------------------------------------------------------------------

if "ai_query" not in st.session_state:
    st.session_state["ai_query"] = ""

user_question = st.text_area(
    "Ask Gazoo AI about your stint",
    value=st.session_state["ai_query"],
    key="ai_query",
    height=120,
    placeholder="Example: How does Lap 2 compare to Lap 3? Where am I losing time?",
)

st.markdown("---")

# ----------------------------------------------------------------------
# Run Gemini lap-by-lap coaching
# ----------------------------------------------------------------------

analyze_btn = st.button("Analyze Lap-by-Lap Telemetry", type="primary")

if analyze_btn:
    with st.spinner("Asking Gazoo AI Race Engineer..."):
        try:
            response_text, summary_df = ai_engine.gemini_race_engineer(
                df=df,
                user_question=user_question,
            )
            st.session_state["last_ai_response"] = response_text
            st.session_state["last_summary_df"] = summary_df
        except Exception as e:
            st.error(f"AI analysis failed: {e}")

# ----------------------------------------------------------------------
# Show results if we have them
# ----------------------------------------------------------------------

if "last_ai_response" in st.session_state:
    st.subheader("AI Coaching Summary")
    st.markdown(st.session_state["last_ai_response"])

if "last_summary_df" in st.session_state:
    st.subheader("Telemetry Summary Used for Coaching")
    st.dataframe(
        st.session_state["last_summary_df"],
        use_container_width=True,
    )

def generate_engineer_report(lap_times, sector_scores, recommendation, fatigue_index, confidence):
    best_lap = min(lap_times)
    best_lap_number = lap_times.index(best_lap) + 1
    best_sector = max(sector_scores, key=sector_scores.get)

    report = f"""


Fastest Lap Identified:
    Lap {best_lap_number}  ({best_lap:.3f} seconds)

Strongest Performance Sector:
    {best_sector}

Recommended Driver Adjustment:
    {recommendation}

Driver Performance Observation:
    Focus retained at {fatigue_index*100:.1f}% relative to start of stint

Model Confidence:
    {confidence:.1f}%

Report generated using telemetry, regression models, 
gaze prediction metrics, and clustering patterns.

"""
    return report

# ----------------------------------------------------------------------
# Display auto-generated engineer insight report
# ----------------------------------------------------------------------

st.header("AI Race Engineer Insight Report")

# Example placeholder values — replace with your real computed values
lap_times = [92.4, 91.7, 91.2, 91.8]
sector_scores = {"Sector 1": 76, "Sector 2": 81, "Sector 3": 88}
recommendation = "Brake 120ms earlier entering Turn 9 for improved stability."
fatigue_index = 0.82
confidence = 79.3

report_text = generate_engineer_report(
    lap_times,
    sector_scores,
    recommendation,
    fatigue_index,
    confidence
)

st.text(report_text)


# ----------------------------------------------------------------------
# (Optional) Simple text radio chat (no audio, no whisper, just text)
# ----------------------------------------------------------------------

st.markdown("---")
st.markdown("### Optional: Radio-Style Text Chat (no audio)")

if "radio_history" not in st.session_state:
    st.session_state["radio_history"] = []

radio_input = st.text_input(
    "Radio to engineer:",
    placeholder="Example: How's my consistency between Lap 1 and Lap 3?",
)

col1, col2 = st.columns([1, 3])
with col1:
    send_radio = st.button("Send Radio", use_container_width=True)

if send_radio and radio_input.strip():
    # Use the last summary (if exists) for context
    summary_df = st.session_state.get("last_summary_df")
    try:
        reply = ai_engine.engineer_reply(radio_input, summary_df=summary_df)
        st.session_state["radio_history"].append(("Driver", radio_input))
        st.session_state["radio_history"].append(("Engineer", reply))
    except Exception as e:
        st.error(f"Radio mode error: {e}")

if st.session_state["radio_history"]:
    st.markdown("#### Radio Transcript")
    for speaker, text in st.session_state["radio_history"]:
        if speaker == "Driver":
            st.markdown(f"**Driver:** {text}")
        else:
            st.markdown(f"**Engineer:** {text}")
