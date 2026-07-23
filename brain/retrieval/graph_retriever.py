from typing import List, Tuple, Any
from brain.retrieval.base import BaseRetriever
from brain.storage.models import KnowledgeObject
from brain.storage.db import get_knowledge_object, list_knowledge_objects

class GraphRetriever(BaseRetriever):
    def get_name(self) -> str:
        return "graph_retriever"

    def retrieve(self, query: str, project: str, **kwargs) -> List[Tuple[KnowledgeObject, float]]:
        """
        Retrieved nodes linked within the knowledge graph.
        Specifically handles finding connected node concepts of key query matches.
        """
        graph_manager = kwargs.get("graph_manager")
        if not graph_manager:
            return []

        objs = list_knowledge_objects(project=project)
        results = []

        # Traverse graph nodes that match simple query token overlap
        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        for obj in objs:
            matched = any(term in obj.title.lower() or term in obj.summary.lower() for term in query_terms)
            if matched:
                # Find connected neighbors
                neighbors = graph_manager.get_related_nodes(obj.id, max_distance=1)
                for n_id in neighbors:
                    neighbor_obj = get_knowledge_object(n_id)
                    if neighbor_obj:
                        # Direct hits get higher weight than distant neighbors
                        score = 8.0 if n_id == obj.id else 4.0
                        results.append((neighbor_obj, score))

        return results
