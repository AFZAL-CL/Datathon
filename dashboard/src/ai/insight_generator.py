import pandas as pd
from dashboard.src.ai.schemas import AIQuerySpec

class InsightGenerator:
    def generate(self, df: pd.DataFrame, spec: AIQuerySpec) -> str:
        """Generates a grounded natural language insight based on the DataFrame result."""
        
        if df.empty:
            return "No records match the requested criteria."
            
        dim_title = spec.dimension.replace("_", " ").title() if spec.dimension else "dataset"
        metric_title = spec.metric.replace("_", " ").title()
        
        # Avoid causal claims!
        insight = f"The displayed comparison shows how the recorded {metric_title} varies across {dim_title}. "
        
        if "Value" in df.columns:
            max_val = df["Value"].max()
            min_val = df["Value"].min()
            
            if pd.notna(max_val) and pd.notna(min_val) and len(df) > 1:
                # Format appropriately depending on if it's a percentage or count
                if "rate" in spec.metric.lower():
                    max_str = f"{max_val:.1f}%"
                    min_str = f"{min_val:.1f}%"
                elif "avg" in spec.metric.lower():
                    max_str = f"{max_val:.2f}"
                    min_str = f"{min_val:.2f}"
                else:
                    max_str = f"{max_val:,.0f}"
                    min_str = f"{min_val:,.0f}"
                
                insight += f"The highest observed value in the filtered result is {max_str}, while the lowest is {min_str}."
        
        return insight
