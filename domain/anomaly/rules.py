"""
Anomaly detection rules. Pure logic.
"""

def extract_anomaly_features(event_stream):
    """Placeholder for logic that extracts features from a raw event stream."""
    return {"error_rate": 0.0, "latency_spike": 0.0}

def is_system_unstable(metrics, threshold=0.8):
    """
    Evaluates system stability based on a list of critical metrics.
    """
    critical_count = 0
    for metric_name, value in metrics.items():
        if value > threshold:
            critical_count += 1
            
    return critical_count >= 2
