from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from brain.storage.models import KnowledgeObject
from brain.storage.db import save_knowledge_object, get_knowledge_object, list_knowledge_objects

def remember_working_memory(
    project: str,
    current_task: str,
    active_files: List[str] = [],
    branch: str = "main",
    current_errors: List[str] = []
) -> str:
    """
    Saves or updates Working Memory (active context).
    Type: 'Task' or custom type representing working state.
    """
    obj_id = f"working-memory::{project.lower()}"

    content_lines = [
        f"Active Task: {current_task}",
        f"Active Files: {', '.join(active_files)}",
        f"Git Branch: {branch}",
        f"Current Errors: {', '.join(current_errors)}"
    ]
    content = "\n".join(content_lines)

    obj = KnowledgeObject(
        id=obj_id,
        type="Task",  # Mapped to unified schema
        project=project,
        title="Active Working Memory Context",
        summary=f"Current active task: {current_task}",
        content=content,
        importance=8.0,  # very high importance for working memory!
        confidence=1.0,
        tags=["working-memory", "active-state"],
        created=datetime.now(timezone.utc).isoformat(),
        updated=datetime.now(timezone.utc).isoformat(),
        source="system/working-memory"
    )
    save_knowledge_object(obj)
    return obj_id

def remember_episodic_memory(
    project: str,
    action: str,
    outcome: str,
    reason: str,
    timestamp: Optional[str] = None
) -> str:
    """
    Saves an episodic memory entry (event history).
    Type: 'Meeting' or custom episodic record. Let's use 'Meeting' or 'Workflow' as standard unified types.
    """
    # Use timestamp as unique identifier part
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    clean_ts = ts.replace(":", "-").replace(".", "-")
    obj_id = f"episodic::{project.lower()}::{clean_ts}"

    content = f"Action Taken: {action}\nOutcome: {outcome}\nReason/Details: {reason}"

    obj = KnowledgeObject(
        id=obj_id,
        type="Workflow",  # Standard unified type representing an episode/flow
        project=project,
        title=f"History Episode: {action}",
        summary=f"Action: {action} -> Outcome: {outcome}",
        content=content,
        importance=5.0,
        confidence=1.0,
        tags=["episodic", "history", "outcome"],
        created=ts,
        updated=datetime.now(timezone.utc).isoformat(),
        source="system/episodic"
    )
    save_knowledge_object(obj)
    return obj_id

def remember_semantic_relation(
    project: str,
    concept_a: str,
    relation: str,
    concept_b: str
) -> None:
    """
    Saves or links concepts semantically.
    """
    # Verify/create source concept
    id_a = f"concept::{project.lower()}::{concept_a.lower().replace(' ', '_')}"
    id_b = f"concept::{project.lower()}::{concept_b.lower().replace(' ', '_')}"

    obj_a = get_knowledge_object(id_a)
    if not obj_a:
        obj_a = KnowledgeObject(
            id=id_a,
            type="Fact",
            project=project,
            title=concept_a,
            summary=f"Semantic concept: {concept_a}",
            content=f"Semantic entity: {concept_a}",
            importance=4.0,
            relations=[]
        )

    obj_b = get_knowledge_object(id_b)
    if not obj_b:
        obj_b = KnowledgeObject(
            id=id_b,
            type="Fact",
            project=project,
            title=concept_b,
            summary=f"Semantic concept: {concept_b}",
            content=f"Semantic entity: {concept_b}",
            importance=4.0,
            relations=[]
        )
        save_knowledge_object(obj_b)

    # Append relationship to concept A
    existing_targets = [r["target"] for r in obj_a.relations]
    if id_b not in existing_targets:
        obj_a.relations.append({"target": id_b, "type": relation})

    save_knowledge_object(obj_a)

def remember_decision(
    project: str,
    decision_title: str,
    reason: str,
    alternatives: str = "",
    status: str = "approved"
) -> str:
    """
    Saves a Decision Memory entry.
    Type: 'Decision'.
    """
    clean_title = decision_title.lower().replace(" ", "_")[:30]
    obj_id = f"decision::{project.lower()}::{clean_title}"

    content = f"Decision: {decision_title}\nStatus: {status}\nReason/Constraint: {reason}"
    if alternatives:
        content += f"\nAlternatives Considered: {alternatives}"

    obj = KnowledgeObject(
        id=obj_id,
        type="Decision",  # Standard unified type
        project=project,
        title=f"Decision: {decision_title}",
        summary=reason[:150] + "..." if len(reason) > 150 else reason,
        content=content,
        importance=7.0,
        confidence=1.0,
        tags=["decision", status],
        created=datetime.now(timezone.utc).isoformat(),
        updated=datetime.now(timezone.utc).isoformat(),
        source="system/decision"
    )
    save_knowledge_object(obj)
    return obj_id

def remember_failure(
    project: str,
    attempted_action: str,
    reason_for_failure: str,
    resolution_or_lessons: str = ""
) -> str:
    """
    Saves a Failure Memory entry.
    Type: 'Failure'.
    """
    clean_action = attempted_action.lower().replace(" ", "_")[:30]
    obj_id = f"failure::{project.lower()}::{clean_action}"

    content = f"Attempted Action: {attempted_action}\nFailure Reason: {reason_for_failure}"
    if resolution_or_lessons:
        content += f"\nLessons/Resolution: {resolution_or_lessons}"

    obj = KnowledgeObject(
        id=obj_id,
        type="Failure",  # Standard unified type
        project=project,
        title=f"Failure: {attempted_action}",
        summary=reason_for_failure[:150] + "..." if len(reason_for_failure) > 150 else reason_for_failure,
        content=content,
        importance=8.0,  # failures are highly valuable to avoid repeats!
        confidence=1.0,
        tags=["failure", "lessons-learned"],
        created=datetime.now(timezone.utc).isoformat(),
        updated=datetime.now(timezone.utc).isoformat(),
        source="system/failure"
    )
    save_knowledge_object(obj)
    return obj_id

def remember_pattern(
    project: str,
    pattern_name: str,
    steps: List[str],
    description: str = ""
) -> str:
    """
    Saves a Pattern Memory entry.
    Type: 'Pattern'.
    """
    clean_name = pattern_name.lower().replace(" ", "_")[:30]
    obj_id = f"pattern::{project.lower()}::{clean_name}"

    steps_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
    content = f"Pattern Name: {pattern_name}\nDescription: {description}\n\nSteps:\n{steps_str}"

    obj = KnowledgeObject(
        id=obj_id,
        type="Pattern",  # Standard unified type
        project=project,
        title=f"Pattern: {pattern_name}",
        summary=description or f"Process workflow pattern: {pattern_name}",
        content=content,
        importance=6.0,
        confidence=1.0,
        tags=["pattern", "workflow", "reusable"],
        created=datetime.now(timezone.utc).isoformat(),
        updated=datetime.now(timezone.utc).isoformat(),
        source="system/pattern"
    )
    save_knowledge_object(obj)
    return obj_id
