import math
import re
from typing import List, Tuple
from brain.storage.models import KnowledgeObject
from brain.storage.db import list_knowledge_objects

def tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())

class KeywordSearcher:
    @staticmethod
    def search(query: str, project: str) -> List[Tuple[KnowledgeObject, float]]:
        """
        Calculates simple term overlap / TF-IDF score for all knowledge objects in the project.
        Returns a list of (KnowledgeObject, score).
        """
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        objs = list_knowledge_objects(project=project)
        scored_objs = []

        # Simple TF-IDF/BM25 style matching
        for obj in objs:
            text = f"{obj.title} {obj.summary} {obj.content} {' '.join(obj.tags)}".lower()
            score = 0.0

            for token in query_tokens:
                count = text.count(token)
                if count > 0:
                    # Title matches should be heavily weighted
                    title_count = obj.title.lower().count(token)
                    tag_count = sum(1 for tag in obj.tags if token in tag.lower())

                    term_score = math.log1p(count)
                    if title_count > 0:
                        term_score += 3.0 * math.log1p(title_count)
                    if tag_count > 0:
                        term_score += 2.0

                    score += term_score

            if score > 0.0:
                scored_objs.append((obj, score))

        # Sort by score descending
        scored_objs.sort(key=lambda x: x[1], reverse=True)
        return scored_objs
