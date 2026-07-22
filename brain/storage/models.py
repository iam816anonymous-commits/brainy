from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class KnowledgeObject(BaseModel):
    id: str
    type: str  # Project, Task, Decision, Fact, Conversation, Document, Code, API, Issue, Bug, Architecture, Meeting, Workflow, Rule, Constraint, Failure, Success, Pattern, Template
    project: str
    title: str
    summary: str
    content: str
    importance: float = 1.0  # scale of 0.0 to 10.0
    confidence: float = 1.0  # scale of 0.0 to 1.0
    created: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: List[str] = Field(default_factory=list)
    relations: List[Dict[str, Any]] = Field(default_factory=list)  # list of {"target": str, "type": str}
    source: str = ""
    owner: str = ""

class KnowledgeObjectRelation(BaseModel):
    source_id: str
    target_id: str
    relation_type: str
