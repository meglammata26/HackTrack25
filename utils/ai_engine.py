# utils/ai_engine.py

import os
import pandas as pd
import streamlit as st
import google.generativeai as genai

# ----------------------------------------------------------------------
# GOOGLE AI / GEMINI CONFIG (UPDATED FOR NEW SDK)
# ----------------------------------------------------------------------

# Priority:
# 1. .streamlit/secrets.toml
# 2. GOOGLE_API_KEY in environment
# 3. GEMINI_API_KEY (legacy fallback)

GOOGLE_API_KEY = (
    st.secrets.get("GOOGLE_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
)

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "No API key found.\n"
        "Add GOOGLE_API_KEY to `.streamlit/secrets.toml` or export it in your environment."
    )

genai.configure(api_key=GOOGLE_API_KEY)

TEXT_MODEL = "models/gemini-2.5-flash"


# ----------------------------------------------------------------------
# TELEMETRY METRICS (supports wide or barber long format)
# ----------------------------------------------------------------------

def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if "lap" not in df.columns:
        raise ValueError("Expected a 'lap' column in the telemetry dataframe.")

    lap_col = "lap"
    wide_cols = {"speed", "aps", "pbrake_f"}

    # --- WIDE FORMAT ----------------------------------------------------------
    if wide_cols.issubset(df.columns):
        g = df.groupby(lap_col)
        summary = g.agg(
            avg_speed=("speed", "mean"),
            avg_throttle=("aps", "mean"),
            avg_brake=("pbrake_f", "mean"),
            var_speed=("speed", "var"),
        ).reset_index()
        return summary.round(2)

    # --- LONG FORMAT (barber_sample style) -----------------------------------
    if {"telemetry_name", "telemetry_value"}.issubset(df.columns):
        name_col = "telemetry_name"
        value_col = "telemetry_value"

        def agg_metric(name: str, agg: str):
            sub = df[df[name_col] == name]
            if sub.empty:
                return pd.Series(dtype=float)
            return sub.groupby(lap_col)[value_col].agg(agg)

        speed_mean = agg_metric("speed", "mean")
        speed_var = agg_metric("speed", "var")
        throttle_mean = agg_metric("aps", "mean")
        brake_mean = agg_metric("pbrake_f", "mean")

        summary = pd.DataFrame({lap_col: sorted(df[lap_col].dropna().unique())})

        summary = summary.merge(speed_mean.rename("avg_speed"), on=lap_col, how="left")
        summary = summary.merge(throttle_mean.rename("avg_throttle"), on=lap_col, how="left")
        summary = summary.merge(brake_mean.rename("avg_brake"), on=lap_col, how="left")
        summary = summary.merge(speed_var.rename("var_speed"), on=lap_col, how="left")

        return summary.round(2)

    raise ValueError(
        "Telemetry must be either:\n"
        "- Wide format with: lap, speed, aps, pbrake_f\n"
        "- Long format with: lap, telemetry_name, telemetry_value"
    )


# ----------------------------------------------------------------------
# MAIN LAP-BY-LAP GEMINI RACE ENGINEER
# ----------------------------------------------------------------------

def gemini_race_engineer(df: pd.DataFrame, user_question: str):
    summary = compute_metrics(df)

    if not user_question.strip():
        user_question = "Give me a lap-by-lap coaching summary and where I'm losing time."

    prompt = f"""
You are a calm, precise British motorsport race engineer.
Give direct, actionable driving feedback using ONLY the telemetry summary below.

Telemetry Summary (per lap):
{summary.to_markdown(index=False)}

Driver Question:
{user_question}

Provide:
- Key weaknesses
- Lap-by-lap comparison
- Actionable improvement steps
- No disclaimers, no apologies
"""

    model = genai.GenerativeModel(TEXT_MODEL)
    response = model.generate_content(prompt)

    return response.text, summary


# ----------------------------------------------------------------------
# SHORT RADIO-STYLE GEMINI REPLY
# ----------------------------------------------------------------------

def engineer_reply(user_text: str, summary_df: pd.DataFrame | None = None) -> str:
    telemetry_part = ""
    if summary_df is not None and not summary_df.empty:
        telemetry_part = (
            f"\nTelemetry Summary (per lap):\n"
            f"{summary_df.to_markdown(index=False)}\n"
        )

    prompt = f"""
You are a calm British motorsport race engineer.
Reply like you're on team radio. Short, direct, no fluff.

{telemetry_part}

Driver radio:
"{user_text}"

Engineer, respond in at most 2–3 short sentences:
"""

    model = genai.GenerativeModel(TEXT_MODEL)
    reply = model.generate_content(prompt)

    return reply.text
