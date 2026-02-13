"""
Data models for orchestration policies.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class OrchestrationPolicy:
    latency_threshold_ms: int
    cost_limit: float
    min_accuracy: float
    mode_override: str = None
