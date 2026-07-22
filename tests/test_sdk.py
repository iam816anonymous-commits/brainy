import os
import pytest
from fastapi.testclient import TestClient
from brain.storage.db import init_db
from brain.api.app import app
from brain.sdk.client import BrainClient

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_brain_sdk.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

class MockRequestsSession:
    """
    Simulates requests calls by routing them directly into FastAPI's TestClient
    to verify SDK compatibility without spinning up a real TCP socket listener.
    """
    def __init__(self, client: TestClient):
        self.client = client

    def post(self, url: str, json: dict = None, **kwargs):
        # Extract relative path
        path = url.split("http://localhost:8000")[-1]
        resp = self.client.post(path, json=json)
        # Mock requests.Response
        resp.raise_for_status = lambda: None if resp.status_code == 200 else exec("raise Exception()")
        return resp

    def get(self, url: str, params: dict = None, **kwargs):
        path = url.split("http://localhost:8000")[-1]
        resp = self.client.get(path, params=params)
        resp.raise_for_status = lambda: None if resp.status_code == 200 else exec("raise Exception()")
        return resp

def test_sdk_client_integration():
    test_client = TestClient(app)
    sdk = BrainClient(base_url="http://localhost:8000")

    # Patch request operations to run inside the testclient
    import requests
    mock_session = MockRequestsSession(test_client)
    requests.post = mock_session.post
    requests.get = mock_session.get

    # 1. Create project
    res_proj = sdk.create_project("SdkProj", "SDK Summary", "Extended Description")
    assert "project::sdkproj" in res_proj["id"]

    # 2. Add working memory task
    res_task = sdk.create_task("SdkProj", "Configure test pipelines", ["test.py"])
    assert "working-memory" in res_task["id"]

    # 3. Create generic memory
    res_rem = sdk.remember(
        id="fact-1",
        obj_type="Fact",
        project="SdkProj",
        title="Fact A",
        summary="Summary A",
        content="Content A"
    )
    assert res_rem["id"] == "fact-1"

    # 4. Query Context Package
    pkg = sdk.get_context("SdkProj", "Fact A content details")
    assert pkg["project"] == "SdkProj"
    assert len(pkg["related_docs"]) >= 1
    assert pkg["related_docs"][0]["id"] == "fact-1"
