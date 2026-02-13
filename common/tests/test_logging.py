import json
import logging
from common.utils.logging import get_logger

def test_json_logging():
    """Verify that the logger outputs JSON with expected tags."""
    import io
    log_capture = io.StringIO()
    
    # Access the underlying logger to set up a capture handler
    adapter = get_logger("test_logger", node_id="node-123", factory_id="factory-456")
    logger = adapter.logger
    
    # Remove existing handlers for test isolation
    for h in logger.handlers[:]:
        logger.removeHandler(h)
        
    handler = logging.StreamHandler(log_capture)
    from common.utils.logging import JSONFormatter
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    adapter.info("Test message")
    
    output = log_capture.getvalue().strip()
    log_entry = json.loads(output)
    
    assert log_entry["message"] == "Test message"
    assert log_entry["node_id"] == "node-123"
    assert log_entry["factory_id"] == "factory-456"
    assert "correlation_id" in log_entry
    assert log_entry["level"] == "INFO"

def test_imports():
    """Verify that common components can be imported."""
    from common.models.metadata import ModelMetadata
    from common.schemas.validator import BaseValidator
    from common.utils.logging import get_logger
    assert True
