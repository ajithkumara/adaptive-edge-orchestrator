def classify_severity(error_rate, latency_spike):
    """
    Classifies the severity of an anomaly.
    
    Args:
        error_rate (float): Current error rate (0.0 to 1.0).
        latency_spike (float): Percentage spike in latency.
        
    Returns:
        str: "LOW", "MEDIUM", "CRITICAL"
    """
    if error_rate > 0.1 or latency_spike > 2.0:
        return "CRITICAL"
    if error_rate > 0.05 or latency_spike > 1.0:
        return "MEDIUM"
    return "LOW"
