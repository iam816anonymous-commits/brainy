from abc import ABC, abstractmethod
from typing import List, Tuple, Any
from brain.core.models import KnowledgeObject

class BaseRetriever(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the unique identifier name of this retriever plugin.
        """
        pass

    @abstractmethod
    def retrieve(self, query: str, project: str, **kwargs) -> List[Tuple[KnowledgeObject, float]]:
        """
        Executes query retrieval. Returns a list of (KnowledgeObject, similarity_score_0_to_10).
        """
        pass
