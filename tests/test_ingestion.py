import os
import pytest
from brain.storage.db import init_db, get_knowledge_object, list_knowledge_objects
from brain.ingestion.filesystem.parser import ingest_directory
from brain.ingestion.github.ingestor import ingest_github_issue, ingest_github_commit
from brain.ingestion.docs.ingestor import ingest_markdown_document
from brain.ingestion.browser.ingestor import ingest_scraped_page
from brain.ingestion.conversation.ingestor import ingest_chat_session

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_brain_ingestion.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

def test_filesystem_ingestion_and_ast_parsing(tmp_path):
    # Create mock folder structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    # Write python code
    py_code = """
class MathService:
    \"\"\"Service for mathematical calculations.\"\"\"
    def add(self, a, b):
        \"\"\"Adds a and b.\"\"\"
        return a + b

    def test_add(self):
        assert self.add(2, 3) == 5

def global_utility(x):
    \"\"\"Global helper utility.\"\"\"
    return x * 2
"""
    (src_dir / "math_service.py").write_text(py_code)
    (src_dir / "notes.md").write_text("# Math Notes\nThis describes standard additions.")

    ingested_ids = ingest_directory(str(src_dir), "MathProj")

    # Check that Project exists
    proj = get_knowledge_object("project::MathProj")
    assert proj is not None
    assert proj.type == "Project"

    # Check that File exists
    file_id = "file::MathProj::math_service.py"
    file_obj = get_knowledge_object(file_id)
    assert file_obj is not None
    assert file_obj.type == "Code"

    # Check Class extracted via AST
    class_id = f"{file_id}::class::MathService"
    class_obj = get_knowledge_object(class_id)
    assert class_obj is not None
    assert class_obj.type == "Class"
    assert "MathService" in class_obj.title

    # Check global utility function extracted via AST
    func_id = f"{file_id}::function::global_utility"
    func_obj = get_knowledge_object(func_id)
    assert func_obj is not None
    assert func_obj.type == "Function"
    assert "Global helper utility." in func_obj.summary

def test_github_ingestion():
    issue_id = ingest_github_issue("MyProj", 42, "NullPointerException in parsing", "Occurs when JSON is blank", "open", ["bug", "critical"])
    commit_id = ingest_github_commit("MyProj", "aabbccddeeff", "jules", "Fix null pointer parsing", "Modified parser.py lines 20-30")

    issue_obj = get_knowledge_object(issue_id)
    assert issue_obj is not None
    assert issue_obj.type == "Bug"
    assert "NullPointerException" in issue_obj.title

    commit_obj = get_knowledge_object(commit_id)
    assert commit_obj is not None
    assert commit_obj.type == "Code"
    assert "aabbccdd" in commit_obj.tags

def test_other_ingestors(tmp_path):
    # Test Markdown
    doc_file = tmp_path / "architecture.md"
    doc_file.write_text("# Project Architecture\nThis is standard high-level architecture docs.\nWe use SQLite for context storage.")

    doc_id = ingest_markdown_document(str(doc_file), "MyProj")
    doc_obj = get_knowledge_object(doc_id)
    assert doc_obj is not None
    assert doc_obj.type == "Document"
    assert doc_obj.title == "Project Architecture"

    # Test Browser Ingestion
    web_id = ingest_scraped_page("https://example.com/api", "API Reference Docs", "<html>API</html>", "API Reference description", "MyProj", ["reference"])
    web_obj = get_knowledge_object(web_id)
    assert web_obj is not None
    assert "Reference" in web_obj.title

    # Test Chat Conversation Ingestion
    chat_id = ingest_chat_session(
        "session-abc",
        "MyProj",
        "Fixing UI",
        [
            {"role": "user", "content": "How do I center a div?"},
            {"role": "assistant", "content": "Use flexbox: justify-content: center;"}
        ]
    )
    chat_obj = get_knowledge_object(chat_id)
    assert chat_obj is not None
    assert chat_obj.type == "Conversation"
    assert "How do I center a div?" in chat_obj.summary
