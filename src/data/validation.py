"""
src/data/validation.py
======================
Phase 2 — Validation layer.

Compares raw vs cleaned DataFrames and produces a structured validation report.
Raises RuntimeError if hard failures are detected (row loss, new nulls, etc.).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)

EXPECTED_ROW_COUNT   = 4424
EXPECTED_COL_COUNT   = 37
EXPECTED_NULL_COUNT  = 0
EXPECTED_DUP_COUNT   = 0

# After cleaning: column 4 name and Nacionality → Nationality
REQUIRED_COLUMNS_POST_CLEAN = [
    "Marital status",
    "Application mode",
    "Application order",
    "Course",
    "Daytime/evening attendance",  # tab stripped
    "Previous qualification",
    "Previous qualification (grade)",
    "Nationality",                 # renamed from Nacionality
    "Mother's qualification",
    "Father's qualification",
    "Mother's occupation",
    "Father's occupation",
    "Admission grade",
    "Displaced",
    "Educational special needs",
    "Debtor",
    "Tuition fees up to date",
    "Gender",
    "Scholarship holder",
    "Age at enrollment",
    "International",
    "Curricular units 1st sem (credited)",
    "Curricular units 1st sem (enrolled)",
    "Curricular units 1st sem (evaluations)",
    "Curricular units 1st sem (approved)",
    "Curricular units 1st sem (grade)",
    "Curricular units 1st sem (without evaluations)",
    "Curricular units 2nd sem (credited)",
    "Curricular units 2nd sem (enrolled)",
    "Curricular units 2nd sem (evaluations)",
    "Curricular units 2nd sem (approved)",
    "Curricular units 2nd sem (grade)",
    "Curricular units 2nd sem (without evaluations)",
    "Unemployment rate",
    "Inflation rate",
    "GDP",
    "Target",
]


def run_validation(
    raw: pd.DataFrame,
    clean: pd.DataFrame,
    cleaning_report: dict[str, Any],
) -> dict[str, Any]:
    """
    Cross-validate raw vs. cleaned DataFrame.

    Returns a comprehensive validation report dict.
    Raises RuntimeError on hard failures.
    """
    report: dict[str, Any] = {}
    failures: list[str] = []
    warnings_list: list[str] = []

    # ------------------------------------------------------------------
    # Dimensional checks
    # ------------------------------------------------------------------
    report["rows_before"]   = int(raw.shape[0])
    report["rows_after"]    = int(clean.shape[0])
    report["cols_before"]   = int(raw.shape[1])
    report["cols_after"]    = int(clean.shape[1])

    if raw.shape[0] != clean.shape[0]:
        failures.append(
            f"Row count changed: {raw.shape[0]} → {clean.shape[0]}. "
            "No rows should be dropped during cleaning."
        )
    if clean.shape[0] != EXPECTED_ROW_COUNT:
        failures.append(
            f"Expected {EXPECTED_ROW_COUNT} rows, found {clean.shape[0]}."
        )
    if raw.shape[1] != clean.shape[1]:
        failures.append(
            f"Column count changed: {raw.shape[1]} → {clean.shape[1]}."
        )

    # ------------------------------------------------------------------
    # Null checks
    # ------------------------------------------------------------------
    raw_nulls   = int(raw.isnull().sum().sum())
    clean_nulls = int(clean.isnull().sum().sum())
    report["nulls_before"] = raw_nulls
    report["nulls_after"]  = clean_nulls

    if clean_nulls > raw_nulls:
        failures.append(
            f"Cleaning introduced new nulls: {raw_nulls} → {clean_nulls}."
        )
    if clean_nulls != EXPECTED_NULL_COUNT:
        warnings_list.append(
            f"Expected {EXPECTED_NULL_COUNT} nulls post-clean, found {clean_nulls}."
        )

    # ------------------------------------------------------------------
    # Duplicate checks
    # ------------------------------------------------------------------
    raw_dups   = int(raw.duplicated().sum())
    clean_dups = int(clean.duplicated().sum())
    report["duplicates_before"] = raw_dups
    report["duplicates_after"]  = clean_dups

    if clean_dups > EXPECTED_DUP_COUNT:
        failures.append(f"Duplicate rows found after cleaning: {clean_dups}.")

    # ------------------------------------------------------------------
    # Required columns present
    # ------------------------------------------------------------------
    missing_cols = [c for c in REQUIRED_COLUMNS_POST_CLEAN if c not in clean.columns]
    extra_cols   = [c for c in clean.columns if c not in REQUIRED_COLUMNS_POST_CLEAN]
    report["missing_required_columns"] = missing_cols
    report["unexpected_extra_columns"] = extra_cols

    if missing_cols:
        failures.append(f"Required columns missing after cleaning: {missing_cols}")

    # ------------------------------------------------------------------
    # Renamed / stripped columns
    # ------------------------------------------------------------------
    report["columns_stripped"] = cleaning_report.get("columns_stripped", [])
    report["columns_renamed"]  = cleaning_report.get("columns_renamed", {})

    # ------------------------------------------------------------------
    # Validation issues from cleaning
    # ------------------------------------------------------------------
    report["binary_validation_issues"]      = cleaning_report.get("binary_validation_issues", {})
    report["range_validation_issues"]       = cleaning_report.get("range_validation_issues", {})
    report["categorical_validation_issues"] = cleaning_report.get("categorical_validation_issues", {})
    report["impossible_value_checks"]       = cleaning_report.get("impossible_value_checks", {})

    # Any domain or logical violation indicates unexpected corruption.
    for k, v in report["binary_validation_issues"].items():
        warnings_list.append(f"Binary issue in '{k}': {v}")
    for k, v in report["range_validation_issues"].items():
        warnings_list.append(f"Range issue in '{k}': {v}")
    for k, v in report["categorical_validation_issues"].items():
        warnings_list.append(f"Categorical issue in '{k}': {v}")
    for k, v in report["impossible_value_checks"].items():
        failures.append(f"Impossible value check '{k}': {v} rows")
    for k, v in report["binary_validation_issues"].items():
        failures.append(f"Binary issue in '{k}': {v}")
    for k, v in report["range_validation_issues"].items():
        failures.append(f"Range issue in '{k}': {v}")
    for k, v in report["categorical_validation_issues"].items():
        failures.append(f"Categorical issue in '{k}': {v}")

    # ------------------------------------------------------------------
    # Target distribution
    # ------------------------------------------------------------------
    if "Target" in clean.columns:
        vc  = clean["Target"].value_counts()
        pct = clean["Target"].value_counts(normalize=True).round(4) * 100
        report["target_distribution"] = {
            cls: {"count": int(vc[cls]), "pct": float(pct[cls])}
            for cls in vc.index
        }
        # Confirm all 3 expected classes are present
        expected_classes = {"Graduate", "Dropout", "Enrolled"}
        found_classes    = set(vc.index)
        if found_classes != expected_classes:
            failures.append(
                f"Target classes mismatch. Expected {expected_classes}, found {found_classes}."
            )

    # ------------------------------------------------------------------
    # Overall status
    # ------------------------------------------------------------------
    report["failures"]     = failures
    report["warnings"]     = warnings_list
    report["status"]       = "PASS" if not failures else "FAIL"

    # Hard-fail on critical issues
    if failures:
        msg = "\n".join(f"  ❌ {f}" for f in failures)
        raise RuntimeError(
            f"\n\n{'='*60}\nVALIDATION FAILED — {len(failures)} critical issue(s):\n{msg}\n{'='*60}"
        )

    log.info(
        "Validation PASSED. Rows: %d, Cols: %d, Nulls: %d, Dups: %d, Warnings: %d",
        clean.shape[0], clean.shape[1], clean_nulls, clean_dups, len(warnings_list),
    )
    return report


def save_report(report: dict[str, Any], path: str | Path) -> None:
    """Persist validation report as JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, default=str)
    log.info("Saved validation report to %s", path)
