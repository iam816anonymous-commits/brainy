import os
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Set, Optional
from brain.storage.models import KnowledgeObject
from brain.storage.db import list_knowledge_objects, get_knowledge_object
from brain.graph.graph_manager import KnowledgeGraphManager
from brain.retrieval.planner import RetrievalPlanner

class RetrievalOrchestrator:
    def __init__(self, project: str):
        self.project = project
        self.graph_manager = KnowledgeGraphManager(project_name=project)

    def retrieve_and_rank(self, query: str, limit: int = 10) -> List[Tuple[KnowledgeObject, float, Dict[str, float]]]:
        """
        Retrieves relevant context using the Retrieval Planner and ranks candidates.
        Returns:
            List of (KnowledgeObject, final_score, trace_metrics_dictionary)
        """
        # Ensure graph is fresh
        self.graph_manager.build_graph()

        # 1. Delegate retrieval planning and execution to the RetrievalPlanner
        candidate_similarities, graph_boosts, intent = RetrievalPlanner.plan_and_retrieve(
            query=query,
            project=self.project,
            graph_manager=self.graph_manager
        )

        # Collect candidates
        candidate_ids = set(candidate_similarities.keys()) | set(graph_boosts.keys())

        # If no candidates, fallback to recent items
        if not candidate_ids:
            all_objs = list_knowledge_objects(project=self.project)
            candidate_ids = {obj.id for obj in all_objs[:15]}

        ranked_candidates: List[Tuple[KnowledgeObject, float, Dict[str, float]]] = []
        query_words = set(re.findall(r"\w+", query.lower()))

        for cid in candidate_ids:
            obj = get_knowledge_object(cid)
            if not obj:
                continue

            # Unified Context Ranking Formula
            similarity_score = candidate_similarities.get(cid, 0.0)
            importance_score = obj.importance

            recency_score = 0.0
            if obj.created:
                try:
                    created_dt = datetime.fromisoformat(obj.created)
                    now = datetime.now(timezone.utc)
                    if created_dt.tzinfo is None:
                        created_dt = created_dt.replace(tzinfo=timezone.utc)
                    delta_hours = (now - created_dt).total_seconds() / 3600.0
                    recency_score = max(0.0, 3.0 / (1.0 + (delta_hours / 24.0)))
                except Exception:
                    pass

            project_match = 5.0 if obj.project.lower() == self.project.lower() else 0.0

            file_match = 0.0
            title_words = set(re.findall(r"\w+", obj.title.lower()))
            if query_words & title_words:
                file_match = 5.0

            dependency_boost = graph_boosts.get(cid, 0.0)

            intent_boost = 0.0
            if intent == "DEBUG_ERROR" and obj.type in ["Bug", "Issue", "Failure"]:
                intent_boost = 6.0
            elif intent == "DECISION_HISTORY" and obj.type == "Decision":
                intent_boost = 6.0
            elif intent == "TASK_STATUS" and obj.type == "Task":
                intent_boost = 6.0
            elif intent == "ARCHITECTURE" and obj.type in ["Class", "Folder", "Architecture"]:
                intent_boost = 6.0
            elif intent == "CODE_SEARCH" and obj.type in ["Code", "Function", "Class"]:
                intent_boost = 6.0

            historical_success = obj.confidence * 2.0

            noise_penalty = 0.0
            if "deprecated" in obj.tags or "old" in obj.tags:
                noise_penalty = 5.0
            if obj.title.startswith("."):
                noise_penalty = 3.0

            final_score = (
                similarity_score +
                importance_score +
                recency_score +
                project_match +
                file_match +
                dependency_boost +
                intent_boost +
                historical_success -
                noise_penalty
            )

            trace_metrics = {
                "raw_similarity": similarity_score,
                "importance_boost": importance_score,
                "recency_boost": recency_score,
                "project_boost": project_match,
                "file_boost": file_match,
                "graph_boost": dependency_boost,
                "intent_boost": intent_boost,
                "historical_success_boost": historical_success,
                "noise_penalty": noise_penalty,
                "intent": intent
            }

            ranked_candidates.append((obj, final_score, trace_metrics))

        ranked_candidates.sort(key=lambda x: x[1], reverse=True)
        return ranked_candidates[:limit]
