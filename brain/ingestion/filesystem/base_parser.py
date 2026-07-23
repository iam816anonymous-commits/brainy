from abc import ABC, abstractmethod
from typing import List
from brain.storage.models import KnowledgeObject

class BaseParser(ABC):
    @abstractmethod
    def can_parse(self, filepath: str) -> bool:
        """
        Returns True if this parser can handle the given file extension/path.
        """
        pass

    @abstractmethod
    def parse(self, filepath: str, project_name: str, parent_id: str) -> List[KnowledgeObject]:
        """
        Parses the file and extracts hierarchical child KnowledgeObjects (Classes, Functions, Tests, etc.).
        """
        pass
