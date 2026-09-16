from __future__ import annotations

import streamlit as st
import plotly.express as px

from dashboard.charts.plots import academic_outcome_box
from dashboard.components.ui import empty_state, kpi_row, page_header, section_title
from dashboard.utils.data import OUTCOME_COLORS


def render(df):
    page_header("Academic Performance", "Outcome comparisons across grades, progress, evaluations and approved units.")
    if df.empty:
        empty_state()
        return
    kpi_row([
        ("Average semester 1 grade", f"{df['Curricular units 1st sem (grade)'].mean():.2f}", "0–20 scale"),
        ("Average semester 2 grade", f"{df['Curricular units 2nd sem (grade)'].mean():.2f}", "0–20 scale"),
        ("Average academic progress", f"{df['academic_progress'].mean():.1%}", "Approved / enrolled"),
        ("Average approved units", f"{df['f_b_total_units_approved'].mean():.1f}", "Across both semesters"),
    ])
    cols = st.columns(2)
    for col, metric, title in [(cols[0], "Curricular units 1st sem (grade)", "Semester 1 grade distribution"), (cols[1], "Curricular units 2nd sem (grade)", "Semester 2 grade distribution")]:
        with col:
            section_title(title)
            st.plotly_chart(px.histogram(df, x=metric, color="Target", nbins=20, barmode="overlay", opacity=.75, color_discrete_map=OUTCOME_COLORS, title=title), use_container_width=True, config={"displayModeBar": False})
    section_title("Semester 1 vs semester 2 grade", "Observed relationship; zero grades can represent structural no-approval values")
    st.plotly_chart(px.scatter(df, x="Curricular units 1st sem (grade)", y="Curricular units 2nd sem (grade)", color="Target", color_discrete_map=OUTCOME_COLORS, opacity=.5, hover_data=["Record Index"], title="Semester grade comparison"), use_container_width=True, config={"displayModeBar": False})
    section_title("Performance → outcome", "Outcome comparison, not a causal claim")
    metrics = [("academic_progress", "Academic progress by outcome"), ("f_b_total_units_approved", "Approved units by outcome"), ("semester_1_evaluation_rate", "Evaluation rate by outcome"), ("Curricular units 1st sem (without evaluations)", "Units without evaluation by outcome")]
    for start in range(0, len(metrics), 2):
        cols = st.columns(2)
        for col, (metric, title) in zip(cols, metrics[start:start + 2]):
            with col:
                if metric in df:
                    st.plotly_chart(academic_outcome_box(df, metric, title), use_container_width=True, config={"displayModeBar": False})
