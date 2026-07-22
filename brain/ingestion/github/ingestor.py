import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from brain.storage.models import KnowledgeObject
from brain.storage.db import save_knowledge_object

def ingest_github_issue(
    project_name: str,
    issue_number: int,
    title: str,
    body: str,
    state: str,
    labels: List[str] = [],
    creator: str = "",
    created_at: Optional[str] = None
) -> str:
    """
    Ingests a GitHub Issue as an 'Issue' or 'Bug' KnowledgeObject.
    """
    is_bug = any("bug" in label.lower() for label in labels)
    obj_type = "Bug" if is_bug else "Issue"
    obj_id = f"github::{project_name}::issue::{issue_number}"

    obj = KnowledgeObject(
        id=obj_id,
        type=obj_type,
        project=project_name,
        title=f"GitHub Issue #{issue_number}: {title}",
        summary=f"GitHub issue {issue_number} in state: {state}",
        content=body,
        importance=4.0 if state == "open" else 2.0,
        confidence=1.0,
        tags=labels + ["github", state],
        created=created_at or datetime.now(timezone.utc).isoformat(),
        updated=datetime.now(timezone.utc).isoformat(),
        source=f"github/issues/{issue_number}",
        owner=creator
    )
    save_knowledge_object(obj)
    return obj_id

def ingest_github_commit(
    project_name: str,
    commit_sha: str,
    author: str,
    message: str,
    changes_summary: str = "",
    created_at: Optional[str] = None
) -> str:
    """
    Ingests a commit into our system, representing code history/changes.
    """
    obj_id = f"github::{project_name}::commit::{commit_sha[:8]}"

    obj = KnowledgeObject(
        id=obj_id,
        type="Code",
        project=project_name,
        title=f"Commit: {message.splitlines()[0]}",
        summary=f"Commit by {author}: {message}",
        content=changes_summary or message,
        importance=2.0,
        confidence=1.0,
        tags=["commit", "github", commit_sha[:8]],
        created=created_at or datetime.now(timezone.utc).isoformat(),
        source=f"github/commits/{commit_sha}",
        owner=author
    )
    save_knowledge_object(obj)
    return obj_id
