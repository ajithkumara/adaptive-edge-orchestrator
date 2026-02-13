import logging
import json
import time
from uuid import uuid4

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None),
            "node_id": getattr(record, "node_id", None),
            "factory_id": getattr(record, "factory_id", None)
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

def get_logger(name, correlation_id=None, node_id=None, factory_id=None):
    """
    Standardized logger setup with JSON support and tagging.
    
    Args:
        name (str): Logger name.
        correlation_id (str): Optional correlation ID for request tracing.
        node_id (str): Optional edge node identifier.
        factory_id (str): Optional factory identifier.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicating handlers if already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    # Add context tagging using a LogAdapter
    extra = {
        "correlation_id": correlation_id or str(uuid4()),
        "node_id": node_id,
        "factory_id": factory_id
    }
    
    return logging.LoggerAdapter(logger, extra)
