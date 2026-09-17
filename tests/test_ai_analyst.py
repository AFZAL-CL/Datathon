import pytest
import pandas as pd
from dashboard.src.ai.schemas import AIQuerySpec
from dashboard.src.ai.intent_parser import IntentParser
from dashboard.src.ai.query_engine import QueryEngine
from dashboard.src.ai.chart_selector import ChartSelector
from dashboard.src.ai.insight_generator import InsightGenerator

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Course Label": ["A", "A", "B", "B", "C"],
        "Target": ["Dropout", "Graduate", "Dropout", "Dropout", "Enrolled"],
        "Gender Label": ["Male", "Female", "Male", "Male", "Female"],
        "Scholarship Status": ["No scholarship", "Scholarship holder", "No scholarship", "No scholarship", "Scholarship holder"],
        "Tuition Status": ["Not up to date", "Up to date", "Not up to date", "Not up to date", "Up to date"],
        "f_b_academic_progress": [0.1, 0.9, 0.2, 0.1, 0.5],
        "current_academic_risk": ["High", "Low", "High", "High", "Medium"]
    })

@pytest.fixture
def sample_early_df():
    return pd.DataFrame({
        "Course Label": ["A", "A", "B", "B", "C"],
        "early_admission_risk": ["High", "Low", "Medium", "High", "Low"]
    })

def test_intent_parser_deterministic():
    parser = IntentParser()
    parser.use_llm = False
    
    spec = parser.parse("Which courses have the highest dropout rate?")
    assert spec.metric == "dropout_rate"
    assert spec.dimension == "course"
    
    spec2 = parser.parse("Show graduation rate by course")
    assert spec2.metric == "graduate_rate"
    assert spec2.dimension == "course"
    
    spec3 = parser.parse("Show dropout by gender")
    assert spec3.metric == "dropout_count"
    assert spec3.dimension == "gender"
    
    spec4 = parser.parse("Compare scholarship students outcome")
    assert spec4.dimension == "scholarship"
    
    spec5 = parser.parse("Show current academic risk by course")
    assert spec5.metric == "current_risk_rate"
    assert spec5.dimension == "course"

def test_unsupported_infrastructure_question():
    parser = IntentParser()
    with pytest.raises(ValueError, match="UNSUPPORTED_INFRASTRUCTURE"):
        parser.parse("Does electricity infrastructure affect dropout?")

def test_query_engine_dropout_rate(sample_df, sample_early_df):
    engine = QueryEngine(sample_df, sample_early_df)
    spec = AIQuerySpec(metric="dropout_rate", dimension="course")
    result = engine.execute(spec)
    
    assert not result.empty
    assert "Value" in result.columns
    # Course B has 2 dropouts out of 2 = 100%
    assert result[result["Course Label"] == "B"]["Value"].values[0] == 100.0
    
def test_query_engine_current_risk(sample_df, sample_early_df):
    engine = QueryEngine(sample_df, sample_early_df)
    spec = AIQuerySpec(metric="current_risk_rate", dimension="course")
    result = engine.execute(spec)
    
    assert not result.empty
    assert "Value" in result.columns
    assert result[result["Course Label"] == "B"]["Value"].values[0] == 100.0

def test_insight_generator(sample_df, sample_early_df):
    engine = QueryEngine(sample_df, sample_early_df)
    spec = AIQuerySpec(metric="dropout_rate", dimension="course")
    result = engine.execute(spec)
    
    gen = InsightGenerator()
    insight = gen.generate(result, spec)
    assert "Dropout Rate varies across Course" in insight
    assert "100.0%" in insight # Because max is 100% in our mock data
