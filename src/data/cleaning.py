"""
src/data/cleaning.py
====================
Phase 1 — Data Cleaning for the UCI Student Dropout & Academic Success dataset.

Rules:
- Strip whitespace / tab characters from every column name.
- Rename 'Nacionality' → 'Nationality'.
- Preserve the Target column as-is (3 classes: Graduate, Dropout, Enrolled).
- Do NOT treat grade = 0 as missing (structural zeros for students with no approvals).
- Do NOT remove any rows.
- Validate binary fields, numerical ranges, and categorical domain codes.
- Flag (but do not drop) any impossible values for the validation report.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain knowledge — valid code sets from the UCI codebook
# ---------------------------------------------------------------------------

VALID_MARITAL_STATUS     = {1, 2, 3, 4, 5, 6}
VALID_APPLICATION_MODES  = {1, 2, 5, 7, 10, 15, 16, 17, 18, 26, 27, 39, 42, 43, 44, 51, 53, 57}
VALID_APPLICATION_ORDERS = set(range(10))           # 0–9
VALID_COURSES = {33, 171, 8014, 9003, 9070, 9085, 9119, 9130, 9147,
                 9238, 9254, 9500, 9556, 9670, 9773, 9853, 9991}
VALID_PREV_QUAL          = {1, 2, 3, 4, 5, 6, 9, 10, 12, 14, 15, 19, 38, 39, 40, 42, 43}
VALID_NATIONALITIES      = set(range(1, 110))        # 1–109 (country codes)
VALID_PARENT_QUAL        = set(range(1, 45))         # 1–44
VALID_PARENT_OCC         = set(range(0, 196))        # 0–195
VALID_TARGET_CLASSES     = {"Graduate", "Dropout", "Enrolled"}

BINARY_COLUMNS = [
    "Daytime/evening attendance",
    "Displaced",
    "Educational special needs",
    "Debtor",
    "Tuition fees up to date",
    "Gender",
    "Scholarship holder",
    "International",
]

GRADE_COLUMNS = [
    "Previous qualification (grade)",
    "Admission grade",
    "Curricular units 1st sem (grade)",
    "Curricular units 2nd sem (grade)",
]

# Grades 0-200 for pre-enrolment; 0-20 for in-programme
GRADE_RANGES = {
    "Previous qualification (grade)":  (0.0, 200.0),
    "Admission grade":                  (0.0, 200.0),
    "Curricular units 1st sem (grade)": (0.0, 20.0),
    "Curricular units 2nd sem (grade)": (0.0, 20.0),
}

COUNT_COLUMNS = [
    "Curricular units 1st sem (credited)",
    "Curricular units 1st sem (enrolled)",
    "Curricular units 1st sem (evaluations)",
    "Curricular units 1st sem (approved)",
    "Curricular units 1st sem (without evaluations)",
    "Curricular units 2nd sem (credited)",
    "Curricular units 2nd sem (enrolled)",
    "Curricular units 2nd sem (evaluations)",
    "Curricular units 2nd sem (approved)",
    "Curricular units 2nd sem (without evaluations)",
]

AGE_RANGE = (17, 70)
MACRO_RANGES = {
    "Unemployment rate": (-100.0, 100.0),
    "Inflation rate": (-100.0, 100.0),
    "GDP": (-100.0, 100.0),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_raw(path: str | Path) -> pd.DataFrame:
    """Load the raw semicolon-delimited CSV without any transformations."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Raw data not found at: {path}")
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    log.info("Loaded raw data: %d rows × %d cols from %s", *df.shape, path)
    return df


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Apply all cleaning steps to the raw DataFrame.

    Returns
    -------
    cleaned : pd.DataFrame
        The cleaned dataset.
    report  : dict
        A dictionary of cleaning statistics for the validation report.
    """
    report: dict[str, Any] = {}
    df = df.copy()

    # ------------------------------------------------------------------
    # Step 1 — Strip whitespace / tab characters from column names
    # ------------------------------------------------------------------
    original_cols = list(df.columns)
    df.columns = [c.strip() for c in df.columns]
    stripped = [
        (orig, new) for orig, new in zip(original_cols, df.columns) if orig != new
    ]
    report["columns_stripped"] = stripped
    log.info("Step 1: stripped whitespace from %d column name(s): %s", len(stripped), stripped)

    # ------------------------------------------------------------------
    # Step 2 — Rename typos
    # ------------------------------------------------------------------
    renames: dict[str, str] = {}
    if "Nacionality" in df.columns:
        renames["Nacionality"] = "Nationality"
    if renames:
        df.rename(columns=renames, inplace=True)
    report["columns_renamed"] = renames
    log.info("Step 2: renamed columns: %s", renames)

    # ------------------------------------------------------------------
    # Step 3 — Validate binary columns (must be 0 or 1)
    # ------------------------------------------------------------------
    binary_issues: dict[str, list] = {}
    for col in BINARY_COLUMNS:
        if col not in df.columns:
            continue
        bad_mask = ~df[col].isin({0, 1})
        if bad_mask.any():
            bad_vals = df.loc[bad_mask, col].unique().tolist()
            binary_issues[col] = bad_vals
            log.warning("Binary column '%s' has unexpected values: %s", col, bad_vals)
    report["binary_validation_issues"] = binary_issues

    # ------------------------------------------------------------------
    # Step 4 — Validate numerical ranges
    # ------------------------------------------------------------------
    range_issues: dict[str, dict] = {}

    # Grades
    for col, (lo, hi) in GRADE_RANGES.items():
        if col not in df.columns:
            continue
        out_of_range = df[(df[col] < lo) | (df[col] > hi)]
        if not out_of_range.empty:
            range_issues[col] = {
                "min_found": float(df[col].min()),
                "max_found": float(df[col].max()),
                "expected": [lo, hi],
                "n_violations": int(out_of_range.shape[0]),
            }
            log.warning("Range issue in '%s': %d rows outside [%.1f, %.1f]", col, len(out_of_range), lo, hi)

    # Count columns must be ≥ 0
    for col in COUNT_COLUMNS:
        if col not in df.columns:
            continue
        neg = df[df[col] < 0]
        if not neg.empty:
            range_issues[col] = {
                "issue": "negative count",
                "n_violations": int(neg.shape[0]),
            }
            log.warning("Negative count in '%s': %d rows", col, len(neg))

    # Age
    if "Age at enrollment" in df.columns:
        lo, hi = AGE_RANGE
        out = df[(df["Age at enrollment"] < lo) | (df["Age at enrollment"] > hi)]
        if not out.empty:
            range_issues["Age at enrollment"] = {
                "min_found": int(df["Age at enrollment"].min()),
                "max_found": int(df["Age at enrollment"].max()),
                "expected": list(AGE_RANGE),
                "n_violations": int(out.shape[0]),
            }

    report["range_validation_issues"] = range_issues

    # ------------------------------------------------------------------
    # Step 5 — Validate categorical domain codes
    # ------------------------------------------------------------------
    cat_issues: dict[str, dict] = {}

    def _check_cat(col: str, valid_set: set) -> None:
        if col not in df.columns:
            return
        found = set(df[col].unique())
        unknown = found - valid_set
        if unknown:
            cat_issues[col] = {"unknown_codes": sorted(unknown)}
            log.warning("Unknown codes in '%s': %s", col, sorted(unknown))

    _check_cat("Marital status",        VALID_MARITAL_STATUS)
    _check_cat("Application mode",      VALID_APPLICATION_MODES)
    _check_cat("Application order",     VALID_APPLICATION_ORDERS)
    _check_cat("Course",                VALID_COURSES)
    _check_cat("Previous qualification",VALID_PREV_QUAL)
    _check_cat("Nationality",           VALID_NATIONALITIES)
    _check_cat("Mother's qualification",VALID_PARENT_QUAL)
    _check_cat("Father's qualification",VALID_PARENT_QUAL)
    _check_cat("Mother's occupation",   VALID_PARENT_OCC)
    _check_cat("Father's occupation",   VALID_PARENT_OCC)

    # Target
    if "Target" in df.columns:
        found_targets = set(df["Target"].unique())
        bad_targets = found_targets - VALID_TARGET_CLASSES
        if bad_targets:
            cat_issues["Target"] = {"unknown_classes": sorted(bad_targets)}
            log.error("Unknown target classes: %s", sorted(bad_targets))
        report["target_classes_found"] = sorted(found_targets)
    report["categorical_validation_issues"] = cat_issues

    if "Target" in df.columns:
        df["Target"] = pd.Categorical(
            df["Target"], categories=["Graduate", "Dropout", "Enrolled"]
        )

    # ------------------------------------------------------------------
    # Step 6 — Impossible value checks (logical cross-field)
    # ------------------------------------------------------------------
    impossible: dict[str, Any] = {}

    # approved cannot exceed enrolled
    for sem in ("1st", "2nd"):
        enrolled_col  = f"Curricular units {sem} sem (enrolled)"
        approved_col  = f"Curricular units {sem} sem (approved)"
        if enrolled_col in df.columns and approved_col in df.columns:
            bad = df[df[approved_col] > df[enrolled_col]]
            if not bad.empty:
                impossible[f"{sem}_sem_approved_exceeds_enrolled"] = int(bad.shape[0])
                log.warning(
                    "Sem %s: approved > enrolled in %d rows", sem, bad.shape[0]
                )
    for col, (lo, hi) in MACRO_RANGES.items():
        if col in df.columns:
            mask = (df[col] < lo) | (df[col] > hi)
            if mask.any():
                range_issues[col] = {
                    "min_found": float(df[col].min()), "max_found": float(df[col].max()),
                    "expected": [lo, hi], "n_violations": int(mask.sum()),
                }

    report["impossible_value_checks"] = impossible

    # ------------------------------------------------------------------
    # Step 7 — Duplicate check after cleaning
    # ------------------------------------------------------------------
    n_dups = int(df.duplicated().sum())
    report["duplicates_after_cleaning"] = n_dups
    log.info("Step 7: %d duplicate rows after cleaning", n_dups)

    # ------------------------------------------------------------------
    # Step 8 — Missing value check after cleaning
    # ------------------------------------------------------------------
    nulls = df.isnull().sum()
    report["nulls_after_cleaning"] = int(nulls.sum())
    report["null_detail"] = {
        col: int(n) for col, n in nulls.items() if n > 0
    }

    # ------------------------------------------------------------------
    # Step 9 — Final column order & dtypes (no changes to values)
    # ------------------------------------------------------------------
    report["final_shape"] = list(df.shape)
    report["final_columns"] = list(df.columns)

    log.info(
        "Cleaning complete. Final shape: %d × %d. Issues: binary=%d, range=%d, cat=%d, impossible=%d",
        df.shape[0], df.shape[1],
        len(binary_issues), len(range_issues), len(cat_issues), len(impossible),
    )
    return df, report


def save_clean(df: pd.DataFrame, path: str | Path) -> None:
    """Write the cleaned DataFrame to CSV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    log.info("Saved cleaned data to %s (%d rows × %d cols)", path, *df.shape)
