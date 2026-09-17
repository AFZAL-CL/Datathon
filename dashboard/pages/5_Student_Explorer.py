import streamlit as st
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.utils import inject_css, page_header, empty_state, section_title

st.set_page_config(page_title="EDUPULSE | Student Explorer", page_icon="🔍", layout="wide")
inject_css()

df, meta = load_data()
if df.empty:
    st.error("Data could not be loaded.")
    st.stop()

# We need the early df to show early admission risk if applicable
early_df = meta.get("early", df)

selections = render_global_filters(df)
filtered_df = apply_filters(df, selections)

page_header("Dataset Record Explorer", "Inspect a filtered record without implying that the dataset contains a real-world student identifier.")

if filtered_df.empty:
    empty_state()
    st.stop()

st.markdown("""
<div class="notice">
<strong>Note:</strong> The dataset does NOT provide a real-world student ID. We use "Record Index" as the identifier for exploration purposes.
</div>
""", unsafe_allow_html=True)

# Select Record
record_idx = st.selectbox("Record Index (Searchable)", filtered_df["Record Index"].tolist(), format_func=lambda x: f"Record {x}")

# Get the specific row from filtered_df
row = filtered_df[filtered_df["Record Index"] == record_idx].iloc[0]

# Try to get early admission risk from early_df if available
early_risk = "N/A"
if "early_admission_risk" in early_df.columns:
    early_row = early_df[early_df["Record Index"] == record_idx]
    if not early_row.empty:
        early_risk = early_row.iloc[0]["early_admission_risk"]

section_title("Outcome & Risk Segmentation", "Observed record-level fields")

cols = st.columns(4)
with cols[0]:
    st.metric("Recorded Target", row.get("Target", "Unknown"))
with cols[1]:
    st.metric("Early Admission Risk", early_risk)
with cols[2]:
    st.metric("Current Academic Risk", row.get("current_academic_risk", "N/A"))
with cols[3]:
    # Try different academic progress names
    prog = row.get("f_b_academic_progress", row.get("academic_progress", None))
    prog_str = f"{prog * 100:.1f}%" if prog is not None else "N/A"
    st.metric("Academic Progress", prog_str)

st.markdown("---")

sections = {
    "Demographics": ["Gender Label", "Age at enrollment", "age_group", "Displaced", "International", "Educational special needs", "Nacionality", "Nationality"],
    "Admission Profile": ["Course Label", "Application mode", "Application order", "Admission grade", "Admission Grade Band", "Previous qualification", "Previous qualification (grade)"],
    "Financial Indicators": ["Scholarship Status", "Tuition Status", "Debtor Status", "Unemployment rate", "Inflation rate", "GDP"],
    "Academic Profile": [
        "Curricular units 1st sem (enrolled)", "Curricular units 1st sem (evaluations)", "Curricular units 1st sem (approved)", "Curricular units 1st sem (grade)", "Curricular units 1st sem (without evaluations)",
        "Curricular units 2nd sem (enrolled)", "Curricular units 2nd sem (evaluations)", "Curricular units 2nd sem (approved)", "Curricular units 2nd sem (grade)", "Curricular units 2nd sem (without evaluations)"
    ]
}

for title, fields in sections.items():
    with st.expander(title, expanded=True):
        available_fields = [f for f in fields if f in row.index]
        if available_fields:
            data = []
            for f in available_fields:
                data.append({"Attribute": f, "Value": str(row[f])})
            st.table(data)
        else:
            st.caption("No fields available for this section.")
