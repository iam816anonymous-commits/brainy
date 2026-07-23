from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class NodeTrace(BaseModel):
    id: str
    type: str
    title: str
    raw_similarity: float
    intent_boost: float
    importance_boost: float
    recency_boost: float
    project_boost: float
    file_boost: float
    graph_boost: float
    historical_success_boost: float
    noise_penalty: float
    final_score: float
    is_included: bool
    compression_ratio: float = 1.0 # ratio of final length to original length

class ContextTrace(BaseModel):
    query: str
    intent: str
    total_candidates_processed: int
    included_count: int
    execution_time_ms: float
    traces: List[NodeTrace] = Field(default_factory=list)

class ObservabilityTraceRegistry:
    """
    Subsystem inside the Context Layer that records, stores, and exposes
    explainability execution audits of how ContextPackages are compiled.
    """
    _traces: List[ContextTrace] = []

    @classmethod
    def record_trace(cls, trace: ContextTrace) -> None:
        cls._traces.append(trace)
        # Limit global registry size
        if len(cls._traces) > 100:
            cls._traces.pop(0)

    @classmethod
    def get_latest_trace(cls) -> Optional[ContextTrace]:
        if cls._traces:
            return cls._traces[-1]
        return None

    @classmethod
    def list_traces(cls) -> List[ContextTrace]:
        return cls._traces

    @classmethod
    def clear(cls) -> None:
        cls._traces.clear()
