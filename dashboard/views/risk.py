from __future__ import annotations

import streamlit as st
import plotly.express as px

from dashboard.charts.plots import academic_outcome_box, dropout_by_dimension, risk_distribution
from dashboard.components.ui import empty_state, page_header, section_title
from dashboard.utils.data import OUTCOME_COLORS, age_order


def render(df):
    page_header("Risk Analysis", "Two analytical scenarios, kept separate to make timing and leakage explicit.")
    if df.empty:
        empty_state()
        return
    st.info("Early Risk uses admission-time information. Current Academic Risk includes post-enrolment indicators and should not be interpreted as an admission-time prediction.")
    section_title("A / Early or admission risk", "Admission-time context only; semester performance is excluded")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(risk_distribution(df, "early_admission_risk", "Early admission-risk distribution"), use_container_width=True, config={"displayModeBar": False})
    with right:
        st.plotly_chart(dropout_by_dimension(df, "Course Label", "Early-risk context by course", top_n=17), use_container_width=True, config={"displayModeBar": False})
    for dimension, title in [("Scholarship Status", "Early risk by scholarship status"), ("Tuition Status", "Early risk by tuition status"), ("age_group", "Early risk by age group"), ("Admission Grade Band", "Early risk by admission grade band")]:
        section_title(title)
        table = df.groupby([dimension, "early_admission_risk"]).size().reset_index(name="Students")
        fig = px.bar(table, x=dimension, y="Students", color="early_admission_risk", barmode="stack", category_orders={"age_group": age_order()}, title=title, color_discrete_map={"LOW":"#2f7d68", "MEDIUM":"#c58a31", "HIGH":"#b94a48"})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    section_title("B / Current academic risk", "Post-enrolment academic indicators")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(risk_distribution(df, "current_academic_risk", "Current academic-risk distribution"), use_container_width=True, config={"displayModeBar": False})
    with right:
        st.plotly_chart(dropout_by_dimension(df, "Course Label", "Current academic risk context by course", top_n=17), use_container_width=True, config={"displayModeBar": False})
    fig = px.box(df, x="Target", y="academic_progress", color="Target", category_orders={"Target": ["Graduate", "Enrolled", "Dropout"]}, color_discrete_map=OUTCOME_COLORS, title="Academic progress vs observed outcome", points=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    section_title("Semester performance", "Observed comparison of in-programme indicators")
    perf = ["Curricular units 1st sem (grade)", "Curricular units 2nd sem (grade)", "f_b_total_units_approved"]
    cols = st.columns(3)
    for col, metric in zip(cols, perf):
        with col:
            if metric in df:
                st.plotly_chart(academic_outcome_box(df, metric, metric.replace("Curricular units ", "").replace("f_b_", "").title()), use_container_width=True, config={"displayModeBar": False})
