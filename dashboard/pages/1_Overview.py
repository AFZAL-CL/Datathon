import streamlit as st
import plotly.express as px
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.metrics import calculate_kpis, get_outcome_distribution
from dashboard.src.utils import inject_css, page_header, kpi_row, empty_state, section_title, insight_box
from dashboard.src.ai.chart_selector import apply_premium_theme

# Needs to be top
st.set_page_config(page_title="EDUPULSE | Overview", page_icon="📈", layout="wide")
inject_css()

# Load Data
df, meta = load_data()
if df.empty:
    st.error("Data could not be loaded. Please ensure the data pipeline has been run.")
    st.stop()

# Filters
selections = render_global_filters(df)
filtered_df = apply_filters(df, selections)

page_header(
    title="Understand the student journey.<br/>Find the signals that matter.",
    subtitle="High-level summary of student retention and outcomes across the cohort.",
    eyebrow="STUDENT RETENTION INTELLIGENCE"
)

if filtered_df.empty:
    empty_state()
    st.stop()

# KPIs
kpis = calculate_kpis(filtered_df)
kpi_row([
    ("Total Students", kpis["Total Students"], "Filtered dataset"),
    ("Dropout Rate", kpis["Dropout Rate"], "Recorded Dropouts"),
    ("Graduation Rate", kpis["Graduation Rate"], "Recorded Graduates"),
    ("Enrolled Rate", kpis["Enrolled Rate"], "Currently Enrolled"),
    ("High-Risk Students", kpis["High-Risk Students"], "Early Risk Segmentation")
])

st.markdown("<hr>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    section_title("Outcome Distribution", "Overall recorded outcomes")
    target_counts = filtered_df["Target"].value_counts().reset_index()
    target_counts.columns = ["Target", "Count"]
    
    fig1 = px.pie(
        target_counts, values="Count", names="Target", hole=0.7,
        color="Target", color_discrete_map={"Graduate": "#34D399", "Enrolled": "#FBBF24", "Dropout": "#FB7185"}
    )
    fig1 = apply_premium_theme(fig1)
    fig1.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
    fig1.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#0A1118', width=2)))
    st.plotly_chart(fig1, use_container_width=True)
    
    section_title("Executive Insights", "Key signals from the current view")
    
    total = len(filtered_df)
    dropout = len(filtered_df[filtered_df["Target"] == "Dropout"])
    dropout_pct = (dropout / total) * 100 if total > 0 else 0
    
    insight_box(
        f"<strong>Observation:</strong> Students recorded as Dropout represent {dropout_pct:.1f}% of the currently filtered dataset.",
        kind="risk" if dropout_pct > 20 else "success"
    )
    
    if "Tuition Status" in filtered_df.columns:
        not_up_to_date = len(filtered_df[(filtered_df["Target"] == "Dropout") & (filtered_df["Tuition Status"] == "Not up to date")])
        if dropout > 0:
            fin_pct = (not_up_to_date / dropout) * 100
            insight_box(
                f"<strong>Observation:</strong> {fin_pct:.1f}% of dropped-out students in this view had tuition fees not up to date.",
                kind="warning"
            )

with col2:
    section_title("Outcome by Demographics & Status", "Breakdown of outcomes by key dimensions")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Course", "Age Group", "Gender", "Scholarship", "Tuition", "Debtor"])
    
    def plot_bar(dimension, tab):
        with tab:
            dist = get_outcome_distribution(filtered_df, dimension)
            if dist.empty:
                st.info(f"No data for {dimension}")
                return
            
            fig = px.bar(
                dist, x=dimension, y=["Graduate", "Enrolled", "Dropout"],
                labels={"value": "Percentage (%)", "variable": "Outcome", dimension: ""},
                color_discrete_map={"Graduate": "#34D399", "Enrolled": "#FBBF24", "Dropout": "#FB7185"},
                barmode="stack"
            )
            fig = apply_premium_theme(fig)
            fig.update_layout(xaxis_tickangle=-45, legend_title="Outcome", margin=dict(t=20, b=80))
            st.plotly_chart(fig, use_container_width=True)

    plot_bar("Course Label", tab1)
    plot_bar("age_group", tab2)
    plot_bar("Gender Label", tab3)
    plot_bar("Scholarship Status", tab4)
    plot_bar("Tuition Status", tab5)
    plot_bar("Debtor Status", tab6)
