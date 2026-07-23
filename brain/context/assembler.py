import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from brain.retrieval.ranking.orchestrator import RetrievalOrchestrator
from brain.compression.compressor import ContextCompressor
from brain.storage.db import get_knowledge_object
from brain.context.resource_manager import ContextResourceManager
from brain.context.trace import ContextTrace, NodeTrace, ObservabilityTraceRegistry

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
        token_budget: int = 4000
    ) -> ContextPackage:
        """
        Retrieves, ranks, compresses, and organizes project context into a standard ContextPackage JSON.
        Integrates ContextResourceManager allocation budgets and writes to ObservabilityTraceRegistry.
        """
        start_time = time.time()

        # Initialize Resource Manager & Orchestrator
        resource_mgr = ContextResourceManager(token_budget=token_budget)
        segment_limits = resource_mgr.get_segment_allocations()

        orchestrator = RetrievalOrchestrator(project=project)
        search_query = f"{user_goal} {current_task_input or ''}".strip()

        # Retrieve candidates
        candidates_with_scores = orchestrator.retrieve_and_rank(
            query=search_query,
            limit=resource_mgr.retrieval_limit
        )

        goal = user_goal
        current_task = current_task_input or ""

        working_mem_id = f"working-memory::{project.lower()}"
        working_mem = get_knowledge_object(working_mem_id)
        if working_mem and not current_task:
            current_task = working_mem.summary or working_mem.title

        # Buffer candidates temporarily
        relevant_code_candidates = []
        decisions_candidates = []
        constraints_candidates = []
        known_failures_candidates = []
        related_docs_candidates = []
        important_conversations_candidates = []
        architecture_lines = []
        recommended_actions = []

        node_traces: List[NodeTrace] = []
        detected_intent = "GENERAL"

        for obj, score, trace_metrics in candidates_with_scores:
            detected_intent = trace_metrics.get("intent", "GENERAL")
            orig_len = len(obj.content)

            payload = {
                "id": obj.id,
                "title": obj.title,
                "summary": obj.summary,
                "content": obj.content,  # keep original first for resource allocations
                "importance": obj.importance,
                "confidence": obj.confidence,
                "tags": obj.tags,
                "score": round(score, 2)
            }

            # Categorize
            if obj.type in ["Code", "Class", "Function", "Test"]:
                relevant_code_candidates.append(payload)
            elif obj.type == "Decision":
                decisions_candidates.append(payload)
            elif obj.type in ["Constraint", "Rule"]:
                constraints_candidates.append(payload)
            elif obj.type in ["Failure", "Bug", "Issue"]:
                known_failures_candidates.append(payload)
                recommended_actions.append(f"Avoid previous failure: {obj.title} - {obj.summary}")
            elif obj.type in ["Document", "Fact", "Template", "Pattern"]:
                related_docs_candidates.append(payload)
            elif obj.type == "Conversation":
                important_conversations_candidates.append(payload)
            elif obj.type == "Project":
                architecture_lines.append(f"Project: {obj.title} ({obj.summary})")

            # Log individual node trace
            node_traces.append(NodeTrace(
                id=obj.id,
                type=obj.type,
                title=obj.title,
                raw_similarity=trace_metrics.get("raw_similarity", 0.0),
                intent_boost=trace_metrics.get("intent_boost", 0.0),
                importance_boost=trace_metrics.get("importance_boost", 0.0),
                recency_boost=trace_metrics.get("recency_boost", 0.0),
                project_boost=trace_metrics.get("project_boost", 0.0),
                file_boost=trace_metrics.get("file_boost", 0.0),
                graph_boost=trace_metrics.get("graph_boost", 0.0),
                historical_success_boost=trace_metrics.get("historical_success_boost", 0.0),
                noise_penalty=trace_metrics.get("noise_penalty", 0.0),
                final_score=round(score, 2),
                is_included=False  # updated below after allocations
            ))

        # Enforce resource token budgets per segment via the Resource Manager
        relevant_code = resource_mgr.allocate_tokens_to_segment(relevant_code_candidates, segment_limits["relevant_code"])
        decisions = resource_mgr.allocate_tokens_to_segment(decisions_candidates, segment_limits["decisions"])
        constraints = resource_mgr.allocate_tokens_to_segment(constraints_candidates, segment_limits["constraints"])
        known_failures = resource_mgr.allocate_tokens_to_segment(known_failures_candidates, segment_limits["known_failures"])
        related_docs = resource_mgr.allocate_tokens_to_segment(related_docs_candidates, segment_limits["related_docs"])
        # conversations get generic default limits
        important_conversations = important_conversations_candidates[:3]

        # Update trace inclusions & calculate compression ratios
        included_ids = {
            item["id"] for item in (relevant_code + decisions + constraints + known_failures + related_docs + important_conversations)
        }

        for trace in node_traces:
            if trace.id in included_ids:
                trace.is_included = True
                # Match to the final compressed item length
                final_item = next((item for item in (relevant_code + decisions + constraints + known_failures + related_docs + important_conversations) if item["id"] == trace.id), None)
                if final_item and len(trace.title) > 0:
                    orig_len = next((len(o.content) for o, _, _ in candidates_with_scores if o.id == trace.id), 1)
                    final_len = len(final_item["content"])
                    trace.compression_ratio = round(final_len / max(1, orig_len), 3)

        recommended_actions = list(dict.fromkeys(recommended_actions))
        if not recommended_actions:
            recommended_actions.append("Follow modular project design constraints.")

        architecture = "\n".join(architecture_lines) if architecture_lines else f"Architecture for project {project}"

        package = ContextPackage(
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

        # Save complete audit trace to registry
        execution_time = (time.time() - start_time) * 1000.0
        ObservabilityTraceRegistry.record_trace(ContextTrace(
            query=search_query,
            intent=detected_intent,
            total_candidates_processed=len(candidates_with_scores),
            included_count=len(included_ids),
            execution_time_ms=round(execution_time, 2),
            traces=node_traces
        ))

        return package
