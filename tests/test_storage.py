import os
import pytest
from brain.core.db import init_db, save_knowledge_object, get_knowledge_object, list_knowledge_objects, delete_knowledge_object
from brain.core.models import KnowledgeObject

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    # Set DB path to a temporary file
    db_file = tmp_path / "test_brain.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

def test_save_and_retrieve_knowledge_object():
    obj = KnowledgeObject(
        id="proj-1",
        type="Project",
        project="TestProj",
        title="Test Project Title",
        summary="Test Summary",
        content="Test Content",
        importance=5.0,
        confidence=0.9,
        tags=["pytest", "storage"],
        relations=[{"target": "task-1", "type": "has_task"}],
        source="manual",
        owner="jules"
    )

    save_knowledge_object(obj)

    retrieved = get_knowledge_object("proj-1")
    assert retrieved is not None
    assert retrieved.id == "proj-1"
    assert retrieved.type == "Project"
    assert retrieved.project == "TestProj"
    assert retrieved.title == "Test Project Title"
    assert retrieved.summary == "Test Summary"
    assert retrieved.content == "Test Content"
    assert retrieved.importance == 5.0
    assert retrieved.confidence == 0.9
    assert retrieved.tags == ["pytest", "storage"]
    assert len(retrieved.relations) == 1
    assert retrieved.relations[0]["target"] == "task-1"
    assert retrieved.relations[0]["type"] == "has_task"
    assert retrieved.source == "manual"
    assert retrieved.owner == "jules"

def test_list_and_delete():
    obj1 = KnowledgeObject(
        id="id-1",
        type="Fact",
        project="ProjA",
        title="Fact 1",
        summary="A summary",
        content="Some content"
    )
    obj2 = KnowledgeObject(
        id="id-2",
        type="Decision",
        project="ProjA",
        title="Decision 1",
        summary="Another summary",
        content="Other content"
    )
    obj3 = KnowledgeObject(
        id="id-3",
        type="Fact",
        project="ProjB",
        title="Fact 2",
        summary="Summary B",
        content="Content B"
    )

    save_knowledge_object(obj1)
    save_knowledge_object(obj2)
    save_knowledge_object(obj3)

    all_objects = list_knowledge_objects()
    assert len(all_objects) == 3

    proja_objects = list_knowledge_objects(project="ProjA")
    assert len(proja_objects) == 2

    facts_proja = list_knowledge_objects(project="ProjA", obj_type="Fact")
    assert len(facts_proja) == 1
    assert facts_proja[0].id == "id-1"

    delete_knowledge_object("id-1")
    assert get_knowledge_object("id-1") is None
    assert len(list_knowledge_objects(project="ProjA")) == 1
