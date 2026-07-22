from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from brain.retrieval.ranking.orchestrator import RetrievalOrchestrator
from brain.compression.compressor import ContextCompressor
from brain.storage.db import get_knowledge_object

class ContextPackage(BaseModel):
    goal: str = ""
    project: str = ""
    current_task: str = ""
    architecture: str = ""
    relevant_code: List[Dict[str, Any]] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    constraints: List[Dict[str, Any]] = Field(default_factory=list)
    known_failures: List[Dict[str, Any]] = Field(default_factory=list)
    related_docs: List[Dict[str, Any]] = Field(default_factory=list)
    important_conversations: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)

class ContextAssembler:
    @staticmethod
    def assemble_package(
        project: str,
        user_goal: str,
        current_task_input: Optional[str] = None,
        limit_per_type: int = 5
    ) -> ContextPackage:
        """
        Retrieves, ranks, compresses, and organizes project context into a standard ContextPackage JSON.
        """
        # Initialize orchestrator
        orchestrator = RetrievalOrchestrator(project=project)

        # We search with a blend of user_goal + current_task_input to fetch optimal candidates
        search_query = f"{user_goal} {current_task_input or ''}".strip()
        candidates_with_scores = orchestrator.retrieve_and_rank(search_query, limit=25)

        # Prepare package fields
        goal = user_goal
        current_task = current_task_input or ""

        # If current_task is not provided, look up Working Memory (type: Task)
        working_mem_id = f"working-memory::{project.lower()}"
        working_mem = get_knowledge_object(working_mem_id)
        if working_mem:
            if not current_task:
                current_task = working_mem.summary or working_mem.title

        # Group retrieved candidates into standard package fields
        relevant_code = []
        decisions = []
        constraints = []
        known_failures = []
        related_docs = []
        important_conversations = []
        architecture_lines = []
        recommended_actions = []

        for obj, score in candidates_with_scores:
            # Compress long content to preserve context window (limit to 200 tokens ~800 chars)
            compressed_content = ContextCompressor.compress_content(obj.content, max_tokens=200)

            payload = {
                "id": obj.id,
                "title": obj.title,
                "summary": obj.summary,
                "content": compressed_content,
                "importance": obj.importance,
                "confidence": obj.confidence,
                "tags": obj.tags,
                "score": round(score, 2)
            }

            # Map into the standard package attributes based on unified types
            if obj.type in ["Code", "Class", "Function", "Test"]:
                relevant_code.append(payload)
            elif obj.type == "Decision":
                decisions.append(payload)
            elif obj.type in ["Constraint", "Rule"]:
                constraints.append(payload)
            elif obj.type in ["Failure", "Bug", "Issue"]:
                known_failures.append(payload)
                # Auto-generate dynamic recommendations from failure reasons!
                recommended_actions.append(f"Avoid previous failure: {obj.title} - {obj.summary}")
            elif obj.type in ["Document", "Fact", "Template", "Pattern"]:
                related_docs.append(payload)
            elif obj.type == "Conversation":
                important_conversations.append(payload)
            elif obj.type == "Project":
                architecture_lines.append(f"Project: {obj.title} ({obj.summary})")

        # Limit quantities per block to respect context sizes
        relevant_code = relevant_code[:limit_per_type]
        decisions = decisions[:limit_per_type]
        constraints = constraints[:limit_per_type]
        known_failures = known_failures[:limit_per_type]
        related_docs = related_docs[:limit_per_type]
        important_conversations = important_conversations[:limit_per_type]

        # Deduplicate recommended actions
        recommended_actions = list(dict.fromkeys(recommended_actions))
        if not recommended_actions:
            recommended_actions.append("Follow modular project design constraints.")

        # Compile static architecture overview from project summary
        architecture = "\n".join(architecture_lines) if architecture_lines else f"Architecture for project {project}"

        return ContextPackage(
            goal=goal,
            project=project,
            current_task=current_task,
            architecture=architecture,
            relevant_code=relevant_code,
            decisions=decisions,
            constraints=constraints,
            known_failures=known_failures,
            related_docs=related_docs,
            important_conversations=important_conversations,
            recommended_actions=recommended_actions
        )
