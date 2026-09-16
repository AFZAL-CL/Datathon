from __future__ import annotations

import streamlit as st

from dashboard.components.ui import empty_state, page_header, section_title


def render(df):
    page_header("Student Explorer", "Inspect a filtered record without implying that the dataset contains a real-world student identifier.")
    if df.empty:
        empty_state()
        return
    record = st.selectbox("Record Index", df["Record Index"].tolist(), format_func=lambda x: f"Record {x}")
    row = df.loc[df["Record Index"] == record].iloc[0]
    section_title("Outcome and risk", "Observed record-level fields")
    cols = st.columns(4)
    for col, label, value in zip(cols, ["Target", "Early admission risk", "Current academic risk", "Academic progress"], [row.get("Target", ""), row.get("early_admission_risk", ""), row.get("current_academic_risk", ""), f"{row.get('academic_progress', 0):.1%}"]):
        with col:
            st.metric(label, value)
    sections = {
        "Admission profile": ["Course Label", "Application mode", "Application order", "Admission grade", "Admission Grade Band", "Previous qualification", "Previous qualification (grade)"],
        "Demographics": ["Gender Label", "Age at enrollment", "age_group", "Displaced", "International", "Educational special needs"],
        "Financial indicators": ["Scholarship Status", "Tuition Status", "Debtor Status"],
        "Academic profile": ["Curricular units 1st sem (grade)", "Curricular units 2nd sem (grade)", "f_b_total_units_approved", "f_b_total_units_enrolled", "semester_1_evaluation_rate", "semester_2_evaluation_rate", "Curricular units 1st sem (without evaluations)", "Curricular units 2nd sem (without evaluations)"],
    }
    for title, fields in sections.items():
        with st.expander(title, expanded=True):
            available = [field for field in fields if field in row.index]
            if available:
                profile = row[available].map(str).rename("Value").to_frame()
                st.dataframe(profile, use_container_width=True)
            else:
                st.caption("No fields available for this profile section.")
