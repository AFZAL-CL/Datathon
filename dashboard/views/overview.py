from __future__ import annotations

import streamlit as st

from dashboard.charts.plots import dropout_by_dimension, outcome_distribution
from dashboard.components.ui import empty_state, kpi_row, page_header, section_title
from dashboard.utils.data import age_order


def render(df, validation):
    page_header("Student Retention & Academic Intelligence", "Explore student outcomes, academic patterns and observed dropout-risk indicators.")
    if df.empty:
        empty_state()
        return
    total = len(df)
    dropout = (df["Target"] == "Dropout").mean() * 100
    graduate = (df["Target"] == "Graduate").mean() * 100
    enrolled = (df["Target"] == "Enrolled").mean() * 100
    high_risk = int((df["current_academic_risk"] == "HIGH").sum())
    kpi_row([
        ("Total students", f"{total:,}", "Current selection"),
        ("Observed dropout rate", f"{dropout:.1f}%", "Associated outcome"),
        ("Graduation rate", f"{graduate:.1f}%", "Observed outcome"),
        ("Enrolled rate", f"{enrolled:.1f}%", "Observed outcome"),
        ("High academic risk", f"{high_risk:,}", "Post-enrolment indicator"),
    ])
    left, right = st.columns([1, 1.35])
    with left:
        section_title("Outcome distribution", "Counts within the current selection")
        st.plotly_chart(outcome_distribution(df), use_container_width=True, config={"displayModeBar": False})
    with right:
        section_title("Dropout rate by course", "Courses with larger observed dropout rates appear higher")
        st.plotly_chart(dropout_by_dimension(df, "Course Label", "Observed dropout rate by course", top_n=17), use_container_width=True, config={"displayModeBar": False})
    section_title("Age pattern", "Age bands keep the comparison readable")
    st.plotly_chart(dropout_by_dimension(df, "age_group", "Observed dropout rate by age group", age_order()), use_container_width=True, config={"displayModeBar": False})
    section_title("What the data says", "Dynamic observations from the current filters")
    course = df.groupby("Course Label")["Target"].apply(lambda x: (x == "Dropout").mean() * 100).sort_values(ascending=False)
    age = df.groupby("age_group")["Target"].apply(lambda x: (x == "Dropout").mean() * 100).sort_values(ascending=False)
    for text in [
        f"{course.index[0]} has the highest observed dropout rate among selected courses ({course.iloc[0]:.1f}%)." if len(course) else "Course comparison is unavailable for this selection.",
        f"The {age.index[0]} age group has the highest observed dropout rate in the current selection ({age.iloc[0]:.1f}%)." if len(age) else "Age-group comparison is unavailable for this selection.",
        f"The current selection contains {high_risk:,} students labelled HIGH on the post-enrolment academic-risk indicator." if "current_academic_risk" in df else "Academic risk indicators are unavailable.",
    ]:
        st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)
        with st.expander("Data quality"):
            st.write({"Raw rows": validation.get("rows_before"), "Processed rows": validation.get("rows_after"), "Nulls": validation.get("nulls_after"), "Duplicates": validation.get("duplicates_after"), "Renamed": validation.get("columns_renamed"), "Header normalized": "Daytime/evening attendance"})
