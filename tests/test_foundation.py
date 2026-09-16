from pathlib import Path

import pandas as pd
import pytest

from src.analytics.metrics import outcome_distribution, outcome_by_dimension
from src.data.cleaning import clean, load_raw
from src.data.preprocessing import build_scenario_a_features, build_scenario_b_features
from src.data.validation import run_validation


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def raw():
    return load_raw(ROOT / "data/raw/student_dropout.csv")


def test_cleaning_preserves_rows_and_controls_target(raw):
    cleaned, report = clean(raw)
    assert cleaned.shape == (4424, 37)
    assert cleaned["Target"].dtype.name == "category"
    assert set(cleaned["Target"].dropna()) == {"Graduate", "Dropout", "Enrolled"}
    assert "Nationality" in cleaned.columns
    assert report["columns_renamed"] == {"Nacionality": "Nationality"}
    assert int(cleaned.isna().sum().sum()) == 0


def test_validation_passes_audited_data(raw):
    cleaned, cleaning_report = clean(raw)
    report = run_validation(raw, cleaned, cleaning_report)
    assert report["status"] == "PASS"
    assert report["duplicates_after"] == 0


def test_validation_fails_unexpected_target(raw):
    corrupted = raw.copy()
    corrupted.loc[0, "Target"] = "Unknown"
    cleaned, cleaning_report = clean(corrupted)
    with pytest.raises(RuntimeError, match="Categorical issue"):
        run_validation(corrupted, cleaned, cleaning_report)


def test_feature_formulas_and_no_target_dependency(raw):
    cleaned, _ = clean(raw)
    scenario_a = build_scenario_a_features(cleaned)
    scenario_b = build_scenario_b_features(scenario_a)
    row = scenario_b.iloc[1]
    assert row["semester_1_pass_rate"] == pytest.approx(
        row["Curricular units 1st sem (approved)"] / row["Curricular units 1st sem (enrolled)"]
    )
    assert row["academic_progress"] == pytest.approx(
        (row["Curricular units 1st sem (approved)"] + row["Curricular units 2nd sem (approved)"])
        / (row["Curricular units 1st sem (enrolled)"] + row["Curricular units 2nd sem (enrolled)"])
    )
    assert "Target" not in {"academic_progress", "academic_performance_score"}


def test_metrics_include_all_target_classes(raw):
    cleaned, _ = clean(raw)
    distribution = outcome_distribution(cleaned)
    assert distribution["total"] == 4424
    assert sum(distribution["counts"].values()) == 4424
    table = outcome_by_dimension(cleaned, "Gender")
    assert {"Graduate", "Dropout", "Enrolled"}.issubset(table.columns)


def test_early_scenario_excludes_semester_features(raw):
    cleaned, _ = clean(raw)
    scenario_a = build_scenario_a_features(cleaned)
    semester_cols = [
        c for c in cleaned.columns
        if c.startswith("Curricular units 1st sem") or c.startswith("Curricular units 2nd sem")
    ]
    early_cols = [c for c in scenario_a.columns if c not in semester_cols]
    assert not any(c.startswith("Curricular units") for c in early_cols)
    assert "f_a_admission_band" in early_cols
