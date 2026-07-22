import os
import json
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from brain.storage.db import init_db, save_knowledge_object, get_knowledge_object
from brain.storage.models import KnowledgeObject
from brain.context.assembler import ContextAssembler

# Initialize FastMCP Server
mcp_server = FastMCP("Brain-Context-OS")

@mcp_server.tool()
def get_context(project: str, user_goal: str, current_task: Optional[str] = None) -> str:
    """
    Retrieves the mathematically optimal context package for a given user goal and task.
    This aggregates, ranks, and compresses active files, decisions, previous failures,
    rules, and documents.
    """
    init_db()
    pkg = ContextAssembler.assemble_package(
        project=project,
        user_goal=user_goal,
        current_task_input=current_task
    )
    return json.dumps(pkg.model_dump(), indent=2)

@mcp_server.tool()
def remember(
    id: str,
    type: str,
    project: str,
    title: str,
    summary: str,
    content: str,
    importance: float = 5.0,
    confidence: float = 1.0,
    tags: str = ""  # comma-separated
) -> str:
    """
    Persistently stores a knowledge object in the Brain.
    Types include: Project, Task, Decision, Fact, Conversation, Document, Code, Issue, Bug, Architecture, Failure, Success, Pattern, Template, Constraint, Rule.
    """
    init_db()
    parsed_tags = [t.strip() for t in tags.split(",") if t.strip()]
    obj = KnowledgeObject(
        id=id,
        type=type,
        project=project,
        title=title,
        summary=summary,
        content=content,
        importance=importance,
        confidence=confidence,
        tags=parsed_tags
    )
    save_knowledge_object(obj)
    return f"Successfully saved knowledge object '{id}' under project '{project}'."

@mcp_server.tool()
def get_graph(project: Optional[str] = None) -> str:
    """
    Retrieves the stored project's knowledge graph (nodes & edges representation).
    """
    from brain.graph.graph_manager import KnowledgeGraphManager
    init_db()
    manager = KnowledgeGraphManager(project_name=project)
    nodes = list(manager.graph.nodes)
    sub = manager.get_subgraph(nodes)
    return json.dumps(sub, indent=2)

def run_mcp_server():
    """
    Launches the MCP server via standard I/O (stdio).
    """
    mcp_server.run()

if __name__ == "__main__":
    run_mcp_server()
