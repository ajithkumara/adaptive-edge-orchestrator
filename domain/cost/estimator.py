"""
Cost estimation logic for cloud and edge processing.
"""

def estimate_cloud_cost(data_size_kb, unit_price=0.005):
    """
    Estimates the cost of processing data in the cloud.
    """
    return data_size_kb * unit_price

def estimate_edge_savings(data_size_kb, cloud_unit_price=0.005, edge_overhead=0.001):
    """
    Estimates the savings achieved by processing on the edge instead of cloud.
    """
    return (data_size_kb * cloud_unit_price) - (data_size_kb * edge_overhead)
