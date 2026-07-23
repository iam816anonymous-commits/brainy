import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

from brain.core.models import KnowledgeObject
from brain.core.db import init_db, save_knowledge_object, get_knowledge_object, list_knowledge_objects, delete_knowledge_object, get_all_relations
from brain.ingestion.filesystem.parser import ingest_directory
from brain.ingestion.github.ingestor import ingest_github_issue, ingest_github_commit
from brain.ingestion.docs.ingestor import ingest_markdown_document
from brain.ingestion.browser.ingestor import ingest_scraped_page
from brain.ingestion.conversation.ingestor import ingest_chat_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Brain - Knowledge & Ingestion Microservice",
    description="Manages persistent KnowledgeObjects, pluggable AST-based directory parsers, and raw ingestions.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Request Models ---

class ProjectInit(BaseModel):
    name: str
    summary: str = ""
    description: str = ""

class ObjectSave(BaseModel):
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
    lifecycle: str = "Created"
    created_from: str = ""
    derived_from: str = ""
    verified_by: str = ""
    visibility: str = "internal"
    permissions: Dict[str, Any] = {}
    group: str = ""
    metadata: Dict[str, Any] = {}
    payload: Dict[str, Any] = {}

class IngestDirRequest(BaseModel):
    directory_path: str
    project_name: str

class IngestIssueRequest(BaseModel):
    project: str
    number: int
    title: str
    body: str
    state: str
    labels: List[str] = []
    creator: str = ""

class IngestCommitRequest(BaseModel):
    project: str
    sha: str
    author: str
    message: str
    changes_summary: str = ""

# --- Routes ---

@app.post("/projects")
def init_project(data: ProjectInit):
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
    return {"id": obj_id, "status": "Project initialized"}

@app.post("/objects")
def save_object(data: ObjectSave):
    obj = KnowledgeObject(**data.model_dump())
    obj.created = datetime.now(timezone.utc).isoformat()
    obj.updated = datetime.now(timezone.utc).isoformat()
    save_knowledge_object(obj)
    return {"id": data.id, "status": "Knowledge object saved successfully"}

@app.get("/objects/{obj_id}", response_model=KnowledgeObject)
def get_object(obj_id: str):
    obj = get_knowledge_object(obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj

@app.delete("/objects/{obj_id}")
def delete_object(obj_id: str):
    delete_knowledge_object(obj_id)
    return {"status": "Deleted successfully"}

@app.get("/objects", response_model=List[KnowledgeObject])
def list_objects(project: Optional[str] = None, type: Optional[str] = None):
    return list_knowledge_objects(project=project, obj_type=type)

@app.get("/relations")
def list_relations():
    return get_all_relations()

# --- Ingestion Pipelines ---

@app.post("/ingest/directory")
def run_directory_ingest(data: IngestDirRequest):
    ids = ingest_directory(data.directory_path, data.project_name)
    return {"ingested_ids": ids, "count": len(ids)}

@app.post("/ingest/github/issue")
def run_github_issue_ingest(data: IngestIssueRequest):
    obj_id = ingest_github_issue(
        project_name=data.project,
        issue_number=data.number,
        title=data.title,
        body=data.body,
        state=data.state,
        labels=data.labels,
        creator=data.creator
    )
    return {"id": obj_id, "status": "GitHub issue ingested"}

@app.post("/ingest/github/commit")
def run_github_commit_ingest(data: IngestCommitRequest):
    obj_id = ingest_github_commit(
        project_name=data.project,
        commit_sha=data.sha,
        author=data.author,
        message=data.message,
        changes_summary=data.changes_summary
    )
    return {"id": obj_id, "status": "GitHub commit ingested"}
