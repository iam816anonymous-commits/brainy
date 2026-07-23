from abc import ABC, abstractmethod
from typing import List
from brain.core.models import KnowledgeObject

class BaseParser(ABC):
    @abstractmethod
    def can_parse(self, filepath: str) -> bool:
        pass

    @abstractmethod
    def parse(self, filepath: str, project_name: str, parent_id: str) -> List[KnowledgeObject]:
        pass
