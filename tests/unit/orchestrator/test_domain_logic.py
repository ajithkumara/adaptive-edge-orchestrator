from domain.anomaly.severity import classify_severity
from domain.cost.models import calculate_system_utility

def test_severity_classification():
    assert classify_severity(0.01, 0.5) == "LOW"
    assert classify_severity(0.06, 0.5) == "MEDIUM"
    assert classify_severity(0.01, 1.5) == "MEDIUM"
    assert classify_severity(0.12, 0.5) == "CRITICAL"
    assert classify_severity(0.01, 2.5) == "CRITICAL"

def test_cost_utility_calculation():
    # accuracy / (cost * latency)
    assert calculate_system_utility(10, 10, 100) == 1.0
    assert calculate_system_utility(0, 10, 100) == 0.0
    assert calculate_system_utility(10, 0, 100) == 0.0
