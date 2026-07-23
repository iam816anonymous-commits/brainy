import uuid
from datetime import datetime, timezone
from typing import List, Optional
from brain.core.models import KnowledgeObject
from brain.core.db import save_knowledge_object

def ingest_scraped_page(
    url: str,
    title: str,
    html_content: str,
    text_content: str,
    project_name: str,
    tags: List[str] = []
) -> str:
    """
    Ingests a browser webpage as a 'Document' KnowledgeObject.
    """
    obj_id = f"browser::{project_name.lower()}::{str(uuid.uuid4())[:8]}"
    summary = text_content[:200] + "..." if len(text_content) > 200 else text_content

    obj = KnowledgeObject(
        id=obj_id,
        type="Document",
        project=project_name,
        title=title or f"Webpage: {url}",
        summary=summary,
        content=text_content,
        importance=3.0,
        confidence=0.8,
        tags=tags + ["browser", "web-scrape"],
        created=datetime.now(timezone.utc).isoformat(),
        updated=datetime.now(timezone.utc).isoformat(),
        source=url
    )
    save_knowledge_object(obj)
    return obj_id
