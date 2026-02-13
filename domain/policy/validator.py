class PolicyValidator:
    """Validates orchestration and adaptive behavior policies."""
    
    def __init__(self):
        self.required_keys = ["latency_threshold_ms", "cost_limit", "min_accuracy"]

    def validate(self, policy):
        """
        Validates a policy dictionary.
        
        Args:
            policy (dict): The policy to validate.
            
        Returns:
            bool: True if valid, raises ValueError otherwise.
        """
        if not isinstance(policy, dict):
            raise ValueError("Policy must be a dictionary")
            
        for key in self.required_keys:
            if key not in policy:
                raise ValueError(f"Missing required policy key: {key}")
                
            if not isinstance(policy[key], (int, float)):
                raise ValueError(f"Policy key {key} must be a number")
                
        return True
