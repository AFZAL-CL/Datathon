import streamlit as st
import plotly.express as px
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.utils import inject_css, page_header, empty_state, section_title

st.set_page_config(page_title="EDUPULSE | Risk Analysis", page_icon="⚠️", layout="wide")
inject_css()

df, meta = load_data()
if df.empty:
    st.error("Data could not be loaded.")
    st.stop()
early_df = meta.get("early", df.copy())

selections = render_global_filters(df)
filtered_df = apply_filters(df, selections)

# Since we need to filter the early_df as well to match global filters:
# We apply the same selections to early_df if the columns exist.
filtered_early = apply_filters(early_df, selections)

page_header("Risk Analysis", "Segmentation of student risk profiles.")

if filtered_df.empty:
    empty_state()
    st.stop()

st.markdown("""
<div class="notice">
This page separates risk into two distinct scenarios. Scenario A uses only information available at admission, while Scenario B incorporates post-enrolment academic performance.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# SCENARIO A
# ==========================================
section_title("SCENARIO A: EARLY / ADMISSION-TIME RISK", "This scenario uses information available at or near admission/enrolment and is intended for early risk segmentation.")

if "early_admission_risk" in filtered_early.columns:
    col1, col2 = st.columns([1, 2])
    with col1:
        risk_counts = filtered_early["early_admission_risk"].value_counts().reset_index()
        risk_counts.columns = ["Risk Level", "Count"]
        fig1 = px.pie(risk_counts, values="Count", names="Risk Level", title="Early Admission Risk Distribution", hole=0.5)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        if "Course Label" in filtered_early.columns:
            course_risk = filtered_early.groupby(["Course Label", "early_admission_risk"]).size().unstack(fill_value=0).reset_index()
            fig2 = px.bar(course_risk, x="Course Label", y=course_risk.columns[1:], title="Risk by Course", barmode="stack")
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)
            
    col3, col4, col5 = st.columns(3)
    
    def plot_early_risk(dimension, title, col):
        if dimension in filtered_early.columns:
            risk = filtered_early.groupby([dimension, "early_admission_risk"]).size().unstack(fill_value=0).reset_index()
            fig = px.bar(risk, x=dimension, y=risk.columns[1:], title=title, barmode="stack")
            fig.update_layout(xaxis_tickangle=-45)
            with col:
                st.plotly_chart(fig, use_container_width=True)

    plot_early_risk("age_group", "Risk by Age Group", col3)
    plot_early_risk("Scholarship holder", "Risk by Scholarship (1=Yes)", col4)
    plot_early_risk("Tuition fees up to date", "Risk by Tuition Status (1=Yes)", col5)
    
    col6, col7 = st.columns(2)
    plot_early_risk("Previous qualification", "Risk by Previous Qualification", col6)
    plot_early_risk("Admission Grade Band", "Risk by Admission Grade Band", col7)
else:
    st.info("early_admission_risk feature not found in data.")

st.markdown("---")

# ==========================================
# SCENARIO B
# ==========================================
section_title("SCENARIO B: CURRENT ACADEMIC RISK", "Post-enrolment / current academic risk based on semester performance.")

if "current_academic_risk" in filtered_df.columns:
    col1, col2 = st.columns([1, 2])
    with col1:
        c_risk_counts = filtered_df["current_academic_risk"].value_counts().reset_index()
        c_risk_counts.columns = ["Risk Level", "Count"]
        fig3 = px.pie(c_risk_counts, values="Count", names="Risk Level", title="Current Academic Risk Distribution", hole=0.5)
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        if "Course Label" in filtered_df.columns:
            c_course_risk = filtered_df.groupby(["Course Label", "current_academic_risk"]).size().unstack(fill_value=0).reset_index()
            fig4 = px.bar(c_course_risk, x="Course Label", y=c_course_risk.columns[1:], title="Current Risk by Course", barmode="stack")
            fig4.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig4, use_container_width=True)
            
    col3, col4, col5 = st.columns(3)
    
    # Semester performance features vs current risk
    if "f_b_academic_progress" in filtered_df.columns:
        with col3:
            fig5 = px.box(filtered_df, x="current_academic_risk", y="f_b_academic_progress", title="Academic Progress vs Risk")
            st.plotly_chart(fig5, use_container_width=True)
    elif "academic_progress" in filtered_df.columns:
        with col3:
            fig5 = px.box(filtered_df, x="current_academic_risk", y="academic_progress", title="Academic Progress vs Risk")
            st.plotly_chart(fig5, use_container_width=True)
            
    if "Target" in filtered_df.columns and "f_b_academic_progress" in filtered_df.columns:
        with col4:
            fig6 = px.box(filtered_df, x="Target", y="f_b_academic_progress", title="Academic Progress vs Outcome", color="Target", color_discrete_map={"Graduate": "#059669", "Enrolled": "#d97706", "Dropout": "#dc2626"})
            st.plotly_chart(fig6, use_container_width=True)
    elif "Target" in filtered_df.columns and "academic_progress" in filtered_df.columns:
        with col4:
            fig6 = px.box(filtered_df, x="Target", y="academic_progress", title="Academic Progress vs Outcome", color="Target", color_discrete_map={"Graduate": "#059669", "Enrolled": "#d97706", "Dropout": "#dc2626"})
            st.plotly_chart(fig6, use_container_width=True)
            
    if "f_b_grade_improvement" in filtered_df.columns:
        with col5:
            fig7 = px.box(filtered_df, x="Target", y="f_b_grade_improvement", title="Grade Improvement vs Outcome", color="Target", color_discrete_map={"Graduate": "#059669", "Enrolled": "#d97706", "Dropout": "#dc2626"})
            st.plotly_chart(fig7, use_container_width=True)
            
else:
    st.info("current_academic_risk feature not found in data.")
