from dataclasses import dataclass, field
from typing import Optional, Dict, List

@dataclass
class AIQuerySpec:
    metric: str
    dimension: Optional[str] = None
    filters: Dict[str, List[str]] = field(default_factory=dict)
    chart_type: str = "bar"
