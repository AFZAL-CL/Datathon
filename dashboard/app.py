from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.ui import inject_css
from dashboard.components.ui import page_header
from dashboard.views import academic, explorer, financial, overview, retention, risk
from dashboard.utils.data import apply_filters, load_data


st.set_page_config(page_title="EDUPULSE | Student Retention Intelligence", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
inject_css()
df, meta = load_data()

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-name">EDUPULSE</div><div class="brand-sub">Student Retention &amp; Academic Intelligence</div></div>', unsafe_allow_html=True)
    page = st.radio("Navigate", ["Overview", "Retention & Outcomes", "Risk Analysis", "Academic Performance", "Financial & Support", "Student Explorer", "AI Analyst"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**Global filters**")
    def select(label, values):
        return st.multiselect(label, ["All"] + sorted([str(v) for v in values]), default=["All"], key=f"filter_{label}")
    selections = {
        "Course": select("Course", df["Course Label"].unique()),
        "Gender": select("Gender", df["Gender Label"].unique()),
        "Age Group": select("Age Group", df["age_group"].dropna().unique()),
        "Scholarship Holder": select("Scholarship Holder", df["Scholarship Status"].unique()),
        "Tuition Status": select("Tuition Status", df["Tuition Status"].unique()),
        "Debtor Status": select("Debtor Status", df["Debtor Status"].unique()),
        "Target": select("Target", df["Target"].dropna().unique()),
    }
    st.markdown("---")
    st.caption("Data Source: UCI Student Dropout & Academic Success")
    st.caption("No Mid-Day Meal, school infrastructure, or TransOrg fields are represented.")

filtered = apply_filters(df, selections)

if page == "Overview":
    overview.render(filtered, meta["validation"])
elif page == "Retention & Outcomes":
    retention.render(filtered)
elif page == "Risk Analysis":
    risk.render(filtered)
elif page == "Academic Performance":
    academic.render(filtered)
elif page == "Financial & Support":
    financial.render(filtered)
elif page == "Student Explorer":
    explorer.render(filtered)
else:
    page_header("AI Analyst", "Reserved for a future release.")
    st.info("The AI Analyst is intentionally not implemented yet. This dashboard uses transparent, data-derived analytics only.")
