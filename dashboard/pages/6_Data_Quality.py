import streamlit as st
import pandas as pd
from dashboard.src.utils import inject_css, page_header, section_title

st.set_page_config(page_title="EDUPULSE | Data Quality", page_icon="🛡️", layout="wide")
inject_css()

page_header(
    title="Data Lineage & Quality",
    subtitle="Tracking the integrity of the EDUPULSE intelligence pipeline.",
    eyebrow="SYSTEM HEALTH"
)

st.markdown("<hr>", unsafe_allow_html=True)

col_pipe, col_stats = st.columns([1, 1], gap="large")

with col_pipe:
    section_title("Pipeline Visualization", "Stages of data transformation")
    
    st.markdown("""
    <div style="background:var(--surface); border:1px solid var(--border); padding:2rem; border-radius:var(--radius-lg); font-family:'JetBrains Mono', monospace; font-size:0.9rem; line-height:1.8; animation: slideUpFade 800ms var(--transition-slow) both;">
        <div style="color:var(--text-secondary); margin-bottom:1rem;">RAW DATASTREAM</div>
        <div style="padding:1rem; border-left:2px solid var(--text-muted); margin-left:1rem;">
            <div style="color:var(--text-primary); font-weight:600;">raw/student_dropout.csv</div>
            <div style="color:var(--text-muted); font-size:0.8rem;">↓ Extract</div>
        </div>
        
        <div style="color:var(--text-secondary); margin:1rem 0;">VALIDATION</div>
        <div style="padding:1rem; border-left:2px solid var(--accent-secondary); margin-left:1rem;">
            <div style="color:var(--text-primary); font-weight:600;">src/data/validation.py</div>
            <div style="color:var(--text-muted); font-size:0.8rem;">↓ Integrity Check</div>
        </div>
        
        <div style="color:var(--text-secondary); margin:1rem 0;">CLEANING & ENGINEERING</div>
        <div style="padding:1rem; border-left:2px solid var(--accent-primary); margin-left:1rem;">
            <div style="color:var(--text-primary); font-weight:600;">src/data/preprocessing.py</div>
            <div style="color:var(--text-muted); font-size:0.8rem;">↓ Transform</div>
        </div>
        
        <div style="color:var(--success); font-weight:700; margin-top:2rem; display:flex; align-items:center; gap:0.5rem;">
            <span style="display:inline-block; width:8px; height:8px; background:var(--success); border-radius:50%;"></span>
            EDUPULSE CORE (processed/)
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_stats:
    section_title("Integrity Metrics", "Current state of the production dataset")
    
    def metric_card(label, val, note, delay="200ms", color="var(--accent-primary)"):
        st.markdown(f"""
        <div style="background:var(--surface); border:1px solid var(--border); padding:1.5rem; border-radius:var(--radius-md); margin-bottom:1rem; border-left:4px solid {color}; animation: slideUpFade 600ms var(--transition-med) {delay} both;">
            <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                <div>
                    <div style="font-size:0.8rem; font-weight:700; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.5rem;">{label}</div>
                    <div style="font-size:2.5rem; font-weight:700; color:var(--text-primary); font-family:'JetBrains Mono', monospace; line-height:1;">{val}</div>
                </div>
                <div style="font-size:0.85rem; color:var(--text-muted); text-align:right;">{note}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    metric_card("Total Records", "4,424", "Verified rows", delay="200ms", color="var(--accent-primary)")
    metric_card("Schema Columns", "37", "36 Features + 1 Target", delay="300ms", color="var(--accent-secondary)")
    metric_card("Null Values", "0", "Imputation not required", delay="400ms", color="var(--success)")
    metric_card("Duplicate Rows", "0", "100% unique records", delay="500ms", color="var(--success)")
    metric_card("Schema Fixes", "2", "Nationality, Age at enrollment", delay="600ms", color="var(--warning)")
