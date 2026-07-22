from datetime import datetime, timezone
import json
from typing import List, Dict, Any, Optional
from brain.storage.models import KnowledgeObject
from brain.storage.db import save_knowledge_object

def ingest_chat_session(
    session_id: str,
    project_name: str,
    title: str,
    messages: List[Dict[str, str]],  # List of {"role": "user"|"assistant", "content": str}
    summary: Optional[str] = None
) -> str:
    """
    Ingests a complete chat conversation transcript as a 'Conversation' KnowledgeObject.
    """
    obj_id = f"conversation::{project_name}::{session_id}"

    # Generate content representation
    transcript = ""
    for msg in messages:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        transcript += f"[{role}]: {content}\n\n"

    if not summary:
        # Fallback to a preview of the first message
        user_msgs = [m.get("content", "") for m in messages if m.get("role") == "user"]
        summary = f"Chat session containing {len(messages)} messages."
        if user_msgs:
            first_user = user_msgs[0]
            summary += f" First user query: {first_user[:100]}..."

    obj = KnowledgeObject(
        id=obj_id,
        type="Conversation",
        project=project_name,
        title=title or f"Conversation Session {session_id}",
        summary=summary,
        content=transcript,
        importance=6.0,  # conversations capture active intent and user guidance!
        confidence=1.0,
        tags=["chat", "transcript", "interaction"],
        created=datetime.now(timezone.utc).isoformat(),
        updated=datetime.now(timezone.utc).isoformat(),
        source=f"client/chat/{session_id}"
    )
    save_knowledge_object(obj)
    return obj_id
