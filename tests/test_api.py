import os
import pytest
from fastapi.testclient import TestClient
from brain.storage.db import init_db
from brain.api.app import app

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_brain_api.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

def test_api_endpoints():
    client = TestClient(app)

    # 1. Initialize project
    resp = client.post("/projects", json={"name": "ApiProj", "summary": "API Project summary", "description": "Extended documentation description"})
    assert resp.status_code == 200
    assert "project::apiproj" in resp.json()["id"]

    # 2. Add task status (working memory)
    resp = client.post("/tasks", json={"project": "ApiProj", "task": "Integrate API Gateway", "active_files": ["routes.py"], "errors": ["fastapi import error"]})
    assert resp.status_code == 200

    # 3. Add Decision
    resp = client.post("/decision", json={"project": "ApiProj", "title": "Use FastAPI", "reason": "FastAPI is extremely fast and auto-documents"})
    assert resp.status_code == 200

    # 4. Add Failure
    resp = client.post("/failure", json={"project": "ApiProj", "attempted_action": "Use Flask", "reason_for_failure": "Flask lacked async/await support natively in old versions"})
    assert resp.status_code == 200

    # 5. Fetch timeline
    resp = client.get("/timeline?project=ApiProj")
    assert resp.status_code == 200
    timeline = resp.json()
    assert len(timeline) >= 2  # contains decision and failure

    # 6. Fetch graph
    resp = client.get("/graph?project=ApiProj")
    assert resp.status_code == 200
    graph = resp.json()
    assert len(graph["nodes"]) >= 3

    # 7. Get standard context package
    resp = client.get("/context/ApiProj?user_goal=Choose a fast web framework")
    assert resp.status_code == 200
    pkg = resp.json()
    assert pkg["project"] == "ApiProj"
    assert len(pkg["decisions"]) >= 1
    assert pkg["decisions"][0]["title"] == "Decision: Use FastAPI"

    # 8. Submit feedback to adapt ranking variables
    decision_id = "decision::apiproj::use_fastapi"
    resp = client.post("/feedback", json={"id": decision_id, "success": True, "feedback": "FastAPI choice worked out beautifully!"})
    assert resp.status_code == 200
    assert "adapted" in resp.json()["status"]
