import math
import re
from typing import List, Tuple
from brain.retrieval.base import BaseRetriever
from brain.storage.models import KnowledgeObject
from brain.storage.db import list_knowledge_objects

def tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())

class KeywordRetriever(BaseRetriever):
    def get_name(self) -> str:
        return "keyword_retriever"

    def retrieve(self, query: str, project: str, **kwargs) -> List[Tuple[KnowledgeObject, float]]:
        """
        Calculates simple term overlap / TF-IDF score for all knowledge objects in the project.
        Returns a list of (KnowledgeObject, score).
        """
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        objs = list_knowledge_objects(project=project)
        scored_objs = []

        for obj in objs:
            text = f"{obj.title} {obj.summary} {obj.content} {' '.join(obj.tags)}".lower()
            score = 0.0

            for token in query_tokens:
                count = text.count(token)
                if count > 0:
                    title_count = obj.title.lower().count(token)
                    tag_count = sum(1 for tag in obj.tags if token in tag.lower())

                    term_score = math.log1p(count)
                    if title_count > 0:
                        term_score += 3.0 * math.log1p(title_count)
                    if tag_count > 0:
                        term_score += 2.0

                    score += term_score

            if score > 0.0:
                # Normalize keyword score to a reasonable 0-10 scale
                norm_score = min(score * 2.0, 10.0)
                scored_objs.append((obj, norm_score))

        scored_objs.sort(key=lambda x: x[1], reverse=True)
        return scored_objs

class KeywordSearcher:
    # Maintain backwards compatibility helper
    @staticmethod
    def search(query: str, project: str) -> List[Tuple[KnowledgeObject, float]]:
        retriever = KeywordRetriever()
        # Scale back to original unnormalized score for compatibility if needed,
        # but returning normalized is actually safer!
        return [(obj, score / 2.0) for obj, score in retriever.retrieve(query, project)]
