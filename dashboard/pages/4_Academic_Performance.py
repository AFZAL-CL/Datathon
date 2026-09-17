import streamlit as st
import plotly.express as px
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.utils import inject_css, page_header, empty_state, section_title
from dashboard.src.ai.chart_selector import apply_premium_theme

st.set_page_config(page_title="EDUPULSE | Academic Performance", page_icon="📚", layout="wide")
inject_css()

df, meta = load_data()
if df.empty:
    st.error("Data could not be loaded.")
    st.stop()

selections = render_global_filters(df)
filtered_df = apply_filters(df, selections)

page_header(
    title="Academic Progress Workspace",
    subtitle="Evaluate the relationship between academic engagement, performance, and retention.",
    eyebrow="PERFORMANCE ANALYSIS"
)

if filtered_df.empty:
    empty_state()
    st.stop()

# Overall Academic Progress Metric
avg_progress = filtered_df["f_b_academic_progress"].mean() if "f_b_academic_progress" in filtered_df.columns else 0

st.markdown(f"""
<div style="background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-lg); padding:2rem; text-align:center; margin-bottom:2rem; animation: slideUpFade 600ms var(--transition-med) both;">
    <div style="font-size:0.85rem; font-weight:700; color:var(--text-secondary); letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.5rem;">Average Academic Progress</div>
    <div style="font-size:3.5rem; font-weight:800; color:var(--accent-primary); font-family:'JetBrains Mono', monospace;">{avg_progress:.3f}</div>
    <div style="font-size:0.9rem; color:var(--text-muted); margin-top:0.5rem;">Ratio of approved curricular units to enrolled units.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

section_title("Semester 1 vs Semester 2", "How do grades evolve across the first year?")

if "Curricular units 1st sem (grade)" in filtered_df.columns and "Curricular units 2nd sem (grade)" in filtered_df.columns:
    fig_scatter = px.scatter(
        filtered_df, x="Curricular units 1st sem (grade)", y="Curricular units 2nd sem (grade)",
        color="Target", opacity=0.7,
        color_discrete_map={"Graduate": "#34D399", "Enrolled": "#FBBF24", "Dropout": "#FB7185"},
        labels={"Curricular units 1st sem (grade)": "1st Semester Grade", "Curricular units 2nd sem (grade)": "2nd Semester Grade"}
    )
    
    # Add a diagonal reference line
    max_val = max(filtered_df["Curricular units 1st sem (grade)"].max(), filtered_df["Curricular units 2nd sem (grade)"].max())
    fig_scatter.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="rgba(255,255,255,0.2)", dash="dash"))
    
    fig_scatter = apply_premium_theme(fig_scatter)
    fig_scatter.update_layout(margin=dict(t=20, b=40, l=40, r=40))
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    section_title("Grade Improvement", "Difference between 2nd and 1st semester grades by outcome")
    if "f_b_grade_improvement" in filtered_df.columns:
        fig_box = px.box(
            filtered_df, x="Target", y="f_b_grade_improvement",
            color="Target", color_discrete_map={"Graduate": "#34D399", "Enrolled": "#FBBF24", "Dropout": "#FB7185"},
            labels={"Target": "Outcome", "f_b_grade_improvement": "Grade Improvement"}
        )
        fig_box = apply_premium_theme(fig_box)
        fig_box.update_layout(showlegend=False, margin=dict(t=20, b=40, l=40, r=20))
        st.plotly_chart(fig_box, use_container_width=True)

with col2:
    section_title("Evaluated vs Approved", "Units evaluated vs approved by outcome")
    if "f_b_total_units_evaluated" in filtered_df.columns and "f_b_total_units_approved" in filtered_df.columns:
        avg_units = filtered_df.groupby("Target")[["f_b_total_units_evaluated", "f_b_total_units_approved"]].mean().reset_index()
        fig_bar = px.bar(
            avg_units, x="Target", y=["f_b_total_units_evaluated", "f_b_total_units_approved"],
            barmode="group",
            labels={"value": "Average Units", "variable": "Metric", "Target": "Outcome"},
            color_discrete_sequence=["#8B5CF6", "#0D9488"]
        )
        fig_bar = apply_premium_theme(fig_bar)
        fig_bar.update_layout(margin=dict(t=20, b=40, l=40, r=20))
        st.plotly_chart(fig_bar, use_container_width=True)
