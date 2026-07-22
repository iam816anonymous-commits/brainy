import os
import json
import pytest
from brain.storage.db import init_db, get_knowledge_object
from brain.sdk.mcp_server import get_context, remember, get_graph

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_brain_mcp.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

def test_mcp_server_tools():
    # Test 'remember' tool directly
    res_rem = remember(
        id="mcp-fact",
        type="Fact",
        project="McpProj",
        title="MCP works",
        summary="A summary",
        content="Our MCP implementation conforms to standards",
        importance=6.0,
        confidence=1.0,
        tags="mcp, standard, server"
    )
    assert "Successfully saved" in res_rem

    saved = get_knowledge_object("mcp-fact")
    assert saved is not None
    assert saved.type == "Fact"
    assert saved.tags == ["mcp", "standard", "server"]

    # Test 'get_context' tool directly
    res_ctx = get_context(project="McpProj", user_goal="Understand MCP implementation details")
    pkg = json.loads(res_ctx)
    assert pkg["project"] == "McpProj"
    assert len(pkg["related_docs"]) == 1
    assert pkg["related_docs"][0]["id"] == "mcp-fact"

    # Test 'get_graph' tool directly
    res_graph = get_graph(project="McpProj")
    graph = json.loads(res_graph)
    assert len(graph["nodes"]) == 1
    assert graph["nodes"][0]["id"] == "mcp-fact"
