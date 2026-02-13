def should_transition_to_cloud(metrics, thresholds):
    """
    State transition logic based on performance thresholds.
    
    Args:
        metrics (dict): Current system metrics (e.g., latency).
        thresholds (dict): Threshold values for transition.
        
    Returns:
        bool: True if transition to CLOUD is recommended.
    """
    latency = metrics.get("latency", 0)
    latency_threshold = thresholds.get("latency_threshold", 200)
    
    return latency > latency_threshold
