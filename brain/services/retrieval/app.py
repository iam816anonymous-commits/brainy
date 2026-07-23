import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from brain.context.assembler import ContextAssembler, ContextPackage
from brain.context.session import ContextSession, ContextSessionManager
from brain.context.trace import ContextTrace, ObservabilityTraceRegistry
from brain.graph.graph_manager import KnowledgeGraphManager

app = FastAPI(
    title="Brain - Retrieval & Context Microservice",
    description="Orchestrates context planning, multi-stage retriever plugins, cache controls, resumable task sessions, and tracing dashboards.",
    version="1.0.0"
)

# --- Request Models ---

class ContextRequest(BaseModel):
    project: str
    user_goal: str
    current_task: Optional[str] = None
    token_budget: int = 4000

class SessionCreate(BaseModel):
    project: str
    goal: str = ""
    current_task: str = ""
    active_files: List[str] = []
    branch: str = "main"

class CheckpointCreate(BaseModel):
    name: str
    notes: str = ""

# --- Routes ---

@app.post("/context", response_model=ContextPackage)
def get_context_post(data: ContextRequest):
    package = ContextAssembler.assemble_package(
        project=data.project,
        user_goal=data.user_goal,
        current_task_input=data.current_task,
        token_budget=data.token_budget
    )
    return package

@app.get("/context/{project}", response_model=ContextPackage)
def get_context_get(
    project: str,
    user_goal: str = Query(..., description="Active user request prompt"),
    current_task: Optional[str] = Query(None, description="Active working task"),
    token_budget: int = Query(4000, description="Token size budget")
):
    package = ContextAssembler.assemble_package(
        project=project,
        user_goal=user_goal,
        current_task_input=current_task,
        token_budget=token_budget
    )
    return package

@app.get("/graph")
def get_graph(project: Optional[str] = None):
    manager = KnowledgeGraphManager(project_name=project)
    nodes = list(manager.graph.nodes)
    return manager.get_subgraph(nodes)

# --- Resumable Context Sessions ---

@app.post("/sessions", response_model=ContextSession)
def create_session(data: SessionCreate):
    return ContextSessionManager.create_session(
        project=data.project,
        goal=data.goal,
        current_task=data.current_task,
        active_files=data.active_files,
        branch=data.branch
    )

@app.get("/sessions/{session_id}", response_model=ContextSession)
def get_session(session_id: str):
    sess = ContextSessionManager.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess

@app.post("/sessions/{session_id}/checkpoints", response_model=ContextSession)
def add_checkpoint(session_id: str, data: CheckpointCreate):
    sess = ContextSessionManager.add_checkpoint(session_id, data.name, data.notes)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess

@app.get("/sessions", response_model=List[ContextSession])
def list_sessions(project: Optional[str] = None):
    return ContextSessionManager.list_sessions(project)

# --- Observability Traces ---

@app.get("/traces", response_model=List[ContextTrace])
def list_traces():
    return ObservabilityTraceRegistry.list_traces()
