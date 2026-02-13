import pytest
from domain.policy.validator import PolicyValidator

def test_policy_validation_success():
    validator = PolicyValidator()
    policy = {
        "latency_threshold_ms": 100,
        "cost_limit": 50.5,
        "min_accuracy": 0.95
    }
    assert validator.validate(policy) is True

def test_policy_validation_missing_key():
    validator = PolicyValidator()
    policy = {
        "latency_threshold_ms": 100,
        "cost_limit": 50.5
        # min_accuracy missing
    }
    with pytest.raises(ValueError, match="Missing required policy key: min_accuracy"):
        validator.validate(policy)

def test_policy_validation_wrong_type():
    validator = PolicyValidator()
    policy = {
        "latency_threshold_ms": "fast", # should be number
        "cost_limit": 50.5,
        "min_accuracy": 0.95
    }
    with pytest.raises(ValueError, match="Policy key latency_threshold_ms must be a number"):
        validator.validate(policy)
