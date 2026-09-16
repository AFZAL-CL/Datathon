"""Transparent, distribution-derived risk indicators."""

from __future__ import annotations

import pandas as pd


def _tertile_labels(series: pd.Series) -> tuple[pd.Series, dict[str, float]]:
    """Label low/medium/high using observed 33rd/67th percentiles."""
    low = float(series.quantile(1 / 3))
    high = float(series.quantile(2 / 3))
    labels = pd.Series("MEDIUM", index=series.index)
    labels.loc[series <= low] = "HIGH"
    labels.loc[series > high] = "LOW"
    return labels, {"high_at_or_below": low, "low_above": high}


def add_risk_indicators(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, dict[str, float]]]:
    """Add admission-only and current-academic risk labels.

    Lower observed admission grade or academic progress is HIGH. Thresholds
    come from this dataset's tertiles, not hand-picked cutoffs.
    """
    result = df.copy()
    result["early_admission_risk"], admission_thresholds = _tertile_labels(
        result["Admission grade"]
    )
    result["current_academic_risk"], academic_thresholds = _tertile_labels(
        result["academic_progress"]
    )
    return result, {
        "Admission grade": admission_thresholds,
        "Academic progress": academic_thresholds,
    }
