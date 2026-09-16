from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
OUTCOMES = ["Graduate", "Enrolled", "Dropout"]
OUTCOME_COLORS = {"Graduate": "#2f7d68", "Enrolled": "#c58a31", "Dropout": "#b94a48"}


def _label_binary(value: Any, kind: str) -> str:
    labels = {
        "gender": {0: "Female", 1: "Male"},
        "scholarship": {0: "No scholarship", 1: "Scholarship holder"},
        "tuition": {0: "Not up to date", 1: "Up to date"},
        "debtor": {0: "No debt", 1: "Debtor"},
    }
    return labels[kind].get(int(value), str(value))


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, dict[str, Any]]:
    df = pd.read_csv(PROCESSED / "student_analytics.csv")
    early = pd.read_csv(PROCESSED / "student_analytics_early.csv")
    validation = json.loads((PROCESSED / "validation_report.json").read_text())
    df["Record Index"] = range(1, len(df) + 1)
    df["Gender Label"] = df["Gender"].map(lambda x: _label_binary(x, "gender"))
    df["Scholarship Status"] = df["Scholarship holder"].map(lambda x: _label_binary(x, "scholarship"))
    df["Tuition Status"] = df["Tuition fees up to date"].map(lambda x: _label_binary(x, "tuition"))
    df["Debtor Status"] = df["Debtor"].map(lambda x: _label_binary(x, "debtor"))
    if "age_group" not in df:
        df["age_group"] = pd.cut(df["Age at enrollment"], [14, 19, 24, 29, 39, 100], labels=["15-19", "20-24", "25-29", "30-39", "40+"]).astype(str)
    df["Course Label"] = df["Course"].astype(str)
    df["Admission Grade Band"] = df.get("admission_grade_band", df.get("f_a_admission_band", "Unknown"))
    early["Record Index"] = range(1, len(early) + 1)
    return df, {"early": early, "validation": validation}


def apply_filters(df: pd.DataFrame, selections: dict[str, Any]) -> pd.DataFrame:
    result = df.copy()
    mapping = {
        "Course": "Course Label", "Gender": "Gender Label", "Age Group": "age_group",
        "Scholarship Holder": "Scholarship Status", "Tuition Status": "Tuition Status",
        "Debtor Status": "Debtor Status", "Target": "Target",
    }
    for filter_name, selected in selections.items():
        column = mapping.get(filter_name)
        if column and selected and "All" not in selected:
            result = result[result[column].isin(selected)]
    return result


def age_order() -> list[str]:
    return ["15-19", "20-24", "25-29", "30-39", "40+"]


def outcome_table(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    if df.empty or dimension not in df.columns:
        return pd.DataFrame()
    table = pd.crosstab(df[dimension], df["Target"]).reindex(columns=OUTCOMES, fill_value=0)
    table["Total"] = table.sum(axis=1)
    for outcome in OUTCOMES:
        table[f"{outcome} %"] = (table[outcome] / table["Total"].replace(0, pd.NA) * 100).round(2)
    return table.reset_index()


def risk_table(df: pd.DataFrame, risk_column: str, dimension: str) -> pd.DataFrame:
    if df.empty or risk_column not in df or dimension not in df:
        return pd.DataFrame()
    return df.groupby([dimension, risk_column], dropna=False).size().reset_index(name="Students")
