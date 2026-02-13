"""
Mode Manager.
Responsibility: Manages the current operational mode (EDGE/CLOUD) of the system.
"""
class ModeManager:
    def __init__(self):
        self.mode = "EDGE"

    def set_mode(self, mode):
        self.mode = mode
