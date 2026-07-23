import os
import pytest
from brain.core.db import init_db, save_knowledge_object
from brain.core.models import KnowledgeObject
from brain.compression.compressor import ContextCompressor
from brain.context.assembler import ContextAssembler

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_brain_context.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

def test_context_compressor():
    text = "hello world"
    assert ContextCompressor.estimate_tokens(text) == 2

    large_text = "\n".join([f"Line number {i}" for i in range(100)])
    compressed = ContextCompressor.compress_content(large_text, max_tokens=20)
    assert "[... content truncated to preserve context budget ...]" in compressed

def test_context_assembler():
    save_knowledge_object(KnowledgeObject(
        id="d-1", type="Decision", project="ContextProj", title="Decision Chosen", summary="Selected SQLite", content="SQLite is easy to use and configured by default", importance=5.0
    ))
    save_knowledge_object(KnowledgeObject(
        id="f-1", type="Failure", project="ContextProj", title="Docker failed", summary="Failed to deploy Docker on Windows Home", content="Requires WSL2 which is uninstalled", importance=9.0
    ))

    package = ContextAssembler.assemble_package(
        project="ContextProj",
        user_goal="Setup persistence and deploy the app",
        current_task_input="Write storage initialization logic"
    )

    assert package.project == "ContextProj"
    assert package.goal == "Setup persistence and deploy the app"
    assert package.current_task == "Write storage initialization logic"

    assert len(package.decisions) == 1
    assert package.decisions[0]["title"] == "Decision Chosen"

    assert len(package.known_failures) == 1
    assert package.known_failures[0]["title"] == "Docker failed"
