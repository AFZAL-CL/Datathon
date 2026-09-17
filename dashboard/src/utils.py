import streamlit as st

def inject_css() -> None:
    """Injects the custom dashboard CSS."""
    with open("dashboard/assets/style.css", "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def page_header(title: str, subtitle: str, eyebrow: str = "EDUPULSE") -> None:
    """Renders a standard page header."""
    st.markdown(f'<div class="eyebrow" style="color:var(--accent); font-size:0.75rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.25rem;">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<h1>{title}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def kpi_row(items: list[tuple[str, str, str]]) -> None:
    """Renders a row of KPI cards."""
    cols = st.columns(len(items))
    for col, (label, value, note) in zip(cols, items):
        with col:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-note" style="color:var(--text-muted); font-size:0.75rem; margin-top:0.25rem;">{note}</div>
            </div>
            ''', unsafe_allow_html=True)

def empty_state(message: str = "No records match the current filters.") -> None:
    """Renders an empty state notice."""
    st.markdown(f'<div class="empty-state">{message}</div>', unsafe_allow_html=True)

def section_title(title: str, caption: str = "") -> None:
    """Renders a section title."""
    st.markdown(f'<div style="margin-top:2rem;"><h3>{title}</h3><div style="color:var(--text-muted); font-size:0.9rem; margin-bottom:1rem;">{caption}</div></div>', unsafe_allow_html=True)
