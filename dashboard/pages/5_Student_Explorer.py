import streamlit as st
import pandas as pd
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.utils import inject_css, page_header, empty_state, section_title

st.set_page_config(page_title="EDUPULSE | Student Explorer", page_icon="🔍", layout="wide")
inject_css()

df, meta = load_data()
if df.empty:
    st.error("Data could not be loaded.")
    st.stop()

# Generate deterministic pseudo-IDs for display based on row index
df = df.copy()
df['Record ID'] = ['REC-' + str(i).zfill(4) for i in range(len(df))]

selections = render_global_filters(df)
filtered_df = apply_filters(df, selections)

page_header(
    title="Student Record Explorer",
    subtitle="Inspect individual records from the dataset.",
    eyebrow="RECORD DETAIL"
)

if filtered_df.empty:
    empty_state()
    st.stop()

st.markdown("<hr>", unsafe_allow_html=True)

# Layout: List on left, details on right
col_list, col_detail = st.columns([1, 2], gap="large")

with col_list:
    st.markdown('<div style="font-weight:600; color:var(--text-secondary); margin-bottom:1rem; text-transform:uppercase; font-size:0.85rem; letter-spacing:0.05em;">Filtered Records</div>', unsafe_allow_html=True)
    
    # Render a compact dataframe just for selection
    display_cols = ["Record ID", "Target", "Course Label"]
    available_cols = [c for c in display_cols if c in filtered_df.columns]
    
    st.dataframe(
        filtered_df[available_cols],
        use_container_width=True,
        hide_index=True,
        height=600
    )

with col_detail:
    st.markdown('<div style="font-weight:600; color:var(--text-secondary); margin-bottom:1rem; text-transform:uppercase; font-size:0.85rem; letter-spacing:0.05em;">Record Detail View</div>', unsafe_allow_html=True)
    
    search_id = st.text_input("Enter Record ID to view details (e.g., REC-0005)", value="")
    
    if search_id:
        record = filtered_df[filtered_df["Record ID"] == search_id]
        if record.empty:
            st.warning("Record not found in the currently filtered view.")
        else:
            record_dict = record.iloc[0].to_dict()
            
            # Outcome badge
            target = record_dict.get('Target', 'Unknown')
            color = "var(--success)" if target == "Graduate" else "var(--risk)" if target == "Dropout" else "var(--warning)"
            
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); padding-bottom:1rem; margin-bottom:2rem;">
                <div style="font-size:2rem; font-weight:800; color:var(--text-primary); font-family:'JetBrains Mono', monospace;">{search_id}</div>
                <div style="background:{color}; color:#0A1118; font-weight:700; padding:0.25rem 1rem; border-radius:2rem; font-size:0.9rem;">{target}</div>
            </div>
            """, unsafe_allow_html=True)
            
            def render_section(title, fields):
                html = f'<div style="margin-bottom:2rem;"><div style="font-weight:700; color:var(--accent-primary); letter-spacing:0.1em; font-size:0.85rem; text-transform:uppercase; margin-bottom:1rem;">{title}</div>'
                html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">'
                
                for f in fields:
                    val = record_dict.get(f, 'N/A')
                    if isinstance(val, float):
                        val = f"{val:.2f}"
                    html += f'''
                    <div style="background:var(--surface); padding:1rem; border-radius:var(--radius-sm); border:1px solid var(--border);">
                        <div style="color:var(--text-secondary); font-size:0.8rem; margin-bottom:0.25rem;">{f}</div>
                        <div style="color:var(--text-primary); font-weight:500;">{val}</div>
                    </div>
                    '''
                html += '</div></div>'
                st.markdown(html, unsafe_allow_html=True)
                
            render_section("PROFILE", ["Course Label", "Gender Label", "age_group", "Nationality", "Marital status"])
            render_section("ADMISSION", ["Application mode", "Previous qualification", "Admission Grade Band"])
            render_section("FINANCIAL", ["Scholarship Status", "Tuition Status", "Debtor Status"])
            render_section("ACADEMIC", ["Curricular units 1st sem (grade)", "Curricular units 2nd sem (grade)", "f_b_total_units_approved", "f_b_academic_progress"])
            render_section("RISK (EDUPULSE METRICS)", ["current_academic_risk"])
    else:
        st.markdown("""
        <div style="padding:4rem; text-align:center; background:var(--surface); border:1px dashed var(--border); border-radius:var(--radius-lg);">
            <div style="font-size:2rem; margin-bottom:1rem; opacity:0.5;">👈</div>
            <div style="color:var(--text-primary); font-weight:600; font-size:1.1rem; margin-bottom:0.5rem;">Select a Record</div>
            <div style="color:var(--text-secondary);">Enter a Record ID from the list on the left to view detailed intelligence.</div>
        </div>
        """, unsafe_allow_html=True)
