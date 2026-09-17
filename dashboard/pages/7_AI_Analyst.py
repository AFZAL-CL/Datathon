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

# We need the early df for early admission risk queries
early_df = meta.get("early", df)

selections = render_global_filters(df)
filtered_df = apply_filters(df, selections)
filtered_early = apply_filters(early_df, selections)

page_header("EDUPULSE AI Analyst", "Ask questions about student retention, academic performance, and risk in natural language.")

st.markdown("""
<div class="notice">
<strong>Note:</strong> Analysis uses the currently selected dashboard filters. 
I can analyze student outcomes, academic performance, financial/support indicators, admission attributes, and the two EDUPULSE risk scenarios.
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Session state for queries
if "ai_queries" not in st.session_state:
    st.session_state.ai_queries = []

# Suggested questions
st.markdown("### Suggested questions:")
suggested = [
    "Which courses have the highest dropout rate?",
    "Show dropout by age group.",
    "Compare scholarship and non-scholarship students.",
    "Show current academic risk by course.",
    "Compare second-semester grades by outcome.",
    "Show graduation rate by course."
]

cols = st.columns(len(suggested[:3]))
for i, q in enumerate(suggested[:3]):
    if cols[i].button(q, key=f"sug_{i}"):
        st.session_state.current_query = q
        
cols2 = st.columns(len(suggested[3:]))
for i, q in enumerate(suggested[3:]):
    if cols2[i].button(q, key=f"sug_{i+3}"):
        st.session_state.current_query = q

query = st.text_input("What would you like to analyze?", key="current_query")

if query:
    if query not in st.session_state.ai_queries:
        st.session_state.ai_queries.append(query)
        
    with st.spinner("Analyzing..."):
        # Process the query
        parser = IntentParser()
        try:
            spec = parser.parse(query)
            
            engine = QueryEngine(filtered_df, filtered_early)
            result_df = engine.execute(spec)
            
            if result_df.empty:
                st.warning("No records match the requested criteria or the query is unsupported for the current filters.")
            else:
                st.markdown("### Analysis")
                
                chart_selector = ChartSelector()
                fig = chart_selector.generate_chart(result_df, spec)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(result_df, use_container_width=True)
                
                st.markdown("### Insight")
                insight_gen = InsightGenerator()
                insight = insight_gen.generate(result_df, spec)
                
                st.info(insight)
                
        except ValueError as e:
            if "UNSUPPORTED_INFRASTRUCTURE" in str(e):
                st.error("The current EDUPULSE dataset does not contain school electricity infrastructure, Mid-Day Meal, or other welfare variables, so this relationship cannot be analyzed from the available data.")
            else:
                st.error("I can analyze student outcomes, academic performance, financial/support indicators, admission attributes and the two EDUPULSE risk scenarios. I cannot answer this specific question.")
        except Exception as e:
            st.error(f"Failed to process query: {str(e)}")

if st.session_state.ai_queries:
    st.markdown("---")
    with st.expander("Recent analyses", expanded=False):
        for i, q in enumerate(reversed(st.session_state.ai_queries[-5:])):
            st.write(f"{i+1}. {q}")
