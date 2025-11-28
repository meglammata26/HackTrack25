# utils/ai_engine.py
import pandas as pd
import numpy as np


def _safe_series(df, col):
    if col is None or col not in df.columns:
        return None
    s = df[col]
    if s.dtype == object:
        s = pd.to_numeric(s, errors="coerce")
    return s.replace([np.inf, -np.inf], np.nan)


def compute_offline_metrics(df: pd.DataFrame,
                            speed_col=None,
                            throttle_col=None,
                            brake_col=None,
                            lap_id_col=None):
    metrics = {}

    s_speed = _safe_series(df, speed_col)
    s_throttle = _safe_series(df, throttle_col)
    s_brake = _safe_series(df, brake_col)

    if s_speed is not None:
        metrics["avg_speed"] = float(s_speed.mean())
        metrics["max_speed"] = float(s_speed.max())
        metrics["speed_std"] = float(s_speed.std())

    if s_throttle is not None:
        metrics["avg_throttle"] = float(s_throttle.mean())
        metrics["throttle_std"] = float(s_throttle.std())
        metrics["throttle_aggression"] = float((s_throttle >= 80).mean() * 100.0)

    if s_brake is not None:
        metrics["avg_brake"] = float(s_brake.mean())
        metrics["brake_std"] = float(s_brake.std())
        mean_b = s_brake.mean()
        std_b = s_brake.std()
        if mean_b > 0:
            cv = std_b / mean_b
            score = max(0.0, min(100.0, 100.0 * (1.2 - cv)))
            metrics["brake_consistency_score"] = float(score)

    if lap_id_col and lap_id_col in df.columns and s_speed is not None:
        try:
            lap_speed = df.groupby(lap_id_col)[speed_col].mean()
            metrics["lap_avg_speed_mean"] = float(lap_speed.mean())
            metrics["lap_avg_speed_std"] = float(lap_speed.std())
            metrics["lap_avg_speed_min"] = float(lap_speed.min())
            metrics["lap_avg_speed_max"] = float(lap_speed.max())
        except Exception:
            pass

    return metrics


def offline_gazoo_response(df: pd.DataFrame,
                           user_question: str,
                           speed_col=None,
                           throttle_col=None,
                           brake_col=None,
                           lap_id_col=None) -> str:
    metrics = compute_offline_metrics(
        df,
        speed_col=speed_col,
        throttle_col=throttle_col,
        brake_col=brake_col,
        lap_id_col=lap_id_col,
    )

    lines = []
    lines.append("## Gazoo AI (Offline Race Engineer)")
    lines.append("")
    lines.append("_Running fully offline — using telemetry statistics and heuristics._")
    lines.append("")

    if user_question.strip():
        lines.append("**Driver / Engineer Question**")
        lines.append("")
        lines.append(f"> {user_question.strip()}")
        lines.append("")

    lines.append("### Global Pace Snapshot")
    lines.append("")

    if "avg_speed" in metrics:
        lines.append(
            f"- Average speed across the stint: **{metrics['avg_speed']:.1f} units** "
            f"(max: **{metrics.get('max_speed', 0):.1f}**)."
        )
    if "speed_std" in metrics:
        lines.append(
            f"- Speed variability (σ): **{metrics['speed_std']:.1f} units** "
            "(higher = more on/off the throttle or more traffic influence)."
        )
    if "avg_throttle" in metrics:
        lines.append(
            f"- Average throttle: **{metrics['avg_throttle']:.1f}%** "
            f"(time >80% throttle: ~**{metrics.get('throttle_aggression', 0):.1f}%**)."
        )
    if "avg_brake" in metrics:
        lines.append(
            f"- Average brake signal: **{metrics['avg_brake']:.1f}** "
            "(scale depends on sensor; higher = more time spent braking)."
        )

    lines.append("")

    if "lap_avg_speed_std" in metrics and "lap_avg_speed_mean" in metrics:
        lap_std = metrics["lap_avg_speed_std"]
        lap_mean = metrics["lap_avg_speed_mean"]
        lap_cv = lap_std / lap_mean if lap_mean > 0 else 0.0

        lines.append("### Lap-to-Lap Consistency")
        lines.append("")
        lines.append(
            f"- Avg lap speed: **{lap_mean:.1f}** with σ = **{lap_std:.1f}** "
            f"(relative variation: **{lap_cv*100:.1f}%**)."
        )

        if lap_cv < 0.03:
            lines.append("- Laps are **very consistent** — good race trim behaviour.")
        elif lap_cv < 0.07:
            lines.append("- Laps are **reasonably consistent** — a few small mistakes or traffic.")
        else:
            lines.append("- Laps are **quite variable** — braking points and exits likely change lap-to-lap.")

        if "lap_avg_speed_min" in metrics and "lap_avg_speed_max" in metrics:
            lines.append(
                f"- Slowest vs fastest lap avg speed: "
                f"**{metrics['lap_avg_speed_min']:.1f} → {metrics['lap_avg_speed_max']:.1f}**."
            )

        lines.append("")

    if "brake_consistency_score" in metrics:
        score = metrics["brake_consistency_score"]
        lines.append("### Braking Style")
        lines.append("")
        lines.append(f"- Braking consistency score (0–100): **{score:.1f}**.")
        if score >= 80:
            lines.append("- Braking is **very consistent** — markers are well defined.")
        elif score >= 60:
            lines.append("- Braking is **fairly consistent**, but a few corners are still unstable.")
        else:
            lines.append("- Braking is **inconsistent** — often a sign of uncertainty on corner entry.")
        lines.append("")

    if "throttle_aggression" in metrics:
        thr_agg = metrics["throttle_aggression"]
        lines.append("### Throttle Application")
        lines.append("")
        lines.append(f"- Time above 80% throttle: **{thr_agg:.1f}%** of samples.")
        if thr_agg < 40:
            lines.append("- Not much time at full throttle — likely early lifting or cautious exits.")
        elif thr_agg < 70:
            lines.append("- Throttle usage is **balanced** — some margin left for exits/straights.")
        else:
            lines.append("- Throttle usage is **very aggressive** — qualifying-style, watch for traction issues.")
        lines.append("")

    lines.append("### High-Level Recommendations")
    lines.append("")
    lines.append("- Focus on **2–3 key corners** rather than the whole lap at once.")
    lines.append("- On entry: aim for **smooth brake release** so the car rotates the same way every lap.")
    lines.append("- On exit: use **progressive throttle** to avoid on/off steps in mid-speed corners.")
    lines.append("- Once consistency is stable, start moving braking points a little deeper where comfortable.")

    return "\n".join(lines)
