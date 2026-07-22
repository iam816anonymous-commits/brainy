import os
import pytest
from brain.storage.db import init_db, save_knowledge_object, get_knowledge_object
from brain.storage.models import KnowledgeObject
from brain.context.assembler import ContextPackage
from brain.adapters.chatgpt import ChatGPTAdapter
from brain.adapters.claude import ClaudeAdapter
from brain.adapters.gemini import GeminiAdapter
from brain.adapters.ollama import OllamaAdapter
from brain.learning.pipeline import LearningPipeline

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_brain_adapters.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

def test_adapters_system_prompt_formatting():
    pkg = ContextPackage(
        project="TestAdapterProj",
        current_task="Fix broken module import",
        goal="Fully deploy server",
        decisions=[{"title": "SQLite choice", "summary": "Faster deployment"}],
        known_failures=[{"title": "Tried PostgreSQL", "summary": "Too slow to launch", "content": "Requires manual docker port mapping"}]
    )

    # Check system prompt formatting
    sys_prompt = ChatGPTAdapter.format_system_prompt(pkg, "Help me write code")
    assert "TestAdapterProj" in sys_prompt
    assert "SQLite choice" in sys_prompt
    assert "Tried PostgreSQL" in sys_prompt

def test_mock_adapters():
    pkg = ContextPackage(project="MyMock")

    # ChatGPT
    res_gpt = ChatGPTAdapter.execute(pkg, "Hello ChatGPT")
    assert "[MOCK CHATGPT RESPONSE" in res_gpt

    # Claude
    res_claude = ClaudeAdapter.execute(pkg, "Hello Claude")
    assert "[MOCK CLAUDE RESPONSE" in res_claude

    # Gemini
    res_gemini = GeminiAdapter.execute(pkg, "Hello Gemini")
    assert "[MOCK GEMINI RESPONSE" in res_gemini

    # Ollama
    res_ollama = OllamaAdapter.execute(pkg, "Hello Ollama")
    assert "[MOCK OLLAMA RESPONSE" in res_ollama

def test_learning_pipeline_feedback():
    # Save a template
    obj_id = "tmpl-1"
    save_knowledge_object(KnowledgeObject(
        id=obj_id, type="Template", project="LearnProj", title="HTML template", summary="Base template", content="<html></html>", confidence=0.8, importance=5.0
    ))

    # 1. Success feedback
    res_success = LearningPipeline.process_feedback(obj_id, success=True)
    assert res_success["success_registered"] is True

    obj_retrieved = get_knowledge_object(obj_id)
    assert obj_retrieved.confidence == 0.9  # 0.8 + 0.1
    assert obj_retrieved.importance == 5.5  # 5.0 + 0.5

    # 2. Failure feedback
    res_failure = LearningPipeline.process_feedback(obj_id, success=False, user_notes="Layout broken on mobile devices")
    assert res_failure["success_registered"] is False

    obj_retrieved_2 = get_knowledge_object(obj_id)
    assert obj_retrieved_2.confidence == 0.7  # 0.9 - 0.2

    # Check that a Failure Memory was automatically recorded
    from brain.storage.db import list_knowledge_objects
    all_failures = list_knowledge_objects(project="LearnProj", obj_type="Failure")
    assert len(all_failures) == 1
    assert "HTML template" in all_failures[0].content
    assert "Layout broken on mobile devices" in all_failures[0].content
