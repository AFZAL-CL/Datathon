import streamlit as st
import plotly.express as px
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.metrics import calculate_kpis, get_outcome_distribution
from dashboard.src.utils import inject_css, page_header, kpi_row, empty_state, section_title

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

page_header("Executive Overview", "High-level summary of student retention and outcomes.")

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
    ("High-Risk Students", kpis["High-Risk Students"], "Based on Early Risk")
])

st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    section_title("Student Outcome Distribution", "Overall recorded outcomes")
    target_counts = filtered_df["Target"].value_counts().reset_index()
    target_counts.columns = ["Target", "Count"]
    
    color_map = {"Graduate": "var(--color-graduate)", "Enrolled": "var(--color-enrolled)", "Dropout": "var(--color-dropout)"}
    fig1 = px.pie(target_counts, values="Count", names="Target", hole=0.6,
                 color="Target", color_discrete_map={"Graduate": "#059669", "Enrolled": "#d97706", "Dropout": "#dc2626"})
    fig1.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("### Key Signals")
    
    # Calculate some dynamic key signals
    total = len(filtered_df)
    dropout = len(filtered_df[filtered_df["Target"] == "Dropout"])
    dropout_pct = (dropout / total) * 100 if total > 0 else 0
    
    st.markdown(f'''
    <div class="signal-box">
        <strong>Observation:</strong> Students recorded as Dropout represent {dropout_pct:.1f}% of the currently filtered dataset.
    </div>
    ''', unsafe_allow_html=True)
    
    if "Tuition Status" in filtered_df.columns:
        not_up_to_date = len(filtered_df[(filtered_df["Target"] == "Dropout") & (filtered_df["Tuition Status"] == "Not up to date")])
        if dropout > 0:
            fin_pct = (not_up_to_date / dropout) * 100
            st.markdown(f'''
            <div class="signal-box" style="border-left-color: #d97706;">
                <strong>Observation:</strong> {fin_pct:.1f}% of dropped-out students in this view had tuition fees not up to date.
            </div>
            ''', unsafe_allow_html=True)

with col2:
    section_title("Outcome by Demographics and Status", "Breakdown of outcomes by key dimensions")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Course", "Age Group", "Gender", "Scholarship", "Tuition", "Debtor"])
    
    def plot_bar(dimension, tab):
        with tab:
            dist = get_outcome_distribution(filtered_df, dimension)
            if dist.empty:
                st.info(f"No data for {dimension}")
                return
            
            fig = px.bar(dist, x=dimension, y=["Graduate", "Enrolled", "Dropout"],
                         title=f"Outcome Distribution by {dimension}",
                         labels={"value": "Percentage (%)", "variable": "Outcome"},
                         color_discrete_map={"Graduate": "#059669", "Enrolled": "#d97706", "Dropout": "#dc2626"},
                         barmode="stack")
            fig.update_layout(xaxis_tickangle=-45, legend_title="Outcome", margin=dict(b=100))
            st.plotly_chart(fig, use_container_width=True)

    plot_bar("Course Label", tab1)
    plot_bar("age_group", tab2)
    plot_bar("Gender Label", tab3)
    plot_bar("Scholarship Status", tab4)
    plot_bar("Tuition Status", tab5)
    plot_bar("Debtor Status", tab6)
