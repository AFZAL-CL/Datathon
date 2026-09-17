import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.utils import inject_css, page_header, empty_state, section_title, insight_box
from dashboard.src.ai.chart_selector import apply_premium_theme

st.set_page_config(page_title="EDUPULSE | Risk Analysis", page_icon="⚠️", layout="wide")
inject_css()

df, meta = load_data()
if df.empty:
    st.error("Data could not be loaded.")
    st.stop()

# Get early dataset if available
early_df = meta.get("early", df)

selections = render_global_filters(df)
filtered_df = apply_filters(df, selections)
filtered_early = apply_filters(early_df, selections)

page_header(
    title="Risk Analysis",
    subtitle="Understand vulnerability at the point of admission vs. current academic progress.",
    eyebrow="SCENARIO SEGMENTATION"
)

if filtered_df.empty:
    empty_state()
    st.stop()

st.markdown("<hr>", unsafe_allow_html=True)

# -----------------------------------
# EARLY / ADMISSION-TIME RISK
# -----------------------------------
st.markdown("""
<div style="background:var(--surface); padding:2rem; border-radius:var(--radius-lg); border-left:4px solid var(--accent-secondary); margin-bottom:2rem;">
    <h3 style="margin-top:0; color:var(--text-primary); letter-spacing:-0.02em;">EARLY / ADMISSION-TIME RISK (SCENARIO A)</h3>
    <p style="color:var(--text-secondary); margin-bottom:0;">Risk calculated using only demographic, socio-economic, and admission variables (no academic history).</p>
</div>
""", unsafe_allow_html=True)

col_e1, col_e2 = st.columns([1, 2], gap="large")

with col_e1:
    early_counts = filtered_early["early_admission_risk"].value_counts().reset_index()
    early_counts.columns = ["Risk Level", "Count"]
    
    fig_e1 = px.pie(
        early_counts, values="Count", names="Risk Level", hole=0.6,
        color="Risk Level", color_discrete_map={"High": "#FB7185", "Medium": "#FBBF24", "Low": "#34D399"}
    )
    fig_e1 = apply_premium_theme(fig_e1)
    fig_e1.update_layout(showlegend=True, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_e1, use_container_width=True)
    
    high_early = len(filtered_early[filtered_early["early_admission_risk"] == "High"])
    total_early = len(filtered_early)
    if total_early > 0:
        insight_box(f"<strong>{high_early} students</strong> ({(high_early/total_early)*100:.1f}%) were classified as High Risk at the point of admission based on demographics and socio-economic factors.", kind="warning")

with col_e2:
    if "Course Label" in filtered_early.columns:
        course_risk = filtered_early.groupby(["Course Label", "early_admission_risk"]).size().unstack(fill_value=0)
        course_risk = course_risk.reindex(columns=["High", "Medium", "Low"], fill_value=0)
        course_risk["Total"] = course_risk.sum(axis=1)
        course_risk["High Risk Rate"] = (course_risk["High"] / course_risk["Total"]) * 100
        course_risk = course_risk.sort_values("High Risk Rate", ascending=True).reset_index()
        
        fig_e2 = px.bar(
            course_risk, y="Course Label", x="High Risk Rate", orientation='h',
            title="Early High Risk Rate by Course",
            labels={"High Risk Rate": "High Risk Rate (%)", "Course Label": ""},
            color="High Risk Rate", color_continuous_scale="Purples"
        )
        fig_e2 = apply_premium_theme(fig_e2)
        fig_e2.update_layout(coloraxis_showscale=False, margin=dict(l=20, r=20, t=40, b=40))
        st.plotly_chart(fig_e2, use_container_width=True)


st.markdown("<hr>", unsafe_allow_html=True)

# -----------------------------------
# CURRENT ACADEMIC RISK
# -----------------------------------
st.markdown("""
<div style="background:var(--surface); padding:2rem; border-radius:var(--radius-lg); border-left:4px solid var(--accent-primary); margin-bottom:2rem;">
    <h3 style="margin-top:0; color:var(--text-primary); letter-spacing:-0.02em;">CURRENT ACADEMIC RISK (SCENARIO B)</h3>
    <p style="color:var(--text-secondary); margin-bottom:0;">Risk calculated incorporating real-time academic performance (grades, evaluated units, progress).</p>
</div>
""", unsafe_allow_html=True)

col_c1, col_c2 = st.columns([1, 2], gap="large")

with col_c1:
    curr_counts = filtered_df["current_academic_risk"].value_counts().reset_index()
    curr_counts.columns = ["Risk Level", "Count"]
    
    fig_c1 = px.pie(
        curr_counts, values="Count", names="Risk Level", hole=0.6,
        color="Risk Level", color_discrete_map={"High": "#FB7185", "Medium": "#FBBF24", "Low": "#34D399"}
    )
    fig_c1 = apply_premium_theme(fig_c1)
    fig_c1.update_layout(showlegend=True, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_c1, use_container_width=True)
    
    high_curr = len(filtered_df[filtered_df["current_academic_risk"] == "High"])
    total_curr = len(filtered_df)
    if total_curr > 0:
        insight_box(f"<strong>{high_curr} students</strong> ({(high_curr/total_curr)*100:.1f}%) are currently classified as High Risk based on their active academic performance.", kind="risk")

with col_c2:
    if "Course Label" in filtered_df.columns:
        course_curr = filtered_df.groupby(["Course Label", "current_academic_risk"]).size().unstack(fill_value=0)
        course_curr = course_curr.reindex(columns=["High", "Medium", "Low"], fill_value=0)
        course_curr["Total"] = course_curr.sum(axis=1)
        course_curr["High Risk Rate"] = (course_curr["High"] / course_curr["Total"]) * 100
        course_curr = course_curr.sort_values("High Risk Rate", ascending=True).reset_index()
        
        fig_c2 = px.bar(
            course_curr, y="Course Label", x="High Risk Rate", orientation='h',
            title="Current High Risk Rate by Course",
            labels={"High Risk Rate": "High Risk Rate (%)", "Course Label": ""},
            color="High Risk Rate", color_continuous_scale="Teal"
        )
        fig_c2 = apply_premium_theme(fig_c2)
        fig_c2.update_layout(coloraxis_showscale=False, margin=dict(l=20, r=20, t=40, b=40))
        st.plotly_chart(fig_c2, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

section_title("Academic Progress by Risk Segment", "How do current risk bands perform academically?")

if "f_b_academic_progress" in filtered_df.columns:
    fig_box = px.box(
        filtered_df, x="current_academic_risk", y="f_b_academic_progress",
        category_orders={"current_academic_risk": ["High", "Medium", "Low"]},
        color="current_academic_risk",
        color_discrete_map={"High": "#FB7185", "Medium": "#FBBF24", "Low": "#34D399"},
        labels={"current_academic_risk": "Risk Band", "f_b_academic_progress": "Academic Progress"}
    )
    fig_box = apply_premium_theme(fig_box)
    fig_box.update_layout(showlegend=False, margin=dict(t=40, b=40, l=40, r=40))
    st.plotly_chart(fig_box, use_container_width=True)
