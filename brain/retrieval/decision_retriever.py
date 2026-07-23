from typing import List, Tuple
from brain.retrieval.base import BaseRetriever
from brain.storage.models import KnowledgeObject
from brain.storage.db import list_knowledge_objects

class DecisionRetriever(BaseRetriever):
    def get_name(self) -> str:
        return "decision_retriever"

    def retrieve(self, query: str, project: str, **kwargs) -> List[Tuple[KnowledgeObject, float]]:
        """
        Retrieves matching Decision type KnowledgeObjects from Structured Storage.
        """
        decisions = list_knowledge_objects(project=project, obj_type="Decision")
        results = []

        query_words = set(query.lower().split())
        for d in decisions:
            text = f"{d.title} {d.summary} {d.content}".lower()
            # Score matches based on term frequency
            match_count = sum(1 for w in query_words if w in text)
            if match_count > 0:
                score = min(match_count * 2.0, 10.0)
                results.append((d, score))

        return results
