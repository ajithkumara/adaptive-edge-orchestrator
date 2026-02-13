import time
from common.utils.logging import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Cloud application starting...")
    while True:
        logger.info("Cloud processing...")
        time.sleep(10)

if __name__ == "__main__":
    main()
