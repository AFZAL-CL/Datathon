import pandas as pd
from typing import Dict, Any, List

def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates high-level KPIs from the given DataFrame."""
    if df.empty:
        return {
            "Total Students": 0,
            "Dropout Rate": "0%",
            "Graduation Rate": "0%",
            "Enrolled Rate": "0%",
            "High-Risk Students": 0
        }
        
    total = len(df)
    counts = df["Target"].value_counts()
    
    dropout = counts.get("Dropout", 0)
    graduate = counts.get("Graduate", 0)
    enrolled = counts.get("Enrolled", 0)
    
    # Calculate percentages
    dropout_rate = (dropout / total) * 100
    graduate_rate = (graduate / total) * 100
    enrolled_rate = (enrolled / total) * 100
    
    # High-Risk Students based on early_admission_risk or current_academic_risk
    # Depending on what exists. If we assume 'early_admission_risk' has categories like 'High'
    high_risk_count = 0
    if "early_admission_risk" in df.columns:
        high_risk_count = len(df[df["early_admission_risk"] == "High"])
    
    return {
        "Total Students": f"{total:,}",
        "Dropout Rate": f"{dropout_rate:.1f}%",
        "Graduation Rate": f"{graduate_rate:.1f}%",
        "Enrolled Rate": f"{enrolled_rate:.1f}%",
        "High-Risk Students": f"{high_risk_count:,}"
    }

def get_outcome_distribution(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Gets the distribution of Target across a dimension."""
    if df.empty or dimension not in df.columns:
        return pd.DataFrame()
    table = pd.crosstab(df[dimension], df["Target"], normalize='index') * 100
    return table.reset_index()
