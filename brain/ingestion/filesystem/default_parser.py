import os
from typing import List
from brain.ingestion.filesystem.base_parser import BaseParser
from brain.core.models import KnowledgeObject

class DefaultParser(BaseParser):
    def can_parse(self, filepath: str) -> bool:
        return True

    def parse(self, filepath: str, project_name: str, parent_id: str) -> List[KnowledgeObject]:
        return []
