import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.utils import inject_css, page_header, empty_state, section_title

st.set_page_config(page_title="EDUPULSE | Retention & Outcomes", page_icon="📊", layout="wide")
inject_css()

df, meta = load_data()
if df.empty:
    st.error("Data could not be loaded.")
    st.stop()

selections = render_global_filters(df)
filtered_df = apply_filters(df, selections)

page_header("Retention & Outcomes", "Focus specifically on retention patterns and outcomes.")

if filtered_df.empty:
    empty_state()
    st.stop()

section_title("Dropout Rates by Dimension", "Visualizing attrition across different student characteristics")

def plot_dropout_rate(dimension, title):
    if dimension not in filtered_df.columns:
        return
    
    # Calculate dropout rate per dimension
    counts = filtered_df.groupby([dimension, "Target"]).size().unstack(fill_value=0)
    if "Dropout" not in counts.columns:
        st.info(f"No dropouts in {dimension}")
        return
        
    counts["Total"] = counts.sum(axis=1)
    counts["Dropout Rate"] = (counts["Dropout"] / counts["Total"]) * 100
    counts = counts.reset_index().sort_values("Dropout Rate", ascending=False)
    
    fig = px.bar(counts, x=dimension, y="Dropout Rate", title=title,
                 labels={"Dropout Rate": "Dropout Rate (%)"},
                 color="Dropout Rate", color_continuous_scale="Reds")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    plot_dropout_rate("Course Label", "Dropout Rate by Course")
    plot_dropout_rate("Scholarship Status", "Dropout Rate by Scholarship Status")
    plot_dropout_rate("Previous qualification", "Dropout Rate by Previous Qualification")

with col2:
    plot_dropout_rate("age_group", "Dropout Rate by Age Group")
    plot_dropout_rate("Tuition Status", "Dropout Rate by Tuition Status")
    plot_dropout_rate("Application mode", "Dropout Rate by Application Mode")

with col3:
    plot_dropout_rate("Gender Label", "Dropout Rate by Gender")
    plot_dropout_rate("Debtor Status", "Dropout Rate by Debtor Status")
    plot_dropout_rate("Admission Grade Band", "Dropout Rate by Admission Grade Band")

st.markdown("---")

section_title("Interactive Outcome Matrix", "Detailed crosstabulation of outcomes by course")

metric_type = st.radio("Display Metric", ["Count", "Percentage"], horizontal=True)

if "Course Label" in filtered_df.columns and "Target" in filtered_df.columns:
    matrix = pd.crosstab(filtered_df["Course Label"], filtered_df["Target"])
    outcomes = [col for col in ["Graduate", "Enrolled", "Dropout"] if col in matrix.columns]
    matrix = matrix[outcomes]
    
    if metric_type == "Percentage":
        matrix = matrix.div(matrix.sum(axis=1), axis=0) * 100
        st.dataframe(matrix.style.format("{:.1f}%").background_gradient(cmap="Greens", subset=["Graduate"]).background_gradient(cmap="Oranges", subset=["Enrolled"]).background_gradient(cmap="Reds", subset=["Dropout"]), use_container_width=True)
    else:
        st.dataframe(matrix.style.background_gradient(cmap="Greens", subset=["Graduate"]).background_gradient(cmap="Oranges", subset=["Enrolled"]).background_gradient(cmap="Reds", subset=["Dropout"]), use_container_width=True)
