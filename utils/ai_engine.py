# utils/ai_engine.py

import os
import pandas as pd
import google.generativeai as genai

# ----------------------------------------------------------------------
# GEMINI CONFIG
# ----------------------------------------------------------------------

# You can either:
#  - export GEMINI_API_KEY in your shell, OR
#  - hardcode it here if you're just hacking locally.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "PASTE_YOUR_KEY_HERE"

if not GEMINI_API_KEY or GEMINI_API_KEY == "PASTE_YOUR_KEY_HERE":
    print("[ai_engine] Warning: GEMINI_API_KEY not configured. Gemini calls will fail.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

TEXT_MODEL = "models/gemini-2.5-flash"


# ----------------------------------------------------------------------
# TELEMETRY METRICS (supports barber_sample LONG FORMAT)
# ----------------------------------------------------------------------

def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-lap summary metrics for feedback.

    Supports:
      1) Wide format with columns: lap, speed, aps, pbrake_f
      2) Long format like barber_sample with:
         lap, telemetry_name, telemetry_value
            - speed     -> avg_speed / var_speed
            - aps       -> avg_throttle
            - pbrake_f  -> avg_brake
    """
    if "lap" not in df.columns:
        raise ValueError("Expected a 'lap' column in the telemetry dataframe.")

    lap_col = "lap"

    # ---- Case 1: wide format -------------------------------------------------
    wide_cols = {"speed", "aps", "pbrake_f"}
    if wide_cols.issubset(df.columns):
        g = df.groupby(lap_col)
        summary = g.agg(
            avg_speed=("speed", "mean"),
            avg_throttle=("aps", "mean"),
            avg_brake=("pbrake_f", "mean"),
            var_speed=("speed", "var"),
        ).reset_index()
        return summary.round(2)

    # ---- Case 2: barber_sample-style long format -----------------------------
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

        # Base frame: all laps present in the data
        summary = pd.DataFrame({lap_col: sorted(df[lap_col].dropna().unique())})

        summary = summary.merge(
            speed_mean.rename("avg_speed"),
            on=lap_col,
            how="left",
        )
        summary = summary.merge(
            throttle_mean.rename("avg_throttle"),
            on=lap_col,
            how="left",
        )
        summary = summary.merge(
            brake_mean.rename("avg_brake"),
            on=lap_col,
            how="left",
        )
        summary = summary.merge(
            speed_var.rename("var_speed"),
            on=lap_col,
            how="left",
        )

        return summary.round(2)

    # ---- Unsupported shape ---------------------------------------------------
    raise ValueError(
        "Telemetry dataframe must either be:\n"
        "  - wide format with columns: lap, speed, aps, pbrake_f\n"
        "  - or long format with: lap, telemetry_name, telemetry_value"
    )


# ----------------------------------------------------------------------
# GEMINI RACE ENGINEER (LAP-BY-LAP COACHING)
# ----------------------------------------------------------------------

def gemini_race_engineer(df: pd.DataFrame, user_question: str):
    """
    Generate textual race analysis using Gemini based on per-lap metrics.

    Returns:
        (response_text: str, summary_df: pd.DataFrame)
    """
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
- No disclaimers, no apologies, no fluff
"""

    if not GEMINI_API_KEY or GEMINI_API_KEY == "PASTE_YOUR_KEY_HERE":
        raise RuntimeError("GEMINI_API_KEY is not configured; cannot call Gemini API.")

    model = genai.GenerativeModel(TEXT_MODEL)
    response = model.generate_content(prompt)

    return response.text, summary


# ----------------------------------------------------------------------
# TEXT-ONLY RADIO CONVERSATION (OPTIONAL, NO AUDIO)
# ----------------------------------------------------------------------

def engineer_reply(user_text: str, summary_df: pd.DataFrame | None = None) -> str:
    """
    Generate a short 'radio' reply from the engineer.
    Text-only. No audio / TTS.

    You can call this from a simple chat UI if you want,
    but it's not required for lap-by-lap coaching to work.
    """
    telemetry_part = ""
    if summary_df is not None and not summary_df.empty:
        telemetry_part = f"\nTelemetry Summary (per lap):\n{summary_df.to_markdown(index=False)}\n"

    prompt = f"""
You are a calm British motorsport race engineer.
Reply like you're on team radio. Short, direct, no fluff.

{telemetry_part}

Driver radio:
"{user_text}"

Engineer, respond in at most 2–3 short sentences:
"""

    if not GEMINI_API_KEY or GEMINI_API_KEY == "PASTE_YOUR_KEY_HERE":
        raise RuntimeError("GEMINI_API_KEY is not configured; cannot call Gemini API.")

    model = genai.GenerativeModel(TEXT_MODEL)
    result = model.generate_content(prompt)
    return result.text
