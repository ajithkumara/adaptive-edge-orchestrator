class ModelMetadata:
    """Standardized model metadata structure."""
    def __init__(self, model_id, version, framework, description=""):
        self.model_id = model_id
        self.version = version
        self.framework = framework
        self.description = description

    def to_dict(self):
        return {
            "model_id": self.model_id,
            "version": self.version,
            "framework": self.framework,
            "description": self.description
        }
