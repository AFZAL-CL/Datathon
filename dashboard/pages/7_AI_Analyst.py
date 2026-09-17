import streamlit as st
import time
from dashboard.src.data_loader import load_data
from dashboard.src.filters import render_global_filters, apply_filters
from dashboard.src.utils import inject_css, page_header, empty_state
from dashboard.src.ai.intent_parser import IntentParser
from dashboard.src.ai.query_engine import QueryEngine
from dashboard.src.ai.chart_selector import ChartSelector
from dashboard.src.ai.insight_generator import InsightGenerator

st.set_page_config(page_title="EDUPULSE | AI Analyst", page_icon="🤖", layout="wide")
inject_css()

df, meta = load_data()
if df.empty:
    st.error("Data could not be loaded.")
    st.stop()

early_df = meta.get("early", df)

selections = render_global_filters(df)
filtered_df = apply_filters(df, selections)
filtered_early = apply_filters(early_df, selections)

page_header(
    title="Ask the dataset.",
    subtitle="Natural-language interface to the EDUPULSE intelligence pipeline.",
    eyebrow="EDUPULSE AI ANALYST"
)

st.markdown("""
<div style="background:var(--surface); border:1px solid var(--border); padding:1rem 1.5rem; border-radius:var(--radius-md); font-size:0.9rem; color:var(--text-secondary); margin-bottom:2rem; display:flex; align-items:center; gap:1rem; animation: slideUpFade 600ms var(--transition-med) both;">
    <span style="color:var(--accent-primary);">⚡</span>
    <span>Analysis is bounded to the currently selected global filters and respects dataset boundaries.</span>
</div>
""", unsafe_allow_html=True)

if "ai_queries" not in st.session_state:
    st.session_state.ai_queries = []

st.markdown('<div style="font-weight:700; color:var(--text-primary); margin-bottom:1rem; font-size:1.1rem;">Suggested Queries</div>', unsafe_allow_html=True)

suggested = [
    "Which courses have the highest dropout rate?",
    "Show current academic risk by course.",
    "Compare scholarship and non-scholarship outcomes.",
    "How does academic progress vary by outcome?"
]

# Render elegant query chips
cols = st.columns(4)
for i, q in enumerate(suggested):
    if cols[i].button(q, key=f"sug_{i}", use_container_width=True):
        st.session_state.current_query = q

st.markdown("<br/>", unsafe_allow_html=True)
query = st.text_input("What would you like to understand?", key="current_query", placeholder="e.g., Show dropout by age group...")

if query:
    if query not in st.session_state.ai_queries:
        st.session_state.ai_queries.append(query)
        
    with st.spinner("Analyzing data..."):
        parser = IntentParser()
        try:
            spec = parser.parse(query)
            engine = QueryEngine(filtered_df, filtered_early)
            result_df = engine.execute(spec)
            
            if result_df.empty:
                st.markdown("""
                <div style="padding:2rem; background:var(--surface); border:1px dashed var(--risk); border-radius:var(--radius-md); margin-top:2rem; text-align:center;">
                    <div style="color:var(--risk); margin-bottom:0.5rem; font-weight:600;">No Results</div>
                    <div style="color:var(--text-secondary); font-size:0.9rem;">The query returned no data for the current filters.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="margin-top:3rem; margin-bottom:1.5rem; font-weight:700; color:var(--accent-secondary); letter-spacing:0.1em; text-transform:uppercase; font-size:0.85rem;">Result Workspace</div>', unsafe_allow_html=True)
                
                chart_selector = ChartSelector()
                fig = chart_selector.generate_chart(result_df, spec)
                
                # Render inside an editorial container
                st.markdown('<div style="background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-lg); padding:2rem; animation: slideUpFade 800ms var(--transition-med) both;">', unsafe_allow_html=True)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(result_df, use_container_width=True)
                
                insight_gen = InsightGenerator()
                insight = insight_gen.generate(result_df, spec)
                
                st.markdown(f"""
                <div style="border-top:1px solid var(--border); margin-top:2rem; padding-top:1.5rem;">
                    <div style="font-size:0.75rem; color:var(--text-secondary); text-transform:uppercase; font-weight:700; letter-spacing:0.05em; margin-bottom:0.5rem;">Synthesized Insight</div>
                    <div style="font-size:1.1rem; color:var(--text-primary); line-height:1.6;">{insight}</div>
                </div>
                </div>
                """, unsafe_allow_html=True)
                
        except ValueError as e:
            if "UNSUPPORTED_INFRASTRUCTURE" in str(e):
                st.error("The current EDUPULSE dataset does not contain school electricity infrastructure, Mid-Day Meal, or other welfare variables, so this relationship cannot be analyzed from the available data.")
            else:
                st.error("I can analyze student outcomes, academic performance, financial/support indicators, admission attributes and the two EDUPULSE risk scenarios. I cannot answer this specific question.")
        except Exception as e:
            st.error(f"Failed to process query: {str(e)}")

if st.session_state.ai_queries:
    st.markdown("<hr style='margin-top:4rem;'>", unsafe_allow_html=True)
    with st.expander("Session History", expanded=False):
        for i, q in enumerate(reversed(st.session_state.ai_queries[-5:])):
            st.markdown(f'<div style="color:var(--text-secondary); margin-bottom:0.5rem; font-size:0.9rem;">{i+1}. {q}</div>', unsafe_allow_html=True)
