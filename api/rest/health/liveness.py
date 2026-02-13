class LivenessProbe:
    """Check to determine if the service process is alive."""
    def __init__(self):
        pass

    def check(self):
        """Simple check for process health."""
        return {"status": "alive"}
