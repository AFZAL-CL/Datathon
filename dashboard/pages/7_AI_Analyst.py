import streamlit as st
from dashboard.src.utils import inject_css, page_header

st.set_page_config(page_title="EDUPULSE | AI Analyst", page_icon="🤖", layout="wide")
inject_css()

# Since we don't need to load the data to show this placeholder
page_header("AI Analyst — Next Module", "Future module for intelligent insights.")

st.info("The AI Analyst is intentionally not implemented yet. This dashboard uses transparent, data-derived analytics only.")
