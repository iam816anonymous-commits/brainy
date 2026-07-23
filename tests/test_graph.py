import os
import pytest
from brain.core.db import init_db, save_knowledge_object
from brain.core.models import KnowledgeObject
from brain.graph.graph_manager import KnowledgeGraphManager

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_brain_graph.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

def test_graph_creation_and_traversal():
    proj = KnowledgeObject(
        id="p1", type="Project", project="MyProj", title="My Proj", summary="", content="",
        relations=[{"target": "m1", "type": "contains_module"}]
    )
    mod = KnowledgeObject(
        id="m1", type="Folder", project="MyProj", title="Module 1", summary="", content="",
        relations=[{"target": "f1", "type": "contains_file"}]
    )
    file_obj = KnowledgeObject(
        id="f1", type="Code", project="MyProj", title="File 1", summary="", content="",
        relations=[{"target": "m1", "type": "part_of"}]
    )

    save_knowledge_object(proj)
    save_knowledge_object(mod)
    save_knowledge_object(file_obj)

    manager = KnowledgeGraphManager(project_name="MyProj")

    assert manager.graph.has_node("p1")
    assert manager.graph.has_node("m1")
    assert manager.graph.has_node("f1")

    assert manager.graph.has_edge("p1", "m1")
    assert manager.graph.has_edge("m1", "f1")

    related_to_p1 = manager.get_related_nodes("p1", max_distance=1)
    assert "p1" in related_to_p1
    assert "m1" in related_to_p1
    assert "f1" not in related_to_p1

    related_to_p1_dist2 = manager.get_related_nodes("p1", max_distance=2)
    assert "f1" in related_to_p1_dist2

    sub = manager.get_subgraph(["p1", "m1"])
    assert len(sub["nodes"]) == 2
    assert len(sub["edges"]) == 1
    assert sub["edges"][0]["source"] == "p1"
    assert sub["edges"][0]["target"] == "m1"
