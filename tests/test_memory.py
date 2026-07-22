import os
import pytest
from brain.storage.db import init_db, get_knowledge_object
from brain.memory.manager import (
    remember_working_memory,
    remember_episodic_memory,
    remember_semantic_relation,
    remember_decision,
    remember_failure,
    remember_pattern
)

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_brain_memory.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

def test_working_memory():
    obj_id = remember_working_memory("TestProj", "Refactor storage layer", ["db.py", "models.py"], "main", ["import error"])
    obj = get_knowledge_object(obj_id)
    assert obj is not None
    assert obj.type == "Task"
    assert "Refactor storage layer" in obj.content
    assert "import error" in obj.content

def test_episodic_memory():
    obj_id = remember_episodic_memory("TestProj", "Tried to import math", "Failed", "Circular dependency")
    obj = get_knowledge_object(obj_id)
    assert obj is not None
    assert obj.type == "Workflow"
    assert "Circular dependency" in obj.content

def test_semantic_relation():
    remember_semantic_relation("TestProj", "Playwright", "uses", "Browser Runtime")
    obj_a = get_knowledge_object("concept::testproj::playwright")
    assert obj_a is not None
    assert len(obj_a.relations) == 1
    assert obj_a.relations[0]["target"] == "concept::testproj::browser_runtime"
    assert obj_a.relations[0]["type"] == "uses"

def test_decision_memory():
    obj_id = remember_decision("TestProj", "Don't use Docker", "Windows deployment constraints", "Use local virtual environments")
    obj = get_knowledge_object(obj_id)
    assert obj is not None
    assert obj.type == "Decision"
    assert "Windows deployment" in obj.content

def test_failure_memory():
    obj_id = remember_failure("TestProj", "Tried Selenium", "Dynamic DOM loaded via react", "Use Playwright instead")
    obj = get_knowledge_object(obj_id)
    assert obj is not None
    assert obj.type == "Failure"
    assert "Dynamic DOM" in obj.content

def test_pattern_memory():
    obj_id = remember_pattern("TestProj", "Auth Flow", ["Search", "Login", "Extract", "Logout"], "Standard authentication mechanism")
    obj = get_knowledge_object(obj_id)
    assert obj is not None
    assert obj.type == "Pattern"
    assert "3. Extract" in obj.content
