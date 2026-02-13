def calculate_system_utility(cost, latency, accuracy):
    """
    Calculates the aggregate utility of a processing decision.
    
    Args:
        cost (float): Operation cost.
        latency (float): Processing latency.
        accuracy (float): Model accuracy.
        
    Returns:
        float: Utility score (higher is better).
    """
    if cost == 0 or latency == 0:
        return 0.0
    return accuracy / (cost * latency)
