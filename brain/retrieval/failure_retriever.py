from typing import List, Tuple
from brain.retrieval.base import BaseRetriever
from brain.storage.models import KnowledgeObject
from brain.storage.db import list_knowledge_objects

class FailureRetriever(BaseRetriever):
    def get_name(self) -> str:
        return "failure_retriever"

    def retrieve(self, query: str, project: str, **kwargs) -> List[Tuple[KnowledgeObject, float]]:
        """
        Retrieves matching Failure/Bug/Issue type KnowledgeObjects from Structured Storage.
        """
        failures = list_knowledge_objects(project=project)
        results = []

        failure_types = {"Failure", "Bug", "Issue"}
        query_words = set(query.lower().split())

        for f in failures:
            if f.type in failure_types:
                text = f"{f.title} {f.summary} {f.content}".lower()
                match_count = sum(1 for w in query_words if w in text)
                if match_count > 0:
                    score = min(match_count * 2.0, 10.0)
                    results.append((f, score))

        return results
