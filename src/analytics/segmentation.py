"""
src/analytics/segmentation.py
==============================
Phase 4 — Student segmentation for dashboard use.

Produces student-level segment labels and aggregated segment tables.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

TARGET_COL = "Target"


def assign_age_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Add 'age_group' column based on enrollment age."""
    bins   = [14, 19, 24, 29, 39, 120]
    labels = ["15-19", "20-24", "25-29", "30-39", "40+"]
    df = df.copy()
    df["age_group"] = pd.cut(
        df["Age at enrollment"], bins=bins, labels=labels, right=True
    ).astype(str)
    return df


def assign_grade_bands(df: pd.DataFrame) -> pd.DataFrame:
    """Add quartile-based grade band columns for admission and prior qualification."""
    df = df.copy()
    for col, label in [
        ("Admission grade", "admission_grade_band"),
        ("Previous qualification (grade)", "prev_qual_grade_band"),
    ]:
        if col not in df.columns:
            continue
        try:
            df[label] = pd.qcut(
                df[col], q=4, labels=["Q1 (Low)", "Q2", "Q3", "Q4 (High)"],
                duplicates="drop",
            ).astype(str)
        except ValueError:
            df[label] = "Q2"
    return df


def segment_by_financial_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a single 'financial_segment' column combining debtor/tuition/scholarship.

    Segments:
      'Scholarship, No Debt'  : Scholarship holder, not debtor, tuition OK
      'Scholarship, At Risk'  : Scholarship holder, but debtor or tuition overdue
      'Stable (No Scholarship)': No scholarship, not debtor, tuition OK
      'Financial Risk'        : Debtor or tuition overdue (no scholarship)
    """
    df = df.copy()
    cond_scholar = df["Scholarship holder"] == 1
    cond_debtor  = df["Debtor"] == 1
    cond_tuition = df["Tuition fees up to date"] == 0
    at_financial_risk = cond_debtor | cond_tuition

    df["financial_segment"] = "Stable (No Scholarship)"
    df.loc[~cond_scholar & at_financial_risk,              "financial_segment"] = "Financial Risk"
    df.loc[ cond_scholar & ~at_financial_risk,             "financial_segment"] = "Scholarship, No Debt"
    df.loc[ cond_scholar & at_financial_risk,              "financial_segment"] = "Scholarship, At Risk"
    return df


def build_course_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate key metrics per Course.

    Returns a DataFrame with one row per course.
    """
    if "Course" not in df.columns:
        return pd.DataFrame()

    grp = df.groupby("Course")
    summary = pd.DataFrame()
    summary["n_students"]       = grp[TARGET_COL].count()
    summary["dropout_pct"]      = (grp[TARGET_COL].apply(lambda x: (x == "Dropout").mean()) * 100).round(2)
    summary["graduate_pct"]     = (grp[TARGET_COL].apply(lambda x: (x == "Graduate").mean()) * 100).round(2)
    summary["enrolled_pct"]     = (grp[TARGET_COL].apply(lambda x: (x == "Enrolled").mean()) * 100).round(2)

    if "Curricular units 2nd sem (grade)" in df.columns:
        summary["avg_sem2_grade"] = grp["Curricular units 2nd sem (grade)"].mean().round(3)

    if "Admission grade" in df.columns:
        summary["avg_admission_grade"] = grp["Admission grade"].mean().round(3)

    summary = summary.reset_index()
    return summary


def build_segment_table(df: pd.DataFrame, segment_col: str) -> pd.DataFrame:
    """
    Generic segment → outcome cross-tabulation with percentage columns.
    """
    if segment_col not in df.columns:
        raise ValueError(f"Column '{segment_col}' not found.")

    result = pd.crosstab(df[segment_col], df[TARGET_COL])
    for cls in ["Graduate", "Dropout", "Enrolled"]:
        if cls not in result.columns:
            result[cls] = 0
    result = result[["Graduate", "Dropout", "Enrolled"]]
    total = result.sum(axis=1)
    for cls in ["Graduate", "Dropout", "Enrolled"]:
        result[f"{cls}_pct"] = (result[cls] / total * 100).round(2)
    result["total"] = total
    return result.reset_index()


def run_all_segments(df: pd.DataFrame) -> dict[str, Any]:
    """Run all segmentation functions and collect results."""
    log.info("Running segmentation ...")
    df = assign_age_groups(df)
    df = assign_grade_bands(df)
    df = segment_by_financial_status(df)

    segments: dict[str, Any] = {
        "enriched_df":      df,
        "by_age_group":     build_segment_table(df, "age_group"),
        "by_grade_band":    build_segment_table(df, "admission_grade_band") if "admission_grade_band" in df.columns else pd.DataFrame(),
        "by_financial_seg": build_segment_table(df, "financial_segment"),
        "by_course":        build_course_summary(df),
    }
    log.info("Segmentation complete.")
    return segments
