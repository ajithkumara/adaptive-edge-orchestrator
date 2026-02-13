"""
Orchestrator Controller.
Responsibility: Coordinates components, manages system state, and delegates processing decisions.
"""
import time
from common.utils.logging import get_logger
from orchestrator.mode_manager import ModeManager
from orchestrator.decision_engine import DecisionEngine
from orchestrator.state_store import StateStore

logger = get_logger(__name__)

class OrchestratorController:
    def __init__(self):
        self.mode_manager = ModeManager()
        self.decision_engine = DecisionEngine()
        self.state_store = StateStore()

    def run(self):
        """Main orchestration loop."""
        logger.info("Orchestrator Controller starting...")
        while True:
            # In a real scenario, this would fetch metrics from the monitoring stack
            # or receive them via gRPC/REST.
            mock_metrics = {"latency": 150} 
            
            new_mode = self.decision_engine.decide(mock_metrics)
            if new_mode != self.mode_manager.mode:
                logger.info(f"Transitioning mode: {self.mode_manager.mode} -> {new_mode}")
                self.mode_manager.set_mode(new_mode)
            
            logger.info(f"Current System State: {self.mode_manager.mode}")
            time.sleep(10)
