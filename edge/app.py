import time
import os
from common.utils.logging import get_logger

# Initialize logger with environment-specific tags
node_id = os.getenv("EDGE_NODE_ID", "default-node")
factory_id = os.getenv("FACTORY_ID", "default-factory")
logger = get_logger(__name__, node_id=node_id, factory_id=factory_id)

def main():
    logger.info("Edge application starting...")
    while True:
        logger.info("Edge processing...")
        time.sleep(10)

if __name__ == "__main__":
    main()
