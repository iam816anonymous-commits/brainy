import os
import re
from datetime import datetime, timezone
from typing import List, Dict, Any
from brain.core.models import KnowledgeObject
from brain.core.db import save_knowledge_object

def ingest_markdown_document(filepath: str, project_name: str) -> str:
    """
    Ingests a markdown documentation file, attempting to parse structured headers.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Markdown file {filepath} not found.")

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(filepath)

    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    summary = ""
    for p in paragraphs:
        if not p.startswith("#") and not p.startswith("!") and not p.startswith("["):
            summary = p[:200] + "..." if len(p) > 200 else p
            break
    if not summary:
        summary = f"Documentation file {os.path.basename(filepath)}"

    filename = os.path.basename(filepath)
    obj_id = f"doc::{project_name.lower()}::{filename}"

    obj = KnowledgeObject(
        id=obj_id,
        type="Document",
        project=project_name,
        title=title,
        summary=summary,
        content=content,
        importance=5.0,
        confidence=1.0,
        tags=["doc", "markdown", "ingested"],
        created=datetime.now(timezone.utc).isoformat(),
        updated=datetime.now(timezone.utc).isoformat(),
        source=filepath
    )
    save_knowledge_object(obj)
    return obj_id
