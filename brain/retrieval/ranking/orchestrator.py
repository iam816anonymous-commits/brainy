import os
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Set, Optional
from brain.storage.models import KnowledgeObject
from brain.storage.db import list_knowledge_objects, get_knowledge_object
from brain.graph.graph_manager import KnowledgeGraphManager
from brain.retrieval.intent import IntentDetector
from brain.retrieval.keyword.search import KeywordSearcher
from brain.retrieval.embedding.search import EmbeddingSearcher

class RetrievalOrchestrator:
    def __init__(self, project: str):
        self.project = project
        self.graph_manager = KnowledgeGraphManager(project_name=project)

    def retrieve_and_rank(self, query: str, limit: int = 10) -> List[Tuple[KnowledgeObject, float]]:
        """
        Retrieves relevant context using the multi-stage pipeline:
        1. Detect intent
        2. Perform keyword search
        3. Perform embedding search
        4. Expand via Knowledge Graph neighbors
        5. Apply Unified Context Ranking Formula to all candidates
        """
        # Ensure graph is fresh
        self.graph_manager.build_graph()

        # 1. Intent Detection
        intent = IntentDetector.detect_intent(query)

        # 2. Collect Candidates & Semantic similarity scores
        # Map obj_id -> highest similarity score found
        candidate_similarities: Dict[str, float] = {}

        keyword_results = KeywordSearcher.search(query, self.project)
        for obj, score in keyword_results:
            # Normalize keyword score to a reasonable 0-10 scale
            norm_score = min(score * 2.0, 10.0)
            candidate_similarities[obj.id] = max(candidate_similarities.get(obj.id, 0.0), norm_score)

        embedding_results = EmbeddingSearcher.search(query, self.project)
        for obj, score in embedding_results:
            # Cosine similarity is usually 0.0 - 1.0, scale up to 0-10
            norm_score = score * 10.0
            candidate_similarities[obj.id] = max(candidate_similarities.get(obj.id, 0.0), norm_score)

        # 3. Knowledge Graph Expansion
        # Find neighbors of our top similarity hits (say, top 3 hits)
        top_hits = sorted(candidate_similarities.items(), key=lambda x: x[1], reverse=True)[:3]
        graph_boosts: Dict[str, float] = {}

        for hit_id, _ in top_hits:
            # 1-step neighbors get a dependency distance boost
            neighbors_1 = self.graph_manager.get_related_nodes(hit_id, max_distance=1)
            for n_id in neighbors_1:
                if n_id != hit_id:
                    graph_boosts[n_id] = max(graph_boosts.get(n_id, 0.0), 3.0)  # +3.0 boost for direct neighbor

            # 2-step neighbors get a smaller boost
            neighbors_2 = self.graph_manager.get_related_nodes(hit_id, max_distance=2)
            for n_id in neighbors_2:
                if n_id != hit_id and n_id not in neighbors_1:
                    graph_boosts[n_id] = max(graph_boosts.get(n_id, 0.0), 1.5)  # +1.5 boost for 2nd degree neighbor

        # Collect all candidates (all matched + all graph-expanded)
        candidate_ids = set(candidate_similarities.keys()) | set(graph_boosts.keys())

        # If no search matches, fallback to returning recent project objects
        if not candidate_ids:
            all_objs = list_knowledge_objects(project=self.project)
            candidate_ids = {obj.id for obj in all_objs[:15]}

        # 4. Rank Candidates
        ranked_candidates: List[Tuple[KnowledgeObject, float]] = []

        # Helper to extract file names/class names from query for direct matching
        query_words = set(re.findall(r"\w+", query.lower()))

        for cid in candidate_ids:
            obj = get_knowledge_object(cid)
            if not obj:
                continue

            # --- Unified Context Ranking Formula ---
            # Score = Similarity + Importance + Recency + Project Match + File Match + Dependency Distance - Noise

            # A. Similarity (0 to 10)
            similarity_score = candidate_similarities.get(cid, 0.0)

            # B. Importance (0 to 10)
            importance_score = obj.importance

            # C. Recency (0 to 3)
            recency_score = 0.0
            if obj.created:
                try:
                    created_dt = datetime.fromisoformat(obj.created)
                    # Calculate difference in hours
                    now = datetime.now(timezone.utc)
                    if created_dt.tzinfo is None:
                        created_dt = created_dt.replace(tzinfo=timezone.utc)
                    delta_hours = (now - created_dt).total_seconds() / 3600.0
                    # Decay formula: boost up to 3.0, decays over time
                    recency_score = max(0.0, 3.0 / (1.0 + (delta_hours / 24.0)))  # decays over days
                except Exception:
                    pass

            # D. Project Match (+5.0)
            project_match = 5.0 if obj.project.lower() == self.project.lower() else 0.0

            # E. File/Entity Match (+5.0)
            file_match = 0.0
            title_words = set(re.findall(r"\w+", obj.title.lower()))
            if query_words & title_words:
                file_match = 5.0

            # F. Dependency Distance (from Graph neighbor boosts)
            dependency_boost = graph_boosts.get(cid, 0.0)

            # G. Intent Boost (If intent matches object type)
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

            # H. Historical Success (e.g. tag high confidence)
            historical_success = obj.confidence * 2.0  # up to 2.0

            # I. Noise (Penalty)
            noise_penalty = 0.0
            if "deprecated" in obj.tags or "old" in obj.tags:
                noise_penalty = 5.0
            if obj.title.startswith("."):
                noise_penalty = 3.0

            # Calculate final total score
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

            ranked_candidates.append((obj, final_score))

        # Sort candidates by final score descending
        ranked_candidates.sort(key=lambda x: x[1], reverse=True)
        return ranked_candidates[:limit]
