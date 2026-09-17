import pandas as pd
import streamlit as st
import json
from pathlib import Path
from typing import Any, Tuple, Dict

ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT / "data" / "processed"

def _label_binary(value: Any, kind: str) -> str:
    labels = {
        "gender": {0: "Female", 1: "Male"},
        "scholarship": {0: "No scholarship", 1: "Scholarship holder"},
        "tuition": {0: "Not up to date", 1: "Up to date"},
        "debtor": {0: "No debt", 1: "Debtor"},
    }
    return labels[kind].get(int(value), str(value))

@st.cache_data(show_spinner=False)
def load_data() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Loads and prepares the dataset for the dashboard."""
    try:
        df = pd.read_csv(PROCESSED_DIR / "student_analytics.csv")
        early = pd.read_csv(PROCESSED_DIR / "student_analytics_early.csv")
        validation = json.loads((PROCESSED_DIR / "validation_report.json").read_text())
        
        # Add Record Index
        df["Record Index"] = range(1, len(df) + 1)
        early["Record Index"] = range(1, len(early) + 1)
        
        # Binary Labels
        df["Gender Label"] = df["Gender"].map(lambda x: _label_binary(x, "gender"))
        df["Scholarship Status"] = df["Scholarship holder"].map(lambda x: _label_binary(x, "scholarship"))
        df["Tuition Status"] = df["Tuition fees up to date"].map(lambda x: _label_binary(x, "tuition"))
        df["Debtor Status"] = df["Debtor"].map(lambda x: _label_binary(x, "debtor"))
        
        if "age_group" not in df.columns:
            df["age_group"] = pd.cut(df["Age at enrollment"], 
                                     bins=[14, 19, 24, 29, 39, 100], 
                                     labels=["15-19", "20-24", "25-29", "30-39", "40+"]).astype(str)
            
        df["Course Label"] = df["Course"].astype(str)
        df["Admission Grade Band"] = df.get("admission_grade_band", df.get("f_a_admission_band", "Unknown"))
        
        return df, {"early": early, "validation": validation}
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame(), {}
