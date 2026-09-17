import streamlit as st

def inject_css() -> None:
    """Injects the custom dashboard CSS."""
    with open("dashboard/assets/style.css", "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def page_header(title: str, subtitle: str, eyebrow: str = "EDUPULSE / INTELLIGENCE") -> None:
    """Renders a premium editorial page header."""
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def kpi_row(items: list[tuple[str, str, str]]) -> None:
    """Renders a row of staggered, animated KPI modules."""
    html = '<div class="kpi-container">'
    for label, value, note in items:
        html += f'''
        <div class="kpi-module">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        '''
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def empty_state(message: str = "No records match the selected filters.") -> None:
    """Renders an elegant empty state."""
    st.markdown(f'''
    <div style="padding:4rem; text-align:center; background:var(--surface); border:1px dashed var(--border); border-radius:var(--radius-lg); margin-top:2rem;">
        <div style="font-size:2rem; margin-bottom:1rem; opacity:0.5;">📭</div>
        <div style="color:var(--text-primary); font-weight:600; font-size:1.1rem; margin-bottom:0.5rem;">No Data in Current View</div>
        <div style="color:var(--text-secondary);">{message}</div>
    </div>
    ''', unsafe_allow_html=True)

def section_title(title: str, caption: str = "") -> None:
    """Renders an editorial section title."""
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="section-caption">{caption}</div>', unsafe_allow_html=True)
        
def insight_box(text: str, kind: str = "primary") -> None:
    """Renders an insight box. kind: primary, warning, risk, success"""
    st.markdown(f'<div class="insight-box {kind}">{text}</div>', unsafe_allow_html=True)
