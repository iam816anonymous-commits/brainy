from typing import List, Tuple
from brain.retrieval.base import BaseRetriever
from brain.core.models import KnowledgeObject
from brain.core.db import list_knowledge_objects

class DecisionRetriever(BaseRetriever):
    def get_name(self) -> str:
        return "decision_retriever"

    def retrieve(self, query: str, project: str, **kwargs) -> List[Tuple[KnowledgeObject, float]]:
        decisions = list_knowledge_objects(project=project, obj_type="Decision")
        results = []

        query_words = set(query.lower().split())
        for d in decisions:
            text = f"{d.title} {d.summary} {d.content}".lower()
            match_count = sum(1 for w in query_words if w in text)
            if match_count > 0:
                score = min(match_count * 2.0, 10.0)
                results.append((d, score))

        return results
