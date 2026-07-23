import os
import math
from typing import List, Tuple, Optional
import numpy as np
import requests
from brain.retrieval.base import BaseRetriever
from brain.core.models import KnowledgeObject
from brain.core.db import list_knowledge_objects

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

class LocalVectorSimilarity:
    @staticmethod
    def compute_similarity(query: str, objs: List[KnowledgeObject]) -> List[Tuple[KnowledgeObject, float]]:
        if not objs:
            return []

        def tokenize(text: str) -> List[str]:
            return [w for w in text.lower().split() if len(w) > 2]

        vocab = set(tokenize(query))
        doc_tokens = []
        for obj in objs:
            text = f"{obj.title} {obj.summary} {obj.content} {' '.join(obj.tags)}"
            tokens = tokenize(text)
            vocab.update(tokens)
            doc_tokens.append(tokens)

        vocab = sorted(list(vocab))
        vocab_index = {w: i for i, w in enumerate(vocab)}

        N = len(objs) + 1
        df = {w: 0 for w in vocab}
        for w in set(tokenize(query)):
            if w in df:
                df[w] += 1
        for tokens in doc_tokens:
            for w in set(tokens):
                if w in df:
                    df[w] += 1

        idf = {w: math.log(N / (df[w] + 1)) + 1.0 for w in vocab}

        def get_tfidf_vector(tokens: List[str]) -> np.ndarray:
            vec = np.zeros(len(vocab))
            tf = {}
            for w in tokens:
                tf[w] = tf.get(w, 0) + 1
            for w, val in tf.items():
                if w in vocab_index:
                    vec[vocab_index[w]] = val * idf[w]
            return vec

        query_vec = get_tfidf_vector(tokenize(query))

        results = []
        for i, obj in enumerate(objs):
            doc_vec = get_tfidf_vector(doc_tokens[i])
            sim = cosine_similarity(query_vec, doc_vec)
            if sim > 0:
                results.append((obj, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

class EmbeddingRetriever(BaseRetriever):
    def get_name(self) -> str:
        return "embedding_retriever"

    @staticmethod
    def get_openai_embedding(text: str, api_key: str) -> Optional[List[float]]:
        try:
            url = "https://api.openai.com/v1/embeddings"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "input": text[:8000],
                "model": "text-embedding-3-small"
            }
            resp = requests.post(url, json=data, headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.json()["data"][0]["embedding"]
        except Exception:
            pass
        return None

    def retrieve(self, query: str, project: str, **kwargs) -> List[Tuple[KnowledgeObject, float]]:
        objs = list_knowledge_objects(project=project)
        if not objs:
            return []

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return [(obj, sim * 10.0) for obj, sim in LocalVectorSimilarity.compute_similarity(query, objs)]

        query_emb = self.get_openai_embedding(query, api_key)
        if not query_emb:
            return [(obj, sim * 10.0) for obj, sim in LocalVectorSimilarity.compute_similarity(query, objs)]

        return [(obj, sim * 10.0) for obj, sim in LocalVectorSimilarity.compute_similarity(query, objs)]

class EmbeddingSearcher:
    @classmethod
    def search(cls, query: str, project: str) -> List[Tuple[KnowledgeObject, float]]:
        retriever = EmbeddingRetriever()
        return [(obj, score / 10.0) for obj, score in retriever.retrieve(query, project)]
