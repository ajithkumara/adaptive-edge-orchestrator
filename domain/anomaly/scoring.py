"""
Pure logic for anomaly scoring. No infrastructure dependencies.
"""

def calculate_anomaly_score(metrics):
    """
    Calculates a normalized anomaly score based on error rates and latency spikes.
    
    Args:
        metrics (dict): Performance metrics.
        
    Returns:
        float: Score between 0.0 and 1.0.
    """
    error_rate = metrics.get("error_rate", 0.0)
    latency_spike = metrics.get("latency_spike", 0.0)
    
    # Heuristic for anomaly scoring
    score = (error_rate * 0.7) + (min(latency_spike, 1.0) * 0.3)
    return min(score, 1.0)
