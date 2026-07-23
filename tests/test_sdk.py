import os
import pytest
from typing import Tuple
from fastapi.testclient import TestClient

from brain.core.db import init_db
from brain.services.knowledge.app import app as knowledge_app
from brain.services.retrieval.app import app as retrieval_app
from brain.services.execution.app import app as execution_app
from brain.sdk.client import BrainClient

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_brain_microservices_sdk.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

class MockDistributedNetworkSession:
    """
    Simulates a distributed HTTP microservices mesh, routing client request URLs
    to their respective standalone FastAPI app TestClients based on port numbers.
    """
    def __init__(self):
        self.knowledge_client = TestClient(knowledge_app)
        self.retrieval_client = TestClient(retrieval_app)
        self.execution_client = TestClient(execution_app)

    def _route(self, url: str) -> Tuple[TestClient, str]:
        if "8001" in url:
            return self.knowledge_client, url.split("8001")[-1]
        elif "8002" in url:
            return self.retrieval_client, url.split("8002")[-1]
        elif "8003" in url:
            return self.execution_client, url.split("8003")[-1]
        raise ValueError(f"Unrouted microservices destination: {url}")

    def post(self, url: str, json: dict = None, **kwargs):
        client, path = self._route(url)
        resp = client.post(path, json=json)
        resp.raise_for_status = lambda: None if resp.status_code == 200 else exec("raise Exception(resp.text)")
        return resp

    def get(self, url: str, params: dict = None, **kwargs):
        client, path = self._route(url)
        resp = client.get(path, params=params)
        resp.raise_for_status = lambda: None if resp.status_code == 200 else exec("raise Exception(resp.text)")
        return resp

def test_distributed_microservices_sdk_integration():
    import requests
    mesh = MockDistributedNetworkSession()
    # Patch request networking onto our mock distributed session
    requests.post = mesh.post
    requests.get = mesh.get

    # Instantiate the unified API Gateway client pointing to the port locations
    sdk = BrainClient(
        knowledge_url="http://localhost:8001",
        retrieval_url="http://localhost:8002",
        execution_url="http://localhost:8003"
    )

    # 1. Store project inside Knowledge & Ingestion service (8001)
    res_proj = sdk.create_project("MicroProj", "Distributed architecture v1", "Using separate port bindings")
    assert "project::microproj" in res_proj["id"]

    # 2. Add canonical fact
    res_rem = sdk.remember(
        id="can-fact-1",
        obj_type="Fact",
        project="MicroProj",
        title="Distributed mesh",
        summary="Communication occurs over HTTP REST",
        content="Microservices isolate storage, retrieval and platform adapters"
    )
    assert "saved" in res_rem["status"]

    # 3. Retrieve Context package from Retrieval & Context service (8002)
    pkg = sdk.get_context("MicroProj", "Distributed mesh architectures")
    assert pkg["project"] == "MicroProj"
    assert len(pkg["related_docs"]) >= 1
    assert pkg["related_docs"][0]["id"] == "can-fact-1"

    # 4. Trigger resumable session creation on Retrieval service (8002)
    sess = sdk.create_session("MicroProj", goal="Migrate microservices", current_task="Map execution ports")
    assert sess["id"] is not None
    assert sess["goal"] == "Migrate microservices"

    # 5. Dispatch completion adapter on Execution service (8003)
    res_claude = sdk.execute_claude("MicroProj", "Migrate microservices", "Refactor ports", model="claude-3-5")
    assert "[MOCK CLAUDE RESPONSE" in res_claude["response"]

    # 6. Process failure feedback loop outcome on Execution service (8003)
    res_feed = sdk.submit_feedback("can-fact-1", success=False, feedback="Lost connection pool", project="MicroProj")
    assert res_feed["success_registered"] is False
