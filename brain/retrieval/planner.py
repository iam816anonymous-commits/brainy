import re
from typing import List, Dict, Any, Tuple, Set
from brain.retrieval.base import BaseRetriever
from brain.retrieval.intent import IntentDetector
from brain.retrieval.keyword.search import KeywordRetriever
from brain.retrieval.embedding.search import EmbeddingRetriever
from brain.retrieval.graph_retriever import GraphRetriever
from brain.retrieval.decision_retriever import DecisionRetriever
from brain.retrieval.failure_retriever import FailureRetriever
from brain.retrieval.recent_retriever import RecentRetriever

class RetrievalPlanner:
    """
    Retrieval Planner decides which context retrieval strategies (Retriever Plugins)
    to invoke and how to blend them based on the detected query intent.
    """
    def __init__(self):
        # Register pluggable retriever subsystems
        self.retrievers: Dict[str, BaseRetriever] = {
            "keyword": KeywordRetriever(),
            "embedding": EmbeddingRetriever(),
            "graph": GraphRetriever(),
            "decision": DecisionRetriever(),
            "failure": FailureRetriever(),
            "recent": RecentRetriever()
        }

    def plan_and_execute(
        self,
        query: str,
        project: str,
        graph_manager: Any
    ) -> Tuple[Dict[str, float], Dict[str, float], str]:
        """
        Plans retrieval and routes to specific query-dependent retriever plugins.
        Returns:
            - candidate_similarities: Dict[obj_id, similarity_score]
            - graph_boosts: Dict[obj_id, boost_score]
            - intent: str (The detected intent)
        """
        intent = IntentDetector.detect_intent(query)

        candidate_similarities: Dict[str, float] = {}
        graph_boosts: Dict[str, float] = {}

        # Decide which retrievers to activate based on detected intent
        active_retriever_keys = ["keyword", "embedding"]

        if intent == "DECISION_HISTORY":
            active_retriever_keys = ["keyword", "decision", "graph"]
        elif intent == "DEBUG_ERROR":
            active_retriever_keys = ["keyword", "failure", "recent"]
        elif intent == "TASK_STATUS":
            active_retriever_keys = ["keyword", "recent"]
        elif intent == "ARCHITECTURE":
            active_retriever_keys = ["keyword", "graph", "embedding"]

        # Execute active retrievers
        for key in active_retriever_keys:
            retriever = self.retrievers.get(key)
            if retriever:
                results = retriever.retrieve(query=query, project=project, graph_manager=graph_manager)
                for obj, score in results:
                    if key == "graph":
                        # Graph hits yield explicit dependency boosts
                        graph_boosts[obj.id] = max(graph_boosts.get(obj.id, 0.0), score)
                    else:
                        candidate_similarities[obj.id] = max(candidate_similarities.get(obj.id, 0.0), score)

        # Standard neighbor expansion if graph wasn't explicitly triggered as a core retriever
        if "graph" not in active_retriever_keys:
            top_hits = sorted(candidate_similarities.items(), key=lambda x: x[1], reverse=True)[:3]
            for hit_id, _ in top_hits:
                neighbors_1 = graph_manager.get_related_nodes(hit_id, max_distance=1)
                for n_id in neighbors_1:
                    if n_id != hit_id:
                        graph_boosts[n_id] = max(graph_boosts.get(n_id, 0.0), 3.0)

                neighbors_2 = graph_manager.get_related_nodes(hit_id, max_distance=2)
                for n_id in neighbors_2:
                    if n_id != hit_id and n_id not in neighbors_1:
                        graph_boosts[n_id] = max(graph_boosts.get(n_id, 0.0), 1.5)

        return candidate_similarities, graph_boosts, intent

    # Maintain backwards compatibility for static/classmethod usages
    @classmethod
    def plan_and_retrieve(cls, query: str, project: str, graph_manager: Any) -> Tuple[Dict[str, float], Dict[str, float], str]:
        planner = cls()
        return planner.plan_and_execute(query, project, graph_manager)
