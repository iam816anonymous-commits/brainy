import os
import pytest
from brain.core.db import init_db, save_knowledge_object
from brain.core.models import KnowledgeObject
from brain.retrieval.intent import IntentDetector
from brain.retrieval.planner import RetrievalPlanner
from brain.retrieval.ranking.orchestrator import RetrievalOrchestrator
from brain.graph.graph_manager import KnowledgeGraphManager

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_brain_retrieval.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

def test_intent_detection():
    assert IntentDetector.detect_intent("How do we fix this traceback error?") == "DEBUG_ERROR"
    assert IntentDetector.detect_intent("What was the rationale behind SQLite choice?") == "DECISION_HISTORY"
    assert IntentDetector.detect_intent("What is my active task?") == "TASK_STATUS"
    assert IntentDetector.detect_intent("Show me the class structure diagram") == "ARCHITECTURE"
    assert IntentDetector.detect_intent("Write a python method to add arrays") == "CODE_SEARCH"
    assert IntentDetector.detect_intent("Hello how is the weather today?") == "GENERAL"

def test_retrieval_planner_routing():
    save_knowledge_object(KnowledgeObject(
        id="d-1", type="Decision", project="PlanProj", title="Decision Chosen", summary="Selected SQLite", content="We chose SQLite"
    ))
    save_knowledge_object(KnowledgeObject(
        id="f-1", type="Fact", project="PlanProj", title="Fact info", summary="General facts", content="Standard vector calculations"
    ))

    gm = KnowledgeGraphManager(project_name="PlanProj")

    candidates, boosts, intent = RetrievalPlanner.plan_and_retrieve(
        query="Why did we choose SQLite?",
        project="PlanProj",
        graph_manager=gm
    )
    assert intent == "DECISION_HISTORY"
    assert "d-1" in candidates

    candidates_task, boosts_task, intent_task = RetrievalPlanner.plan_and_retrieve(
        query="what is my current task?",
        project="PlanProj",
        graph_manager=gm
    )
    assert intent_task == "TASK_STATUS"
    assert len(boosts_task) == 0

def test_retrieval_and_ranking_orchestration():
    doc = KnowledgeObject(
        id="doc-1", type="Document", project="GameProj", title="Gameplay mechanics design doc",
        summary="Describes jumping, running, sliding", content="Game utilizes custom gravity vectors for slides.",
        importance=5.0
    )
    decision = KnowledgeObject(
        id="dec-1", type="Decision", project="GameProj", title="Decision: SQLite instead of PostgreSQL",
        summary="Chose SQLite for self-containment", content="Due to target devices lacking persistent server installations.",
        importance=8.0
    )
    err = KnowledgeObject(
        id="err-1", type="Failure", project="GameProj", title="Failure: Tried Unreal Engine",
        summary="Crashed frequently on macOS", content="The rendering pipeline generated metal thread panic errors.",
        importance=9.0
    )

    doc.relations.append({"target": "dec-1", "type": "influenced_by"})

    save_knowledge_object(doc)
    save_knowledge_object(decision)
    save_knowledge_object(err)

    orchestrator = RetrievalOrchestrator(project="GameProj")

    results_dec = orchestrator.retrieve_and_rank("Why did we choose SQLite?")
    assert len(results_dec) > 0
    top_hit = results_dec[0][0]
    assert top_hit.type == "Decision"
    assert top_hit.id == "dec-1"

    results_err = orchestrator.retrieve_and_rank("What crashed on macOS metal rendering?")
    assert len(results_err) > 0
    top_err_hit = results_err[0][0]
    assert top_err_hit.type == "Failure"
    assert top_err_hit.id == "err-1"
