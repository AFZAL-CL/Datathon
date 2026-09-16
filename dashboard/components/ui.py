from __future__ import annotations

import streamlit as st


def inject_css() -> None:
    st.markdown("""
    <style>
    :root { --ink:#1e2b2f; --muted:#6c797d; --line:#dce4e1; --paper:#f5f7f4; --accent:#2f7d68; }
    .stApp { background: #f5f7f4; color: var(--ink); }
    [data-testid="stSidebar"] { background: #18272a; }
    [data-testid="stSidebar"] * { color: #eef4ef !important; }
    .brand { padding: 0.5rem 0 1.2rem; border-bottom: 1px solid rgba(255,255,255,.15); margin-bottom: 1.2rem; }
    .brand-name { font-size: 1.35rem; letter-spacing: .14em; font-weight: 800; color: #cfe3d8; }
    .brand-sub { font-size: .72rem; color: #a7bbb3; margin-top: .3rem; }
    .eyebrow { color:#2f7d68; font-size:.75rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; margin-bottom:.25rem; }
    h1 { font-size: 2.15rem !important; letter-spacing: -.02em; margin-bottom: .2rem !important; }
    h2, h3 { letter-spacing: -.01em; }
    .subtitle { color: var(--muted); margin-bottom: 1.5rem; }
    .kpi { background:#fff; border:1px solid var(--line); border-radius:12px; padding:1rem 1.1rem; min-height:106px; box-shadow:0 2px 8px rgba(25,45,40,.04); }
    .kpi-label { font-size:.7rem; color:var(--muted); letter-spacing:.1em; text-transform:uppercase; font-weight:700; }
    .kpi-value { font-size:1.85rem; font-weight:800; color:var(--ink); margin-top:.4rem; }
    .kpi-note { color:var(--muted); font-size:.75rem; margin-top:.15rem; }
    .section { margin-top:1.25rem; padding-top:.35rem; }
    .insight { background:#e8f0eb; border-left:3px solid #2f7d68; padding:.7rem .85rem; margin:.35rem 0; border-radius:0 8px 8px 0; color:#2b4840; }
    .notice { background:#fff; border:1px solid var(--line); border-radius:10px; padding:1rem; color:var(--muted); }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str, eyebrow: str = "EDUPULSE") -> None:
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)


def kpi_row(items: list[tuple[str, str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, note) in zip(cols, items):
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)


def empty_state(message: str = "No records match the current filters.") -> None:
    st.markdown(f'<div class="notice">{message}</div>', unsafe_allow_html=True)


def section_title(title: str, caption: str = "") -> None:
    st.markdown(f'<div class="section"><h3>{title}</h3><div class="subtitle">{caption}</div></div>', unsafe_allow_html=True)
