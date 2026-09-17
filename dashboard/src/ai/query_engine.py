import pandas as pd
from dashboard.src.ai.schemas import AIQuerySpec

class QueryEngine:
    def __init__(self, df: pd.DataFrame, early_df: pd.DataFrame):
        self.df = df
        self.early_df = early_df
        
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

    def execute(self, spec: AIQuerySpec) -> pd.DataFrame:
        # Determine which dataframe to use
        # If it asks for early_risk, we use early_df (which is merged or available)
        # For simplicity, let's assume early_admission_risk is available in early_df
        use_df = self.early_df if "early" in spec.metric or spec.dimension == "early_admission_risk" else self.df
        
        # Apply filters (if any)
        for dim, values in spec.filters.items():
            col = self.dim_map.get(dim)
            if col and col in use_df.columns:
                use_df = use_df[use_df[col].isin(values)]
                
        if use_df.empty:
            return pd.DataFrame()

        groupby_col = self.dim_map.get(spec.dimension) if spec.dimension else None
        
        if groupby_col and groupby_col not in use_df.columns:
            # Fallback if column missing
            return pd.DataFrame()

        # Handle Rates
        if spec.metric.endswith("_rate"):
            target_val = spec.metric.split("_")[0].capitalize() # e.g. "Dropout", "Graduate", "Enrolled"
            if "early_risk" in spec.metric:
                if groupby_col:
                    counts = use_df.groupby([groupby_col, "early_admission_risk"]).size().unstack(fill_value=0)
                    counts["Total"] = counts.sum(axis=1)
                    if "High" in counts.columns:
                        counts["Value"] = (counts["High"] / counts["Total"]) * 100
                    else:
                        counts["Value"] = 0
                    return counts[["Value"]].reset_index()
                else:
                    return pd.DataFrame([{"Metric": "Early Risk Rate", "Value": (len(use_df[use_df["early_admission_risk"] == "High"]) / len(use_df) * 100) if len(use_df) > 0 else 0}])
            
            elif "current_risk" in spec.metric:
                if groupby_col:
                    counts = use_df.groupby([groupby_col, "current_academic_risk"]).size().unstack(fill_value=0)
                    counts["Total"] = counts.sum(axis=1)
                    if "High" in counts.columns:
                        counts["Value"] = (counts["High"] / counts["Total"]) * 100
                    else:
                        counts["Value"] = 0
                    return counts[["Value"]].reset_index()
                else:
                    return pd.DataFrame([{"Metric": "Current Risk Rate", "Value": (len(use_df[use_df["current_academic_risk"] == "High"]) / len(use_df) * 100) if len(use_df) > 0 else 0}])
                    
            else: # dropout_rate, graduate_rate, enrolled_rate
                if groupby_col:
                    counts = use_df.groupby([groupby_col, "Target"]).size().unstack(fill_value=0)
                    counts["Total"] = counts.sum(axis=1)
                    if target_val in counts.columns:
                        counts["Value"] = (counts[target_val] / counts["Total"]) * 100
                    else:
                        counts["Value"] = 0
                    return counts[["Value"]].reset_index()
                else:
                    return pd.DataFrame([{"Metric": f"{target_val} Rate", "Value": (len(use_df[use_df["Target"] == target_val]) / len(use_df) * 100) if len(use_df) > 0 else 0}])

        # Handle Counts
        elif spec.metric.endswith("_count"):
            if spec.metric == "student_count":
                if groupby_col:
                    return use_df.groupby(groupby_col).size().reset_index(name="Value")
                else:
                    return pd.DataFrame([{"Metric": "Total Students", "Value": len(use_df)}])
            else:
                target_val = spec.metric.split("_")[0].capitalize()
                if groupby_col:
                    return use_df[use_df["Target"] == target_val].groupby(groupby_col).size().reset_index(name="Value")
                else:
                    return pd.DataFrame([{"Metric": f"{target_val} Students", "Value": len(use_df[use_df["Target"] == target_val])}])

        # Handle Averages / Numerical metrics
        elif spec.metric.startswith("avg_") or spec.metric == "academic_progress":
            col_map = {
                "avg_first_semester_grade": "Curricular units 1st sem (grade)",
                "avg_second_semester_grade": "Curricular units 2nd sem (grade)",
                "avg_approved_units": "f_b_total_units_approved",
                "avg_enrolled_units": "f_b_total_units_enrolled",
                "academic_progress": "f_b_academic_progress"
            }
            target_col = col_map.get(spec.metric)
            # fallback for academic_progress if not using f_b_ prefix
            if spec.metric == "academic_progress" and target_col not in use_df.columns:
                target_col = "academic_progress"
                
            if target_col and target_col in use_df.columns:
                if groupby_col:
                    # For box plots we want the raw data to be passed to Plotly
                    # So we return the filtered dataframe directly with just those columns
                    if spec.chart_type in ["box", "scatter"]:
                        cols = [groupby_col, target_col]
                        if spec.chart_type == "scatter":
                            cols.append("Curricular units 1st sem (grade)") # Just a hack to ensure scatter has 2 axes
                        available_cols = [c for c in cols if c in use_df.columns]
                        return use_df[available_cols].dropna()
                    else:
                        return use_df.groupby(groupby_col)[target_col].mean().reset_index(name="Value")
                else:
                    return pd.DataFrame([{"Metric": spec.metric, "Value": use_df[target_col].mean()}])
                    
        return pd.DataFrame()
