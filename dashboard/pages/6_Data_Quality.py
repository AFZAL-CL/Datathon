import streamlit as st
import pandas as pd
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.utils import inject_css, page_header, empty_state, section_title

st.set_page_config(page_title="EDUPULSE | Data Quality", page_icon="🛡️", layout="wide")
inject_css()

df, meta = load_data()
if df.empty:
    st.error("Data could not be loaded.")
    st.stop()

# No global filters needed for data quality page usually, but keeping sidebar consistent
selections = render_global_filters(df)

page_header("Data Quality & Integrity", "Professional data-quality summary and pipeline lineage.")

section_title("Data Lineage", "Pipeline from raw data to dashboard")

st.markdown("""
```mermaid
graph TD
    A[Raw CSV: data/raw/student_dropout.csv] --> B(Validation)
    B --> C(Cleaning)
    C --> D(Feature Engineering)
    D --> E(Analytics / Risk Datasets)
    E --> F[EDUPULSE Dashboard]
```
""")

section_title("Dataset Summary Statistics", "Row and column facts")

validation = meta.get("validation", {})
raw_rows = validation.get("raw_rows", 4424)
clean_rows = validation.get("clean_rows", 4424)
raw_cols = validation.get("raw_columns", 37)
clean_cols = validation.get("clean_columns", 37)
duplicates = validation.get("duplicates", 0)
nulls = validation.get("null_values", 0)

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Raw Rows", f"{raw_rows:,}")
col2.metric("Cleaned Rows", f"{clean_rows:,}")
col3.metric("Raw Columns", f"{raw_cols}")
col4.metric("Cleaned Columns", f"{clean_cols}")
col5.metric("Duplicate Rows", f"{duplicates}")
col6.metric("Null Values", f"{nulls}")

st.markdown("---")

colA, colB = st.columns(2)

with colA:
    section_title("Schema Corrections", "Known issues addressed during cleaning")
    corrections = [
        {"Issue": "Nacionality (Typo)", "Action": "Renamed to Nationality"},
        {"Issue": "Daytime/evening attendance\\t", "Action": "Removed trailing tab"},
        {"Issue": "Target Variable", "Action": "Categorical string mapped appropriately"}
    ]
    st.table(pd.DataFrame(corrections))

with colB:
    section_title("Target Distribution", "Distribution of outcomes in the dataset")
    target_counts = df["Target"].value_counts().reset_index()
    target_counts.columns = ["Outcome", "Count"]
    target_counts["Percentage"] = (target_counts["Count"] / len(df) * 100).round(1).astype(str) + "%"
    st.table(target_counts)

st.markdown("---")
st.info("The data pipeline strictly preserves original data context without fabricating causal links or missing welfare/infrastructure fields.")
