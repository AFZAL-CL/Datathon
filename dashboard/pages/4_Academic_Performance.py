import streamlit as st
import plotly.express as px
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.utils import inject_css, page_header, empty_state, section_title

st.set_page_config(page_title="EDUPULSE | Academic Performance", page_icon="🎓", layout="wide")
inject_css()

df, meta = load_data()
if df.empty:
    st.error("Data could not be loaded.")
    st.stop()

selections = render_global_filters(df)
filtered_df = apply_filters(df, selections)

page_header("Academic Performance", "Relationship between academic progress and recorded student outcomes.")

if filtered_df.empty:
    empty_state()
    st.stop()

# Helper aliases for variables
g1 = "Curricular units 1st sem (grade)"
g2 = "Curricular units 2nd sem (grade)"
u1_eval = "Curricular units 1st sem (evaluations)"
u2_eval = "Curricular units 2nd sem (evaluations)"
u1_app = "Curricular units 1st sem (approved)"
u2_app = "Curricular units 2nd sem (approved)"

col1, col2, col3 = st.columns(3)
with col1:
    val = filtered_df[g1].mean() if g1 in filtered_df else 0
    st.metric("Avg 1st Semester Grade", f"{val:.2f}" if val > 0 else "N/A")
with col2:
    val = filtered_df[g2].mean() if g2 in filtered_df else 0
    st.metric("Avg 2nd Semester Grade", f"{val:.2f}" if val > 0 else "N/A")
with col3:
    if "f_b_academic_progress" in filtered_df.columns:
        val = filtered_df["f_b_academic_progress"].mean() * 100
        st.metric("Avg Academic Progress", f"{val:.1f}%")
    elif "academic_progress" in filtered_df.columns:
        val = filtered_df["academic_progress"].mean() * 100
        st.metric("Avg Academic Progress", f"{val:.1f}%")

st.markdown("---")

colA, colB = st.columns(2)

with colA:
    if g1 in filtered_df.columns and g2 in filtered_df.columns:
        section_title("1st vs 2nd Semester Performance", "Comparing grades across semesters")
        fig1 = px.scatter(filtered_df, x=g1, y=g2, color="Target", 
                          color_discrete_map={"Graduate": "#059669", "Enrolled": "#d97706", "Dropout": "#dc2626"},
                          opacity=0.6, marginal_x="histogram", marginal_y="histogram")
        st.plotly_chart(fig1, use_container_width=True)
        st.info("Observation: Students who drop out typically show lower grades in both semesters or structural zeros indicating no exams taken.")

with colB:
    if "Target" in filtered_df.columns:
        if u1_app in filtered_df.columns and u2_app in filtered_df.columns:
            section_title("Approved Units by Outcome", "Total units approved across year 1")
            filtered_df["Total_Approved"] = filtered_df[u1_app] + filtered_df[u2_app]
            fig2 = px.box(filtered_df, x="Target", y="Total_Approved", color="Target",
                          color_discrete_map={"Graduate": "#059669", "Enrolled": "#d97706", "Dropout": "#dc2626"})
            st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

colC, colD = st.columns(2)

with colC:
    if "f_b_grade_improvement" in filtered_df.columns:
        section_title("Grade Improvement Distribution", "Change in grade from 1st to 2nd semester")
        fig3 = px.histogram(filtered_df, x="f_b_grade_improvement", color="Target", 
                            color_discrete_map={"Graduate": "#059669", "Enrolled": "#d97706", "Dropout": "#dc2626"},
                            barmode="overlay", opacity=0.7)
        st.plotly_chart(fig3, use_container_width=True)

with colD:
    if "Course Label" in filtered_df.columns and g1 in filtered_df.columns and g2 in filtered_df.columns:
        section_title("Academic Performance by Course", "Average grades per course")
        course_perf = filtered_df.groupby("Course Label")[[g1, g2]].mean().reset_index()
        fig4 = px.bar(course_perf, x="Course Label", y=[g1, g2], barmode="group",
                      labels={"value": "Average Grade", "variable": "Semester"})
        fig4.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig4, use_container_width=True)
