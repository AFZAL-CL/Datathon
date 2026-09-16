"""
src/data/preprocessing.py
=========================
Phase 3 — Feature Engineering.

Creates interpretable derived features from the cleaned dataset.

Leakage policy:
  SCENARIO A — EARLY/ADMISSION RISK
      Features derived only from pre-enrolment / admission-time information.
      (demographics, prior qualifications, admission grade, financial/social flags)

  SCENARIO B — CURRENT ACADEMIC RISK
      All SCENARIO A features PLUS in-programme semester performance.

Rules:
  - DO NOT use Target to create any feature.
  - Document every formula explicitly in the docstring.
  - Structural zeros (grade = 0 for students with 0 approved units) are valid.
  - Avoid division by zero: use safe_div helper.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

ScenarioType = Literal["A", "B"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_div(numerator: pd.Series, denominator: pd.Series, fill: float = 0.0) -> pd.Series:
    """Element-wise division; returns fill where denominator == 0."""
    return numerator.where(denominator != 0, other=fill) / denominator.where(denominator != 0, other=1.0)


# ---------------------------------------------------------------------------
# SCENARIO A — Admission / Early-stage features only
# ---------------------------------------------------------------------------

def build_scenario_a_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build features available at or near enrolment time.

    Derived features (all prefixed with 'f_a_' to avoid name collisions):

    f_a_age_group
        Age banded into: '15-19', '20-24', '25-29', '30-39', '40+'
        Formula: pd.cut on 'Age at enrollment'

    f_a_admission_band
        Admission grade banded into quartiles: 'Q1','Q2','Q3','Q4'
        Formula: pd.qcut on 'Admission grade' into 4 equal-frequency bins

    f_a_prev_qual_band
        Previous qualification grade banded into quartiles
        Formula: pd.qcut on 'Previous qualification (grade)' into 4 equal-frequency bins

    f_a_financial_risk
        Composite financial stress indicator:
          Debtor=1 OR Tuition fees up to date=0 → HIGH
          Scholarship holder=1 AND Debtor=0 AND Tuition=1 → LOW
          else → MEDIUM

    f_a_parental_edu_level
        Average of mother's & father's qualification codes (higher = more educated)
        Formula: mean(Mother's qualification, Father's qualification)

    f_a_is_mature_student
        1 if Age at enrollment >= 23 (median), else 0
        Threshold derived from the median of 'Age at enrollment'

    f_a_first_choice
        1 if Application order == 1 (student's top-choice institution), else 0

    f_a_attended_daytime
        Alias: 1=daytime, 0=evening (renamed for clarity)
        Formula: same as 'Daytime/evening attendance'

    f_a_prior_higher_edu
        1 if Previous qualification code indicates any prior higher-education
          (codes 2,3,4,5,6,40,41,42,43 from the codebook)
        Else 0

    f_a_domestic_student
        1 if Nationality == 1 (Portuguese) AND International == 0
        Else 0
    """
    df = df.copy()

    # f_a_age_group
    df["f_a_age_group"] = pd.cut(
        df["Age at enrollment"],
        bins=[14, 19, 24, 29, 39, 120],
        labels=["15-19", "20-24", "25-29", "30-39", "40+"],
        right=True,
    ).astype(str)

    # f_a_admission_band (quartiles computed on this dataset's distribution)
    try:
        df["f_a_admission_band"] = pd.qcut(
            df["Admission grade"], q=4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop"
        ).astype(str)
    except ValueError:
        df["f_a_admission_band"] = "Q2"  # fallback if grade has no variance

    # f_a_prev_qual_band
    try:
        df["f_a_prev_qual_band"] = pd.qcut(
            df["Previous qualification (grade)"], q=4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop"
        ).astype(str)
    except ValueError:
        df["f_a_prev_qual_band"] = "Q2"

    # f_a_financial_risk
    high_risk = (df["Debtor"] == 1) | (df["Tuition fees up to date"] == 0)
    low_risk  = (df["Scholarship holder"] == 1) & (df["Debtor"] == 0) & (df["Tuition fees up to date"] == 1)
    df["f_a_financial_risk"] = "MEDIUM"
    df.loc[high_risk, "f_a_financial_risk"] = "HIGH"
    df.loc[low_risk & ~high_risk, "f_a_financial_risk"] = "LOW"

    # f_a_parental_edu_level
    df["f_a_parental_edu_level"] = (
        df["Mother's qualification"] + df["Father's qualification"]
    ) / 2.0

    # f_a_is_mature_student — threshold = median of age
    median_age = df["Age at enrollment"].median()
    df["f_a_is_mature_student"] = (df["Age at enrollment"] >= median_age).astype(int)
    log.info("f_a_is_mature_student threshold (median age): %.0f", median_age)

    # f_a_first_choice
    df["f_a_first_choice"] = (df["Application order"] == 1).astype(int)

    # f_a_attended_daytime
    df["f_a_attended_daytime"] = df["Daytime/evening attendance"].astype(int)

    # f_a_prior_higher_edu
    higher_edu_codes = {2, 3, 4, 5, 6, 40, 41, 42, 43}
    df["f_a_prior_higher_edu"] = df["Previous qualification"].isin(higher_edu_codes).astype(int)

    # f_a_domestic_student
    df["f_a_domestic_student"] = (
        (df["Nationality"] == 1) & (df["International"] == 0)
    ).astype(int)

    df["admission_grade_band"] = df["f_a_admission_band"]
    df["age_group"] = df["f_a_age_group"]
    df["financial_risk"] = df["f_a_financial_risk"]

    log.info("Scenario A features built: %d new columns", 10)
    return df


# ---------------------------------------------------------------------------
# SCENARIO B — In-programme performance features (adds to Scenario A)
# ---------------------------------------------------------------------------

def build_scenario_b_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build additional features using semester-level academic performance data.
    Intended for CURRENT ACADEMIC RISK modelling only.

    All features prefixed 'f_b_'.

    f_b_sem1_pass_rate
        Fraction of enrolled units passed in semester 1.
        Formula: approved_1 / enrolled_1   (0 if enrolled = 0)

    f_b_sem2_pass_rate
        Formula: approved_2 / enrolled_2   (0 if enrolled = 0)

    f_b_sem1_evaluation_rate
        Fraction of enrolled units that were evaluated in semester 1.
        Formula: evaluations_1 / enrolled_1  (0 if enrolled = 0)

    f_b_sem2_evaluation_rate
        Formula: evaluations_2 / enrolled_2  (0 if enrolled = 0)

    f_b_academic_progress
        Combined measure: (approved_1 + approved_2) / (enrolled_1 + enrolled_2)
        Formula: total_approved / total_enrolled  (0 if total enrolled = 0)
        Captures overall throughput across both semesters.

    f_b_academic_performance_score
        Average of the two semester grades, weighted by units approved.
        Formula: (grade_1 * approved_1 + grade_2 * approved_2)
                 / (approved_1 + approved_2)
        Returns 0 if no approved units in either semester.

    f_b_sem1_engagement
        Ratio of evaluations to enrolled units in semester 1.
        Proxy for student engagement.

    f_b_sem2_engagement
        Same for semester 2.

    f_b_no_evaluation_flag
        1 if student has units WITHOUT evaluations in BOTH semesters, else 0.
        Formula: (without_eval_1 > 0) AND (without_eval_2 > 0)

    f_b_credited_ratio
        Total credited units / total enrolled units (across both semesters).
        Formula: (credited_1 + credited_2) / (enrolled_1 + enrolled_2)

    f_b_grade_improvement
        sem2_grade - sem1_grade.
        Positive = improving, negative = declining.
        Set to 0 when no approved units in either semester.

    f_b_total_units_approved
        approved_1 + approved_2

    f_b_total_units_enrolled
        enrolled_1 + enrolled_2
    """
    df = df.copy()

    enrolled_1  = df["Curricular units 1st sem (enrolled)"]
    enrolled_2  = df["Curricular units 2nd sem (enrolled)"]
    approved_1  = df["Curricular units 1st sem (approved)"]
    approved_2  = df["Curricular units 2nd sem (approved)"]
    evals_1     = df["Curricular units 1st sem (evaluations)"]
    evals_2     = df["Curricular units 2nd sem (evaluations)"]
    grade_1     = df["Curricular units 1st sem (grade)"]
    grade_2     = df["Curricular units 2nd sem (grade)"]
    credited_1  = df["Curricular units 1st sem (credited)"]
    credited_2  = df["Curricular units 2nd sem (credited)"]
    no_eval_1   = df["Curricular units 1st sem (without evaluations)"]
    no_eval_2   = df["Curricular units 2nd sem (without evaluations)"]

    total_enrolled = enrolled_1 + enrolled_2
    total_approved = approved_1 + approved_2

    df["f_b_sem1_pass_rate"]         = safe_div(approved_1, enrolled_1)
    df["f_b_sem2_pass_rate"]         = safe_div(approved_2, enrolled_2)
    df["f_b_sem1_evaluation_rate"]   = safe_div(evals_1,    enrolled_1)
    df["f_b_sem2_evaluation_rate"]   = safe_div(evals_2,    enrolled_2)
    df["f_b_academic_progress"]      = safe_div(total_approved, total_enrolled)

    # Weighted average grade
    weighted_grade = grade_1 * approved_1 + grade_2 * approved_2
    df["f_b_academic_performance_score"] = safe_div(weighted_grade, total_approved)

    df["f_b_sem1_engagement"]        = safe_div(evals_1, enrolled_1)
    df["f_b_sem2_engagement"]        = safe_div(evals_2, enrolled_2)

    df["f_b_no_evaluation_flag"]     = ((no_eval_1 > 0) & (no_eval_2 > 0)).astype(int)
    df["f_b_credited_ratio"]         = safe_div(credited_1 + credited_2, total_enrolled)

    # Grade improvement: only meaningful when both semesters have approved units
    has_both = (approved_1 > 0) & (approved_2 > 0)
    df["f_b_grade_improvement"]      = np.where(has_both, grade_2 - grade_1, 0.0)

    df["f_b_total_units_approved"]   = total_approved
    df["f_b_total_units_enrolled"]   = total_enrolled

    df["semester_1_pass_rate"] = df["f_b_sem1_pass_rate"]
    df["semester_2_pass_rate"] = df["f_b_sem2_pass_rate"]
    df["semester_1_evaluation_rate"] = df["f_b_sem1_evaluation_rate"]
    df["semester_2_evaluation_rate"] = df["f_b_sem2_evaluation_rate"]
    df["academic_progress"] = df["f_b_academic_progress"]
    df["academic_performance_score"] = df["f_b_academic_performance_score"]
    df["attendance_mode"] = np.where(
        df["Daytime/evening attendance"] == 1, "Daytime", "Evening"
    )

    log.info("Scenario B features built: %d new columns", 13)
    return df


# ---------------------------------------------------------------------------
# Master pipeline
# ---------------------------------------------------------------------------

def build_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build Scenario A features, then Scenario B features, on the cleaned data."""
    df = build_scenario_a_features(df)
    df = build_scenario_b_features(df)
    return df


def get_scenario_a_feature_cols() -> list[str]:
    """Return the list of Scenario A (admission-only) feature column names."""
    return [
        "f_a_age_group", "f_a_admission_band", "f_a_prev_qual_band",
        "f_a_financial_risk", "f_a_parental_edu_level", "f_a_is_mature_student",
        "f_a_first_choice", "f_a_attended_daytime", "f_a_prior_higher_edu",
        "f_a_domestic_student",
    ]


def get_scenario_b_feature_cols() -> list[str]:
    """Return the list of Scenario B (in-programme) feature column names."""
    return [
        "f_b_sem1_pass_rate", "f_b_sem2_pass_rate",
        "f_b_sem1_evaluation_rate", "f_b_sem2_evaluation_rate",
        "f_b_academic_progress", "f_b_academic_performance_score",
        "f_b_sem1_engagement", "f_b_sem2_engagement",
        "f_b_no_evaluation_flag", "f_b_credited_ratio",
        "f_b_grade_improvement", "f_b_total_units_approved",
        "f_b_total_units_enrolled",
    ]


def save_processed(df: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    log.info("Saved analytics dataset to %s (%d rows × %d cols)", path, *df.shape)
