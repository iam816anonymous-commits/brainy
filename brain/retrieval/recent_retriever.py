from typing import List, Tuple
from brain.retrieval.base import BaseRetriever
from brain.core.models import KnowledgeObject
from brain.core.db import list_knowledge_objects

class RecentRetriever(BaseRetriever):
    def get_name(self) -> str:
        return "recent_retriever"

    def retrieve(self, query: str, project: str, **kwargs) -> List[Tuple[KnowledgeObject, float]]:
        objs = list_knowledge_objects(project=project)
        objs.sort(key=lambda x: x.updated or "", reverse=True)

        results = []
        for idx, obj in enumerate(objs[:5]):
            score = 10.0 - (idx * 1.5)
            results.append((obj, score))

        return results
