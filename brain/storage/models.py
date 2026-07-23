from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class KnowledgeObject(BaseModel):
    # Canonical unified ID
    id: str

    # Unified Object Type (Decision, Failure, Code, Class, Method, Bug, Fact, etc.)
    type: str

    # Project scope
    project: str

    # Standard metadata text fields
    title: str
    summary: str
    content: str

    # Core scoring attributes
    importance: float = 1.0  # scale of 0.0 to 10.0
    confidence: float = 1.0  # scale of 0.0 to 1.0

    # Date tracking
    created: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Direct search tags and relationship maps
    tags: List[str] = Field(default_factory=list)
    relations: List[Dict[str, Any]] = Field(default_factory=list)  # [{"target": str, "type": str}]

    # --- Platform Engineering Expanded Fields ---

    # 1. Knowledge Lifecycle State
    # States: Created, Verified, Active, Referenced, Archived, Deleted
    lifecycle: str = "Created"

    # 2. Knowledge Provenance (Lineage tracking)
    source: str = ""
    owner: str = ""
    created_from: str = ""      # Tool, pipeline, or raw import trigger
    derived_from: str = ""      # Reference to parent ID or upstream entity
    verified_by: str = ""       # Expert or automated compiler check name
    last_verified: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # 3. Enterprise Permissions
    visibility: str = "internal"  # public, private, internal
    permissions: Dict[str, Any] = Field(default_factory=dict) # ACL mapping user/group roles
    group: str = ""

    # 4. Extensible metadata & dynamic payload blocks
    metadata: Dict[str, Any] = Field(default_factory=dict)
    payload: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeObjectRelation(BaseModel):
    source_id: str
    target_id: str
    relation_type: str
