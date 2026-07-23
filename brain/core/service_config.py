import os

# Microservices Port Configuration
KNOWLEDGE_SERVICE_URL = os.environ.get("BRAIN_KNOWLEDGE_SERVICE_URL", "http://localhost:8001")
RETRIEVAL_SERVICE_URL = os.environ.get("BRAIN_RETRIEVAL_SERVICE_URL", "http://localhost:8002")
EXECUTION_SERVICE_URL = os.environ.get("BRAIN_EXECUTION_SERVICE_URL", "http://localhost:8003")
