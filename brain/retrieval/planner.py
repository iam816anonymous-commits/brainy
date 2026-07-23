import re
from typing import List, Dict, Any, Tuple, Set
from brain.storage.models import KnowledgeObject
from brain.storage.db import list_knowledge_objects, get_knowledge_object
from brain.retrieval.intent import IntentDetector
from brain.retrieval.keyword.search import KeywordSearcher
from brain.retrieval.embedding.search import EmbeddingSearcher

class RetrievalPlanner:
    """
    Retrieval Planner decides which context retrieval strategies to invoke
    and how to blend them based on the detected query intent.
    """
    @staticmethod
    def plan_and_retrieve(
        query: str,
        project: str,
        graph_manager: Any
    ) -> Tuple[Dict[str, float], Dict[str, float], str]:
        """
        Plans retrieval and routes to specific query-dependent subsystems.
        Returns:
            - candidate_similarities: Dict[obj_id, similarity_score]
            - graph_boosts: Dict[obj_id, boost_score]
            - intent: str (The detected intent)
        """
        # 1. Detect Intent
        intent = IntentDetector.detect_intent(query)

        candidate_similarities: Dict[str, float] = {}
        graph_boosts: Dict[str, float] = {}

        # 2. Planning decisions: activate specific search modules based on intent
        # 2A. Core strategy flags
        run_keyword = True
        run_embedding = True
        run_graph_expansion = True

        # Adjust searches dynamically to save token budgets and focus queries
        if intent == "DECISION_HISTORY":
            # For decisions, we want deep keyword searches on rationales & graph lookups
            run_embedding = False
        elif intent == "TASK_STATUS":
            # For task statuses, rely heavily on direct keyword lookup and recency
            run_embedding = False
            run_graph_expansion = False

        # Execute Keyword Search
        if run_keyword:
            kw_results = KeywordSearcher.search(query, project)
            for obj, score in kw_results:
                norm_score = min(score * 2.0, 10.0)
                candidate_similarities[obj.id] = max(candidate_similarities.get(obj.id, 0.0), norm_score)

        # Execute Embedding Search
        if run_embedding:
            emb_results = EmbeddingSearcher.search(query, project)
            for obj, score in emb_results:
                norm_score = score * 10.0
                candidate_similarities[obj.id] = max(candidate_similarities.get(obj.id, 0.0), norm_score)

        # Execute Graph Neighbor Search / Expansion
        if run_graph_expansion:
            # Expand on top hits
            top_hits = sorted(candidate_similarities.items(), key=lambda x: x[1], reverse=True)[:3]
            for hit_id, _ in top_hits:
                # Direct neighbors get +3.0 boost
                neighbors_1 = graph_manager.get_related_nodes(hit_id, max_distance=1)
                for n_id in neighbors_1:
                    if n_id != hit_id:
                        graph_boosts[n_id] = max(graph_boosts.get(n_id, 0.0), 3.0)

                # 2nd-degree neighbors get +1.5 boost
                neighbors_2 = graph_manager.get_related_nodes(hit_id, max_distance=2)
                for n_id in neighbors_2:
                    if n_id != hit_id and n_id not in neighbors_1:
                        graph_boosts[n_id] = max(graph_boosts.get(n_id, 0.0), 1.5)

        return candidate_similarities, graph_boosts, intent
