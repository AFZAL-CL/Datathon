from __future__ import annotations

import streamlit as st
import plotly.express as px

from dashboard.components.ui import empty_state, page_header, section_title
from dashboard.utils.data import OUTCOME_COLORS


def render(df):
    page_header("Financial & Support Analysis", "Observed outcome patterns across tuition status, debt and scholarship support.")
    if df.empty:
        empty_state()
        return
    dimensions = [("Tuition Status", "Tuition status → outcome"), ("Debtor Status", "Debtor status → outcome"), ("Scholarship Status", "Scholarship status → outcome")]
    cols = st.columns(3)
    for col, (dimension, title) in zip(cols, dimensions):
        with col:
            section_title(title)
            rates = df.groupby(dimension)["Target"].apply(lambda x: (x == "Dropout").mean() * 100).reset_index(name="Observed dropout rate")
            fig = px.bar(rates, x=dimension, y="Observed dropout rate", text="Observed dropout rate", color_discrete_sequence=["#b94a48"], title=title)
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    section_title("Financial support profile", "Only combinations present in the selected records are shown")
    profile = df.assign(FinancialSupportProfile=df["Scholarship Status"] + " + " + df["Tuition Status"])
    summary = profile.groupby("FinancialSupportProfile").agg(Students=("Target", "size"), DropoutRate=("Target", lambda x: (x == "Dropout").mean() * 100)).reset_index().sort_values("DropoutRate", ascending=False)
    fig = px.bar(summary, x="DropoutRate", y="FinancialSupportProfile", orientation="h", text="DropoutRate", color_discrete_sequence=["#2f7d68"], title="Observed dropout rate by financial support profile", hover_data=["Students"])
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.dataframe(summary.rename(columns={"FinancialSupportProfile": "Profile", "DropoutRate": "Observed dropout rate (%)"}), use_container_width=True, hide_index=True)
    st.caption("These are observed associations in the UCI dataset. They do not establish causal effects.")
