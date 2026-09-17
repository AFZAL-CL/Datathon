import streamlit as st
import sys
from pathlib import Path

# Add the project root to sys.path to allow imports from dashboard.src
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.src.utils import inject_css

# Page Configuration MUST be the first Streamlit command
st.set_page_config(
    page_title="EDUPULSE | Executive Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
inject_css()

st.title("EDUPULSE Executive Dashboard")
st.markdown("### Student Retention & Academic Welfare Intelligence")
st.markdown("---")

st.markdown("""
Welcome to the EDUPULSE Executive Analytics Dashboard. 

Please use the sidebar to navigate through the different modules:
- **Overview**: High-level KPIs and outcome distributions.
- **Retention & Outcomes**: Detailed retention patterns and interactive outcome matrices.
- **Risk Analysis**: Early admission risk vs current academic risk segmentation.
- **Academic Performance**: Relationship between academic progress and student outcomes.
- **Student Explorer**: Interactive dataset record explorer.
- **Data Quality**: Data pipeline lineage, schema corrections, and dataset integrity checks.
- **AI Analyst**: Future module for intelligent insights.
""")

st.info("👈 Select a page from the sidebar to begin.")
