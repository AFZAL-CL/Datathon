import plotly.express as px
import pandas as pd
from dashboard.src.ai.schemas import AIQuerySpec

def apply_premium_theme(fig):
    """Applies the premium editorial dark theme to a Plotly figure."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="#F8FAFC"),
        title_font=dict(size=18, color="#F8FAFC"),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.15)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.15)"),
        margin=dict(t=40, b=40, l=40, r=40),
        colorway=["#0D9488", "#8B5CF6", "#FBBF24", "#FB7185", "#34D399"]
    )
    return fig

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

        fig = None

        if spec.chart_type == "box" and dim_col and len(df.columns) > 1:
            y_col = [c for c in df.columns if c != dim_col][0]
            fig = px.box(df, x=dim_col, y=y_col, title=title)
            
        elif spec.chart_type == "scatter" and dim_col and len(df.columns) >= 2:
            cols = [c for c in df.columns if c != dim_col]
            if len(cols) >= 2:
                fig = px.scatter(df, x=cols[0], y=cols[1], color=dim_col, title=title, opacity=0.6)
                
        # Default to bar for most aggregate results
        elif "Value" in df.columns and dim_col in df.columns:
            fig = px.bar(df, x=dim_col, y="Value", title=title, color="Value", color_continuous_scale="Teal")
            fig.update_layout(xaxis_tickangle=-45)
            
        # Fallback if no specific logic matched
        elif dim_col in df.columns and len(df.columns) == 2:
            val_col = [c for c in df.columns if c != dim_col][0]
            fig = px.bar(df, x=dim_col, y=val_col, title=title)
            fig.update_layout(xaxis_tickangle=-45)

        if fig:
            return apply_premium_theme(fig)
        return None
