"""
State Store.
Responsibility: Provides a centralized, thread-safe (placeholder) storage for system state.
"""
class StateStore:
    def __init__(self):
        self.state = {}

    def get_state(self, key):
        return self.state.get(key)

    def set_state(self, key, value):
        self.state[key] = value
