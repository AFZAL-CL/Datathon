import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.utils import inject_css, page_header, empty_state, section_title
from dashboard.src.ai.chart_selector import apply_premium_theme

st.set_page_config(page_title="EDUPULSE | Retention & Outcomes", page_icon="📊", layout="wide")
inject_css()

df, meta = load_data()
if df.empty:
    st.error("Data could not be loaded.")
    st.stop()

selections = render_global_filters(df)
filtered_df = apply_filters(df, selections)

page_header(
    title="Retention & Outcomes",
    subtitle="Where are recorded outcomes diverging? Analyze attrition across student characteristics.",
    eyebrow="OUTCOME ANALYSIS"
)

if filtered_df.empty:
    empty_state()
    st.stop()

st.markdown("<hr>", unsafe_allow_html=True)

def plot_dropout_rate(dimension, title, orientation='v'):
    if dimension not in filtered_df.columns:
        return None
    
    counts = filtered_df.groupby([dimension, "Target"]).size().unstack(fill_value=0)
    if "Dropout" not in counts.columns:
        return None
        
    counts["Total"] = counts.sum(axis=1)
    counts["Dropout Rate"] = (counts["Dropout"] / counts["Total"]) * 100
    counts = counts.reset_index().sort_values("Dropout Rate", ascending=True if orientation == 'h' else False)
    
    if orientation == 'h':
        fig = px.bar(counts, y=dimension, x="Dropout Rate", title=title,
                     labels={"Dropout Rate": "Dropout Rate (%)", dimension: ""},
                     color="Dropout Rate", color_continuous_scale="Reds", orientation='h')
    else:
        fig = px.bar(counts, x=dimension, y="Dropout Rate", title=title,
                     labels={"Dropout Rate": "Dropout Rate (%)", dimension: ""},
                     color="Dropout Rate", color_continuous_scale="Reds")
        fig.update_layout(xaxis_tickangle=-45)
        
    fig = apply_premium_theme(fig)
    fig.update_layout(coloraxis_showscale=False, margin=dict(t=40, b=40, l=40, r=20))
    return fig

# Primary layout
section_title("RETENTION SIGNALS", "Primary divergence vectors")

col_main, col_side = st.columns([2, 1], gap="large")

with col_main:
    fig_course = plot_dropout_rate("Course Label", "Dropout Rate by Course")
    if fig_course:
        st.plotly_chart(fig_course, use_container_width=True)

with col_side:
    fig_age = plot_dropout_rate("age_group", "Dropout Rate by Age Group", orientation='h')
    if fig_age:
        st.plotly_chart(fig_age, use_container_width=True)
        
    fig_gender = plot_dropout_rate("Gender Label", "Dropout Rate by Gender", orientation='h')
    if fig_gender:
        st.plotly_chart(fig_gender, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

section_title("WHO IS MOST AT RISK?", "Secondary demographic and status indicators")

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    f1 = plot_dropout_rate("Scholarship Status", "By Scholarship")
    if f1: st.plotly_chart(f1, use_container_width=True)
with col2:
    f2 = plot_dropout_rate("Tuition Status", "By Tuition")
    if f2: st.plotly_chart(f2, use_container_width=True)
with col3:
    f3 = plot_dropout_rate("Debtor Status", "By Debtor Status")
    if f3: st.plotly_chart(f3, use_container_width=True)
with col4:
    f4 = plot_dropout_rate("Application mode", "By Application Mode")
    if f4: st.plotly_chart(f4, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

section_title("Interactive Outcome Matrix", "Detailed crosstabulation of outcomes by course")

metric_type = st.radio("Display Metric", ["Count", "Percentage"], horizontal=True)

if "Course Label" in filtered_df.columns and "Target" in filtered_df.columns:
    matrix = pd.crosstab(filtered_df["Course Label"], filtered_df["Target"])
    outcomes = [col for col in ["Graduate", "Enrolled", "Dropout"] if col in matrix.columns]
    matrix = matrix[outcomes]
    
    # Custom styling for pandas dataframe to match dark theme
    def style_df(df, metric):
        styled = df.style
        if metric == "Percentage":
            styled = styled.format("{:.1f}%")
            
        return styled.set_table_styles([
            {'selector': 'th', 'props': [('background-color', 'var(--bg-secondary)'), ('color', 'var(--text-secondary)'), ('font-weight', '600')]},
            {'selector': 'td', 'props': [('background-color', 'var(--bg-primary)'), ('color', 'var(--text-primary)')]},
            {'selector': 'tr:hover td', 'props': [('background-color', 'var(--surface-hover)')]},
        ])
    
    if metric_type == "Percentage":
        matrix = matrix.div(matrix.sum(axis=1), axis=0) * 100
        
    st.dataframe(style_df(matrix, metric_type), use_container_width=True)
