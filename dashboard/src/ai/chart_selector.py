import plotly.express as px
import pandas as pd
from dashboard.src.ai.schemas import AIQuerySpec

class ChartSelector:
    def __init__(self):
        self.dim_map = {
            "course": "Course Label",
            "gender": "Gender Label",
            "age_group": "age_group",
            "scholarship": "Scholarship Status",
            "tuition_status": "Tuition Status",
            "debtor_status": "Debtor Status",
            "previous_qualification": "Previous qualification",
            "application_mode": "Application mode",
            "admission_grade_band": "Admission Grade Band",
            "target": "Target",
            "early_admission_risk": "early_admission_risk",
            "current_academic_risk": "current_academic_risk"
        }

    def generate_chart(self, df: pd.DataFrame, spec: AIQuerySpec):
        if df.empty:
            return None
            
        dim_col = self.dim_map.get(spec.dimension)
        
        # Format the title
        metric_title = spec.metric.replace("_", " ").title()
        dim_title = spec.dimension.replace("_", " ").title() if spec.dimension else ""
        title = f"{metric_title} by {dim_title}" if dim_title else metric_title

        if spec.chart_type == "box" and dim_col and len(df.columns) > 1:
            y_col = [c for c in df.columns if c != dim_col][0]
            fig = px.box(df, x=dim_col, y=y_col, title=title)
            return fig
            
        elif spec.chart_type == "scatter" and dim_col and len(df.columns) >= 2:
            cols = [c for c in df.columns if c != dim_col]
            if len(cols) >= 2:
                fig = px.scatter(df, x=cols[0], y=cols[1], color=dim_col, title=title, opacity=0.6)
                return fig
                
        # Default to bar for most aggregate results
        if "Value" in df.columns and dim_col in df.columns:
            fig = px.bar(df, x=dim_col, y="Value", title=title, color="Value", color_continuous_scale="Viridis")
            fig.update_layout(xaxis_tickangle=-45)
            return fig
            
        # Fallback if no specific logic matched
        if dim_col in df.columns and len(df.columns) == 2:
            val_col = [c for c in df.columns if c != dim_col][0]
            fig = px.bar(df, x=dim_col, y=val_col, title=title)
            fig.update_layout(xaxis_tickangle=-45)
            return fig

        return None
