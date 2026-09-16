"""
src/analytics/insights.py
=========================
Phase 4 — Narrative insight generators.

Produces concise, data-driven text insights for each analytical dimension.
These are used to populate the ANALYTICS.md report.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)

TARGET_COL = "Target"


def _dropout_rate(df: pd.DataFrame) -> float:
    return round((df[TARGET_COL] == "Dropout").mean() * 100, 2)


def _graduate_rate(df: pd.DataFrame) -> float:
    return round((df[TARGET_COL] == "Graduate").mean() * 100, 2)


# ---------------------------------------------------------------------------
# Individual insight generators
# ---------------------------------------------------------------------------

def insight_overall(df: pd.DataFrame) -> dict[str, Any]:
    total = len(df)
    vc = df[TARGET_COL].value_counts()
    return {
        "total_students":  total,
        "graduate_count":  int(vc.get("Graduate", 0)),
        "dropout_count":   int(vc.get("Dropout", 0)),
        "enrolled_count":  int(vc.get("Enrolled", 0)),
        "dropout_rate":    _dropout_rate(df),
        "graduate_rate":   _graduate_rate(df),
    }


def insight_gender(df: pd.DataFrame) -> dict[str, Any]:
    if "Gender" not in df.columns:
        return {}
    male   = df[df["Gender"] == 1]
    female = df[df["Gender"] == 0]
    return {
        "male_count":       len(male),
        "female_count":     len(female),
        "male_dropout_pct":   _dropout_rate(male),
        "female_dropout_pct": _dropout_rate(female),
        "male_graduate_pct":  _graduate_rate(male),
        "female_graduate_pct":_graduate_rate(female),
        "note": "Gender=1 is male, Gender=0 is female per UCI codebook.",
    }


def insight_scholarship(df: pd.DataFrame) -> dict[str, Any]:
    if "Scholarship holder" not in df.columns:
        return {}
    scholar     = df[df["Scholarship holder"] == 1]
    non_scholar = df[df["Scholarship holder"] == 0]
    return {
        "scholarship_n":              len(scholar),
        "non_scholarship_n":          len(non_scholar),
        "scholarship_dropout_pct":    _dropout_rate(scholar),
        "non_scholarship_dropout_pct":_dropout_rate(non_scholar),
        "scholarship_graduate_pct":   _graduate_rate(scholar),
    }


def insight_tuition(df: pd.DataFrame) -> dict[str, Any]:
    if "Tuition fees up to date" not in df.columns:
        return {}
    paid   = df[df["Tuition fees up to date"] == 1]
    unpaid = df[df["Tuition fees up to date"] == 0]
    return {
        "tuition_current_n":         len(paid),
        "tuition_overdue_n":         len(unpaid),
        "overdue_dropout_pct":       _dropout_rate(unpaid),
        "current_dropout_pct":       _dropout_rate(paid),
        "overdue_graduate_pct":      _graduate_rate(unpaid),
        "current_graduate_pct":      _graduate_rate(paid),
    }


def insight_debtor(df: pd.DataFrame) -> dict[str, Any]:
    if "Debtor" not in df.columns:
        return {}
    debtor     = df[df["Debtor"] == 1]
    non_debtor = df[df["Debtor"] == 0]
    return {
        "debtor_n":            len(debtor),
        "non_debtor_n":        len(non_debtor),
        "debtor_dropout_pct":  _dropout_rate(debtor),
        "debtor_graduate_pct": _graduate_rate(debtor),
        "non_debtor_dropout_pct":  _dropout_rate(non_debtor),
    }


def insight_age(df: pd.DataFrame) -> dict[str, Any]:
    if "Age at enrollment" not in df.columns:
        return {}
    median_age = float(df["Age at enrollment"].median())
    p75_age    = float(df["Age at enrollment"].quantile(0.75))
    mature     = df[df["Age at enrollment"] >= median_age]
    young      = df[df["Age at enrollment"] < median_age]
    return {
        "median_age":              median_age,
        "p75_age":                 p75_age,
        "mature_student_dropout_pct": _dropout_rate(mature),
        "young_student_dropout_pct":  _dropout_rate(young),
    }


def insight_displaced(df: pd.DataFrame) -> dict[str, Any]:
    if "Displaced" not in df.columns:
        return {}
    disp     = df[df["Displaced"] == 1]
    non_disp = df[df["Displaced"] == 0]
    return {
        "displaced_n":           len(disp),
        "non_displaced_n":       len(non_disp),
        "displaced_dropout_pct": _dropout_rate(disp),
        "non_displaced_dropout_pct": _dropout_rate(non_disp),
    }


def insight_academic_performance(df: pd.DataFrame) -> dict[str, Any]:
    """Compare grade statistics between Dropout and Graduate groups."""
    grade_cols = [
        "Curricular units 1st sem (grade)",
        "Curricular units 2nd sem (grade)",
    ]
    result: dict[str, Any] = {}
    for col in grade_cols:
        if col not in df.columns:
            continue
        result[col] = {
            cls: {
                "mean": round(float(df.loc[df[TARGET_COL] == cls, col].mean()), 3),
                "std":  round(float(df.loc[df[TARGET_COL] == cls, col].std()),  3),
            }
            for cls in ["Graduate", "Dropout", "Enrolled"]
        }
    return result


def insight_macro_economics(df: pd.DataFrame) -> dict[str, Any]:
    """
    Basic statistics for macro-economic contextual variables.
    These are NOT student-level features; they reflect national conditions.
    """
    macro_cols = ["Unemployment rate", "Inflation rate", "GDP"]
    result: dict[str, Any] = {}
    for col in macro_cols:
        if col not in df.columns:
            continue
        dropout_mean = df.loc[df[TARGET_COL] == "Dropout", col].mean()
        grad_mean    = df.loc[df[TARGET_COL] == "Graduate", col].mean()
        result[col] = {
            "overall_mean":    round(float(df[col].mean()), 4),
            "overall_unique_vals": int(df[col].nunique()),
            "dropout_mean":    round(float(dropout_mean), 4),
            "graduate_mean":   round(float(grad_mean),    4),
            "limitation": (
                "This is a national quarterly indicator shared across all students enrolled "
                "in the same period. Its variance may reflect cohort timing rather than "
                "individual risk. Use with caution in predictive models."
            ),
        }
    return result


def run_all_insights(df: pd.DataFrame) -> dict[str, Any]:
    """Collect all insight dicts into a single report structure."""
    log.info("Generating insights ...")
    return {
        "overall":              insight_overall(df),
        "gender":               insight_gender(df),
        "scholarship":          insight_scholarship(df),
        "tuition":              insight_tuition(df),
        "debtor":               insight_debtor(df),
        "age":                  insight_age(df),
        "displaced":            insight_displaced(df),
        "academic_performance": insight_academic_performance(df),
        "macro_economics":      insight_macro_economics(df),
    }
