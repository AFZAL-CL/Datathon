"""Run cleaning, validation, feature engineering, analytics, and reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analytics.insights import run_all_insights
from src.analytics.metrics import run_all_metrics
from src.analytics.risk_analysis import add_risk_indicators
from src.analytics.segmentation import run_all_segments
from src.data.cleaning import clean, load_raw, save_clean
from src.data.preprocessing import build_scenario_a_features, build_scenario_b_features
from src.data.validation import run_validation, save_report


def _write_table(table: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(path, index=False)


def _write_reports(validation: dict, metrics: dict, thresholds: dict, root: Path) -> None:
    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    target = metrics["overall"]
    (reports / "CLEANING_REPORT.md").write_text(
        "# Cleaning Report\n\n"
        f"Status: **{validation['status']}**\n\n"
        f"Rows: {validation['rows_before']} before, {validation['rows_after']} after. "
        f"Columns: {validation['cols_before']} before, {validation['cols_after']} after.\n\n"
        f"Nulls: {validation['nulls_before']} before, {validation['nulls_after']} after. "
        f"Duplicates: {validation['duplicates_before']} before, {validation['duplicates_after']} after.\n\n"
        f"Renamed columns: `{validation['columns_renamed']}`. Stripped columns: `{validation['columns_stripped']}`.\n\n"
        f"Invalid values: `{validation['binary_validation_issues']}`, `{validation['range_validation_issues']}`, "
        f"`{validation['categorical_validation_issues']}`, `{validation['impossible_value_checks']}`.\n\n"
        f"Target distribution: `{target['counts']}` ({target['percentages']}%).\n",
        encoding="utf-8",
    )
    (reports / "FEATURE_ENGINEERING.md").write_text(
        "# Feature Engineering\n\n"
        "Scenario A uses age groups, admission/prior-grade quartiles, payment status, application order, prior qualification, and demographic fields available at admission.\n\n"
        "Scenario B adds semester pass/evaluation rates, academic progress = total approved / total enrolled, weighted academic performance = sum(semester grade * approved units) / total approved, grade improvement, engagement, credited ratio, and no-evaluation indicators. Zero denominators return 0; grade zero remains structural.\n\n"
        "Qualification codes remain categorical codes; no unsupported ordinal parental-education average is created.\n",
        encoding="utf-8",
    )
    (reports / "LEAKAGE_ANALYSIS.md").write_text(
        "# Leakage Analysis\n\n"
        "**Scenario A: Early/Admission Risk.** Uses only enrolment/admission-time fields and `early_admission_risk`, whose thresholds are observed admission-grade tertiles. It excludes semester performance features.\n\n"
        "**Scenario B: Current Academic Risk.** Adds semester grades, enrolled/approved/evaluated units, and derived academic rates. These are post-enrolment and can be highly predictive of Target; they must not be described as admission-time prediction. `current_academic_risk` uses observed academic-progress tertiles.\n\n"
        "Unemployment rate, Inflation rate, and GDP are national contextual variables shared by cohorts. They are retained for descriptive context, not treated as individual causal risk factors. Target is never used to create a feature.\n",
        encoding="utf-8",
    )
    (reports / "ANALYTICS.md").write_text(
        "# Analytics\n\n"
        f"Overall outcomes: `{target}`.\n\n"
        "Outcome tables cover Course, Gender, age group, scholarship holder, tuition status, debtor, previous qualification, application mode, admission grade bands, displaced, and international status. Academic summaries include grades, approved/enrolled/evaluation counts, and units without evaluations. Financial, demographic, macroeconomic, segmentation, and rule-based risk outputs are exported under `data/processed`.\n\n"
        f"Risk thresholds derived from actual distributions: `{thresholds}`.\n",
        encoding="utf-8",
    )


def main() -> None:
    raw = load_raw(ROOT / "data/raw/student_dropout.csv")
    cleaned, cleaning_report = clean(raw)
    validation = run_validation(raw, cleaned, cleaning_report)
    save_clean(cleaned, ROOT / "data/processed/student_dropout_clean.csv")
    save_report(validation, ROOT / "data/processed/validation_report.json")

    scenario_a = build_scenario_a_features(cleaned)
    scenario_b = build_scenario_b_features(scenario_a)
    analytics, thresholds = add_risk_indicators(scenario_b)
    semester_cols = [
        c for c in cleaned.columns
        if c.startswith("Curricular units 1st sem") or c.startswith("Curricular units 2nd sem")
    ]
    early_cols = [c for c in scenario_a.columns if c not in semester_cols]
    early_export = scenario_a[early_cols].copy()
    early_export["early_admission_risk"] = analytics["early_admission_risk"]
    _write_table(early_export, ROOT / "data/processed/student_analytics_early.csv")
    _write_table(analytics, ROOT / "data/processed/student_analytics.csv")

    metrics = run_all_metrics(analytics)
    for dimension, table in metrics["by_dimension"].items():
        filename = dimension.lower().replace(" ", "_").replace("/", "_")
        _write_table(table, ROOT / "data/processed" / f"outcomes_by_{filename}.csv")
    insights = run_all_insights(analytics)
    segments = run_all_segments(analytics)
    for name, table in segments.items():
        if name != "enriched_df" and isinstance(table, pd.DataFrame):
            _write_table(table, ROOT / "data/processed" / f"segment_{name}.csv")
    (ROOT / "data/processed/analytics_summary.json").write_text(
        json.dumps(insights, indent=2, default=str), encoding="utf-8"
    )
    _write_reports(validation, metrics, thresholds, ROOT)
    print(f"Pipeline complete: {len(analytics)} rows, {len(analytics.columns)} analytical columns")


if __name__ == "__main__":
    main()
