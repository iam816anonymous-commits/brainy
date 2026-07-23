from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class KnowledgeObject(BaseModel):
    id: str
    type: str
    project: str
    title: str
    summary: str
    content: str
    importance: float = 1.0
    confidence: float = 1.0
    created: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: List[str] = Field(default_factory=list)
    relations: List[Dict[str, Any]] = Field(default_factory=list)

    # Platform fields
    lifecycle: str = "Created"
    source: str = ""
    owner: str = ""
    created_from: str = ""
    derived_from: str = ""
    verified_by: str = ""
    last_verified: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    visibility: str = "internal"
    permissions: Dict[str, Any] = Field(default_factory=dict)
    group: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    payload: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeObjectRelation(BaseModel):
    source_id: str
    target_id: str
    relation_type: str
