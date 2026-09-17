import os
import re
import json
from dashboard.src.ai.schemas import AIQuerySpec

# Optional google-genai dependency
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class IntentParser:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.use_llm = HAS_GENAI and bool(self.api_key)
        
        if self.use_llm:
            self.client = genai.Client(api_key=self.api_key)

    def parse(self, query: str) -> AIQuerySpec:
        """Parses the natural language query into a structured AIQuerySpec."""
        query_lower = query.lower()
        
        # Security/Scope check
        if any(word in query_lower for word in ["mid-day meal", "electricity", "infrastructure", "transorg", "welfare"]):
            raise ValueError("UNSUPPORTED_INFRASTRUCTURE")
            
        if self.use_llm:
            try:
                return self._parse_llm(query)
            except Exception as e:
                print(f"LLM parsing failed: {e}. Falling back to deterministic parser.")
                return self._parse_deterministic(query)
        else:
            return self._parse_deterministic(query)

    def _parse_llm(self, query: str) -> AIQuerySpec:
        """Uses Gemini to extract the structured query intent."""
        prompt = f"""
        You are an AI Analyst for the EDUPULSE Student Retention Dashboard.
        Your job is to parse the user's natural language question into a strict JSON query specification.
        
        ALLOWED METRICS: student_count, dropout_count, graduate_count, enrolled_count, dropout_rate, graduate_rate, enrolled_rate, avg_first_semester_grade, avg_second_semester_grade, avg_approved_units, avg_enrolled_units, academic_progress, early_risk_count, early_risk_rate, current_risk_count, current_risk_rate
        
        ALLOWED DIMENSIONS: course, gender, age_group, scholarship, tuition_status, debtor_status, previous_qualification, application_mode, admission_grade_band, target, early_admission_risk, current_academic_risk
        
        CHART TYPES: bar, pie, scatter, box, heatmap
        
        User Question: "{query}"
        
        Extract the metric, dimension, filters (if any), and chart_type.
        Return ONLY valid JSON matching this schema:
        {{
            "metric": "string",
            "dimension": "string or null",
            "filters": {{"dimension_name": ["value1"]}},
            "chart_type": "string"
        }}
        """
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        data = json.loads(response.text)
        return AIQuerySpec(**data)
        
    def _parse_deterministic(self, query: str) -> AIQuerySpec:
        """Deterministic regex-based fallback parser for common questions."""
        q = query.lower()
        
        metric = "student_count"
        dimension = None
        chart_type = "bar"
        
        # Metric extraction
        if "dropout rate" in q:
            metric = "dropout_rate"
        elif "graduation rate" in q or "graduate rate" in q:
            metric = "graduate_rate"
        elif "enrolled rate" in q:
            metric = "enrolled_rate"
        elif "dropout" in q and ("count" in q or "by" in q):
            metric = "dropout_count"
        elif "early admission risk" in q:
            metric = "early_risk_rate"
        elif "current academic risk" in q:
            metric = "current_risk_rate"
        elif "second-semester grade" in q or "second semester grade" in q:
            metric = "avg_second_semester_grade"
            chart_type = "box"
        elif "academic progress" in q:
            metric = "academic_progress"
            chart_type = "box"
            
        # Dimension extraction
        if "by course" in q or "courses" in q:
            dimension = "course"
        elif "by age group" in q or "across age groups" in q:
            dimension = "age_group"
        elif "by gender" in q or "male" in q or "female" in q:
            dimension = "gender"
        elif "scholarship" in q:
            dimension = "scholarship"
        elif "tuition" in q:
            dimension = "tuition_status"
        elif "debtor" in q:
            dimension = "debtor_status"
        elif "application mode" in q:
            dimension = "application_mode"
        elif "previous qualification" in q:
            dimension = "previous_qualification"
        elif "admission grade band" in q:
            dimension = "admission_grade_band"
        elif "by outcome" in q or "across outcomes" in q or "compare dropout and graduation" in q:
            dimension = "target"
            
        # If it's a comparison of semesters
        if "first and second semester" in q:
            metric = "avg_second_semester_grade"
            dimension = "target"
            chart_type = "scatter"
            
        if not dimension and metric == "student_count":
            # Just asking for generic counts without grouping
            pass
            
        return AIQuerySpec(
            metric=metric,
            dimension=dimension,
            filters={},
            chart_type=chart_type
        )
