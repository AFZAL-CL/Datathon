from __future__ import annotations

import streamlit as st

from dashboard.charts.plots import dropout_by_dimension, outcome_matrix
from dashboard.components.ui import empty_state, page_header, section_title
from dashboard.utils.data import age_order


def render(df):
    page_header("Retention & Outcomes", "Compare observed outcomes across admission, financial and demographic groups.")
    if df.empty:
        empty_state()
        return
    dimensions = [("Gender Label", "Observed dropout rate by gender", None), ("Scholarship Status", "Observed dropout rate by scholarship status", None), ("Tuition Status", "Observed dropout rate by tuition status", None), ("Debtor Status", "Observed dropout rate by debtor status", None), ("Previous qualification", "Observed dropout rate by previous qualification", None), ("Application mode", "Observed dropout rate by application mode", None)]
    for start in range(0, len(dimensions), 2):
        cols = st.columns(2)
        for col, (dimension, title, order) in zip(cols, dimensions[start:start + 2]):
            with col:
                section_title(title)
                st.plotly_chart(dropout_by_dimension(df, dimension, title, order, 12 if dimension in {"Previous qualification", "Application mode"} else None), use_container_width=True, config={"displayModeBar": False})
    section_title("Outcome matrix", "Percentage of each course's selected records by outcome")
    st.plotly_chart(outcome_matrix(df, "Course Label", "Course outcome matrix"), use_container_width=True, config={"displayModeBar": False})
