"""
Decision Engine.
Responsibility: Evaluates metrics against domain policies to determine processing modes.
"""
from domain.policy.transitions import should_transition_to_cloud

class DecisionEngine:
    def __init__(self, latency_threshold=200):
        self.thresholds = {"latency_threshold": latency_threshold}

    def decide(self, metrics):
        """
        Decides processing mode by delegating to domain transition rules.
        """
        if should_transition_to_cloud(metrics, self.thresholds):
            return "CLOUD"
        return "EDGE"
