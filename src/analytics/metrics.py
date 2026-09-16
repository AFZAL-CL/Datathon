"""
src/analytics/metrics.py
========================
Phase 4 — Core metrics: overall student outcomes, grade statistics,
and financial/demographic breakdowns.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import numpy as np

log = logging.getLogger(__name__)

TARGET_COL = "Target"
TARGET_CLASSES = ["Graduate", "Dropout", "Enrolled"]


# ---------------------------------------------------------------------------
# Overall outcome metrics
# ---------------------------------------------------------------------------

def outcome_distribution(df: pd.DataFrame) -> dict[str, Any]:
    """
    Compute overall target class distribution.

    Returns
    -------
    {
        "counts": {"Graduate": N, "Dropout": N, "Enrolled": N},
        "percentages": {"Graduate": %, ...},
        "total": N,
    }
    """
    vc  = df[TARGET_COL].value_counts()
    pct = (df[TARGET_COL].value_counts(normalize=True) * 100).round(2)
    return {
        "counts":      {cls: int(vc.get(cls, 0)) for cls in TARGET_CLASSES},
        "percentages": {cls: float(pct.get(cls, 0.0)) for cls in TARGET_CLASSES},
        "total":       int(len(df)),
    }


# ---------------------------------------------------------------------------
# Breakdown by a dimension (categorical column)
# ---------------------------------------------------------------------------

def outcome_by_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """
    Cross-tabulate Target distribution by a given dimension column.

    Returns a DataFrame with index = dimension values,
    columns = Target classes + '_pct' variants.
    """
    if dimension not in df.columns:
        raise ValueError(f"Column '{dimension}' not found in DataFrame.")

    ct = pd.crosstab(df[dimension], df[TARGET_COL])
    # Ensure all 3 classes are present even if zero
    for cls in TARGET_CLASSES:
        if cls not in ct.columns:
            ct[cls] = 0
    ct = ct[TARGET_CLASSES]
    ct_pct = ct.div(ct.sum(axis=1), axis=0).multiply(100).round(2)
    ct_pct.columns = [f"{c}_pct" for c in ct_pct.columns]
    result = pd.concat([ct, ct_pct], axis=1)
    result.index.name = dimension
    result["total"] = ct.sum(axis=1)
    return result.reset_index()


# ---------------------------------------------------------------------------
# Academic performance metrics
# ---------------------------------------------------------------------------

def academic_performance_summary(df: pd.DataFrame) -> dict[str, Any]:
    """
    Descriptive statistics for grade and unit-count features,
    broken down by Target class.
    """
    perf_cols = [
        "Curricular units 1st sem (grade)",
        "Curricular units 2nd sem (grade)",
        "Curricular units 1st sem (approved)",
        "Curricular units 2nd sem (approved)",
        "Curricular units 1st sem (enrolled)",
        "Curricular units 2nd sem (enrolled)",
        "Curricular units 1st sem (evaluations)",
        "Curricular units 2nd sem (evaluations)",
        "Curricular units 1st sem (without evaluations)",
        "Curricular units 2nd sem (without evaluations)",
    ]
    existing = [c for c in perf_cols if c in df.columns]

    result: dict[str, Any] = {}
    for col in existing:
        stats_by_class: dict[str, Any] = {}
        for cls in TARGET_CLASSES:
            subset = df.loc[df[TARGET_COL] == cls, col]
            if subset.empty:
                continue
            stats_by_class[cls] = {
                "mean":   round(float(subset.mean()),  4),
                "median": round(float(subset.median()), 4),
                "std":    round(float(subset.std()),   4),
                "min":    round(float(subset.min()),   4),
                "max":    round(float(subset.max()),   4),
            }
        result[col] = stats_by_class
    return result


# ---------------------------------------------------------------------------
# Financial analysis
# ---------------------------------------------------------------------------

def financial_analysis(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Outcome breakdowns for Debtor, Tuition fees, Scholarship holder.
    """
    dimensions = {
        "debtor":          "Debtor",
        "tuition_status":  "Tuition fees up to date",
        "scholarship":     "Scholarship holder",
    }
    return {
        key: outcome_by_dimension(df, col)
        for key, col in dimensions.items()
        if col in df.columns
    }


# ---------------------------------------------------------------------------
# Demographic analysis
# ---------------------------------------------------------------------------

def demographic_analysis(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Outcome breakdowns for gender, displaced, international, age group.
    """
    dimensions = {
        "gender":        "Gender",
        "displaced":     "Displaced",
        "international": "International",
        "age_group":     "f_a_age_group",
    }
    return {
        key: outcome_by_dimension(df, col)
        for key, col in dimensions.items()
        if col in df.columns
    }


# ---------------------------------------------------------------------------
# Grade band analysis
# ---------------------------------------------------------------------------

def admission_grade_band_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Outcome by admission grade quartile band."""
    if "f_a_admission_band" not in df.columns:
        raise ValueError("Run preprocessing first to create 'f_a_admission_band'.")
    return outcome_by_dimension(df, "f_a_admission_band")


# ---------------------------------------------------------------------------
# Summary table: all key breakdowns at once
# ---------------------------------------------------------------------------

def run_all_metrics(df: pd.DataFrame) -> dict[str, Any]:
    """
    Run every metric function and collect results in a single dict.
    Safe: skips any breakdown if the column is absent.
    """
    log.info("Running all metrics on %d rows ...", len(df))

    dims_to_analyse = [
        "Course",
        "Gender",
        "Scholarship holder",
        "Tuition fees up to date",
        "Debtor",
        "Previous qualification",
        "Application mode",
        "Displaced",
        "International",
        "Daytime/evening attendance",
        "f_a_age_group",
        "f_a_admission_band",
        "f_a_financial_risk",
    ]

    results: dict[str, Any] = {
        "overall": outcome_distribution(df),
        "academic_performance": academic_performance_summary(df),
        "financial": financial_analysis(df),
        "demographic": demographic_analysis(df),
        "by_dimension": {},
    }

    for dim in dims_to_analyse:
        if dim in df.columns:
            try:
                results["by_dimension"][dim] = outcome_by_dimension(df, dim)
            except Exception as exc:
                log.warning("Skipped breakdown for '%s': %s", dim, exc)

    log.info("Metrics complete. Keys: %s", list(results.keys()))
    return results
