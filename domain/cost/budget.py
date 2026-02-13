"""
Budgeting and constraint logic.
"""

def is_within_budget(current_spend, limit):
    """
    Checks if the current spend is within the defined limit.
    """
    return current_spend <= limit

def calculate_remaining_budget(total_budget, spent):
    """
    Returns the remaining budget.
    """
    return max(0, total_budget - spent)
