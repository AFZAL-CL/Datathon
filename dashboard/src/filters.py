import streamlit as st
import pandas as pd
from typing import Dict, Any

def render_global_filters(df: pd.DataFrame) -> Dict[str, Any]:
    """Renders the global sidebar filters and returns the selections."""
    st.sidebar.markdown('<div class="brand-container"><div class="brand-title">EDUPULSE</div><div class="brand-subtitle">Student Retention & Academic Intelligence</div></div>', unsafe_allow_html=True)
    st.sidebar.markdown("### Global Filters")
    
    def select(label, values):
        return st.sidebar.multiselect(label, ["All"] + sorted([str(v) for v in values if pd.notna(v)]), default=["All"], key=f"filter_{label}")
    
    if st.sidebar.button("Reset Filters", type="primary"):
        # Streamlit doesn't have a native reset button that clears state easily without rerun,
        # but clicking a button will trigger a rerun. We would typically clear session state here.
        for key in st.session_state.keys():
            if key.startswith("filter_"):
                st.session_state[key] = ["All"]
    
    selections = {
        "Course": select("Course", df["Course Label"].unique()),
        "Gender": select("Gender", df["Gender Label"].unique()),
        "Age Group": select("Age Group", df["age_group"].dropna().unique()),
        "Scholarship Holder": select("Scholarship Holder", df["Scholarship Status"].unique()),
        "Tuition Status": select("Tuition Status", df["Tuition Status"].unique()),
        "Debtor Status": select("Debtor Status", df["Debtor Status"].unique()),
        "Target": select("Target", df["Target"].dropna().unique()),
    }
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Data Source: UCI Student Dropout & Academic Success")
    st.sidebar.caption("No Mid-Day Meal, school infrastructure, or TransOrg fields are represented.")
    
    return selections

def apply_filters(df: pd.DataFrame, selections: Dict[str, Any]) -> pd.DataFrame:
    """Applies the selections to the DataFrame."""
    result = df.copy()
    mapping = {
        "Course": "Course Label", 
        "Gender": "Gender Label", 
        "Age Group": "age_group",
        "Scholarship Holder": "Scholarship Status", 
        "Tuition Status": "Tuition Status",
        "Debtor Status": "Debtor Status", 
        "Target": "Target"
    }
    
    for filter_name, selected in selections.items():
        column = mapping.get(filter_name)
        if column and selected and "All" not in selected:
            result = result[result[column].isin(selected)]
            
    return result
