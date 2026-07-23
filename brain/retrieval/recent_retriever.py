from typing import List, Tuple
from brain.retrieval.base import BaseRetriever
from brain.storage.models import KnowledgeObject
from brain.storage.db import list_knowledge_objects

class RecentRetriever(BaseRetriever):
    def get_name(self) -> str:
        return "recent_retriever"

    def retrieve(self, query: str, project: str, **kwargs) -> List[Tuple[KnowledgeObject, float]]:
        """
        Retrieves recent events/actions chronologically based on recency.
        """
        objs = list_knowledge_objects(project=project)
        # Sort by updated date
        objs.sort(key=lambda x: x.updated or "", reverse=True)

        results = []
        # Return top 5 most recently created/updated items with score descending
        for idx, obj in enumerate(objs[:5]):
            score = 10.0 - (idx * 1.5)
            results.append((obj, score))

        return results
