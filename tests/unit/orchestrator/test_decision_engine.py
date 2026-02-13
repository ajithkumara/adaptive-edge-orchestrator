import pytest
from orchestrator.decision_engine import DecisionEngine

def test_decision_engine_default_edge():
    engine = DecisionEngine()
    metrics = {"latency": 150}
    assert engine.decide(metrics) == "EDGE"

def test_decision_engine_transition_to_cloud():
    engine = DecisionEngine(latency_threshold=200)
    metrics = {"latency": 250}
    assert engine.decide(metrics) == "CLOUD"

def test_decision_engine_custom_threshold():
    engine = DecisionEngine(latency_threshold=500)
    metrics = {"latency": 400}
    assert engine.decide(metrics) == "EDGE"
    
    metrics = {"latency": 600}
    assert engine.decide(metrics) == "CLOUD"
