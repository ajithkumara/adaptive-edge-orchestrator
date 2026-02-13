"""
Orchestrator Entry Point.
Responsibility: Bootstraps the orchestrator service and initializes the controller.
"""
from orchestrator.controller import OrchestratorController

def main():
    controller = OrchestratorController()
    controller.run()

if __name__ == "__main__":
    main()
