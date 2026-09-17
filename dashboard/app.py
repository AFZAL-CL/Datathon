import streamlit as st
import sys
from pathlib import Path

# Add the project root to sys.path to allow imports from dashboard.src
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.src.utils import inject_css, page_header

# Page Configuration MUST be the first Streamlit command
st.set_page_config(
    page_title="EDUPULSE | Executive Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
inject_css()

page_header(
    title="Student Retention &<br/>Academic Intelligence",
    subtitle="Understand the patterns behind student outcomes.",
    eyebrow="EDUPULSE / INTELLIGENCE"
)

st.markdown("---")

st.markdown("""
<div style="font-size:1.1rem; color:var(--text-secondary); max-width:800px; line-height:1.6; margin-bottom:2rem;">
Please use the sidebar to navigate through the modules:
<ul style="margin-top:1rem; list-style-type:none; padding:0;">
    <li style="margin-bottom:0.75rem;"><strong>Overview</strong> — High-level KPIs and outcome distributions.</li>
    <li style="margin-bottom:0.75rem;"><strong>Retention & Outcomes</strong> — Detailed retention patterns.</li>
    <li style="margin-bottom:0.75rem;"><strong>Risk Analysis</strong> — Early admission risk vs current academic risk.</li>
    <li style="margin-bottom:0.75rem;"><strong>Academic Performance</strong> — Relationship between progress and outcomes.</li>
    <li style="margin-bottom:0.75rem;"><strong>Student Explorer</strong> — Interactive dataset record explorer.</li>
    <li style="margin-bottom:0.75rem;"><strong>Data Quality</strong> — Pipeline lineage and integrity.</li>
    <li style="margin-bottom:0.75rem;"><strong>AI Analyst</strong> — Natural language analytics layer.</li>
</ul>
</div>
""", unsafe_allow_html=True)
