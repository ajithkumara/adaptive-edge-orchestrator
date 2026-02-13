from orchestrator.mode_manager import ModeManager

def test_mode_manager_initial_state():
    manager = ModeManager()
    assert manager.mode == "EDGE"

def test_mode_manager_set_mode():
    manager = ModeManager()
    manager.set_mode("CLOUD")
    assert manager.mode == "CLOUD"
