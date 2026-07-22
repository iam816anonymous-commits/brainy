from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from brain.storage.models import KnowledgeObject
from brain.storage.db import save_knowledge_object, get_knowledge_object, list_knowledge_objects, delete_knowledge_object
from brain.graph.graph_manager import KnowledgeGraphManager
from brain.memory.manager import (
    remember_working_memory,
    remember_episodic_memory,
    remember_semantic_relation,
    remember_decision,
    remember_failure,
    remember_pattern
)
from brain.context.assembler import ContextAssembler, ContextPackage

router = APIRouter()

# --- Request/Response Models ---

class ProjectCreate(BaseModel):
    name: str
    summary: str = ""
    description: str = ""

class TaskCreate(BaseModel):
    project: str
    task: str
    active_files: List[str] = []
    branch: str = "main"
    errors: List[str] = []

class RememberRequest(BaseModel):
    id: str
    type: str
    project: str
    title: str
    summary: str
    content: str
    importance: float = 1.0
    confidence: float = 1.0
    tags: List[str] = []
    relations: List[Dict[str, Any]] = []
    source: str = ""
    owner: str = ""

class ContextRequest(BaseModel):
    project: str
    user_goal: str
    current_task: Optional[str] = None
    model: Optional[str] = None

class ConversationCreate(BaseModel):
    project: str
    session_id: str
    title: str
    messages: List[Dict[str, str]]
    summary: Optional[str] = None

class DecisionCreate(BaseModel):
    project: str
    title: str
    reason: str
    alternatives: str = ""
    status: str = "approved"

class FailureCreate(BaseModel):
    project: str
    attempted_action: str
    reason_for_failure: str
    resolution_or_lessons: str = ""

class DocumentCreate(BaseModel):
    project: str
    title: str
    content: str
    summary: str = ""
    tags: List[str] = []
    source: str = ""

class CodeCreate(BaseModel):
    project: str
    filepath: str
    content: str
    summary: str = ""
    tags: List[str] = []

class FeedbackRequest(BaseModel):
    id: str
    success: bool
    feedback: str = ""

# --- Routes ---

@router.post("/projects")
def create_project(data: ProjectCreate):
    obj_id = f"project::{data.name.lower()}"
    obj = KnowledgeObject(
        id=obj_id,
        type="Project",
        project=data.name,
        title=f"Project: {data.name}",
        summary=data.summary or f"Project node for {data.name}",
        content=data.description or data.summary,
        importance=10.0,
        confidence=1.0,
        tags=["project", "root"]
    )
    save_knowledge_object(obj)
    return {"id": obj_id, "status": "Project initialized successfully"}

@router.post("/tasks")
def create_task(data: TaskCreate):
    obj_id = remember_working_memory(
        project=data.project,
        current_task=data.task,
        active_files=data.active_files,
        branch=data.branch,
        current_errors=data.errors
    )
    return {"id": obj_id, "status": "Task working memory saved"}

@router.post("/remember")
def remember_generic(data: RememberRequest):
    obj = KnowledgeObject(
        id=data.id,
        type=data.type,
        project=data.project,
        title=data.title,
        summary=data.summary,
        content=data.content,
        importance=data.importance,
        confidence=data.confidence,
        tags=data.tags,
        relations=data.relations,
        source=data.source,
        owner=data.owner,
        created=datetime.now(timezone.utc).isoformat(),
        updated=datetime.now(timezone.utc).isoformat()
    )
    save_knowledge_object(obj)
    return {"id": data.id, "status": "Knowledge object stored successfully"}

@router.post("/context", response_model=ContextPackage)
def get_context_post(data: ContextRequest):
    package = ContextAssembler.assemble_package(
        project=data.project,
        user_goal=data.user_goal,
        current_task_input=data.current_task
    )
    return package

@router.post("/conversation")
def remember_conversation(data: ConversationCreate):
    from brain.ingestion.conversation.ingestor import ingest_chat_session
    obj_id = ingest_chat_session(
        session_id=data.session_id,
        project_name=data.project,
        title=data.title,
        messages=data.messages,
        summary=data.summary
    )
    return {"id": obj_id, "status": "Conversation dialogue ingested successfully"}

@router.post("/decision")
def create_decision(data: DecisionCreate):
    obj_id = remember_decision(
        project=data.project,
        decision_title=data.title,
        reason=data.reason,
        alternatives=data.alternatives,
        status=data.status
    )
    return {"id": obj_id, "status": "Decision logged successfully"}

@router.post("/failure")
def create_failure(data: FailureCreate):
    obj_id = remember_failure(
        project=data.project,
        attempted_action=data.attempted_action,
        reason_for_failure=data.reason_for_failure,
        resolution_or_lessons=data.resolution_or_lessons
    )
    return {"id": obj_id, "status": "Failure lesson-learned registered successfully"}

@router.post("/document")
def create_document(data: DocumentCreate):
    obj_id = f"doc::{data.project.lower()}::{data.title.lower().replace(' ', '_')}"
    obj = KnowledgeObject(
        id=obj_id,
        type="Document",
        project=data.project,
        title=data.title,
        summary=data.summary or f"Document: {data.title}",
        content=data.content,
        importance=5.0,
        tags=data.tags or ["doc"],
        source=data.source
    )
    save_knowledge_object(obj)
    return {"id": obj_id, "status": "Document archived successfully"}

@router.post("/code")
def create_code(data: CodeCreate):
    obj_id = f"code::{data.project.lower()}::{data.filepath.lower().replace('/', '_')}"
    obj = KnowledgeObject(
        id=obj_id,
        type="Code",
        project=data.project,
        title=f"Code: {data.filepath}",
        summary=data.summary or f"Source file: {data.filepath}",
        content=data.content,
        importance=6.0,
        tags=data.tags or ["code"]
    )
    save_knowledge_object(obj)
    return {"id": obj_id, "status": "Code snippet recorded successfully"}

@router.post("/feedback")
def submit_feedback(data: FeedbackRequest):
    obj = get_knowledge_object(data.id)
    if not obj:
        raise HTTPException(status_code=404, detail="Knowledge object not found")

    # Adjust confidence and importance parameters dynamically based on user outcomes!
    if data.success:
        obj.confidence = min(obj.confidence + 0.1, 1.0)
        obj.importance = min(obj.importance + 0.5, 10.0)
    else:
        obj.confidence = max(obj.confidence - 0.2, 0.0)
        # If failure, we flag it as less reliable or note the mismatch
        obj.tags = list(set(obj.tags) | {"flagged-failure"})

    obj.updated = datetime.now(timezone.utc).isoformat()
    save_knowledge_object(obj)
    return {"id": data.id, "status": "Feedback processed and ranking variables adapted"}

@router.get("/context/{project}", response_model=ContextPackage)
def get_context_get(
    project: str,
    user_goal: str = Query(..., description="The user query or intention"),
    current_task: Optional[str] = Query(None, description="The current active task")
):
    package = ContextAssembler.assemble_package(
        project=project,
        user_goal=user_goal,
        current_task_input=current_task
    )
    return package

@router.get("/graph")
def get_graph(project: Optional[str] = None):
    manager = KnowledgeGraphManager(project_name=project)
    # Serialize entire loaded graph structure
    nodes = list(manager.graph.nodes)
    sub = manager.get_subgraph(nodes)
    return sub

@router.get("/timeline")
def get_timeline(project: Optional[str] = None):
    """
    Returns chronological timeline of ingested events and historical episodes.
    """
    objs = list_knowledge_objects(project=project)
    # Filter for episodic/workflow, decision, conversation logs, failure
    timeline_types = {"Workflow", "Decision", "Conversation", "Failure", "Meeting"}
    filtered = [o for o in objs if o.type in timeline_types]

    # Sort chronologically by created date
    filtered.sort(key=lambda x: x.created or "")

    return [
        {
            "id": o.id,
            "type": o.type,
            "title": o.title,
            "summary": o.summary,
            "created": o.created
        }
        for o in filtered
    ]

@router.get("/memories")
def get_memories(project: Optional[str] = None, type: Optional[str] = None):
    """
    Lists memories filtered by project or unified memory type.
    """
    objs = list_knowledge_objects(project=project, obj_type=type)
    return [
        {
            "id": o.id,
            "type": o.type,
            "title": o.title,
            "summary": o.summary,
            "importance": o.importance,
            "confidence": o.confidence,
            "tags": o.tags
        }
        for o in objs
    ]
