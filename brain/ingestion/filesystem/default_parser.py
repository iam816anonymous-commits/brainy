import os
from typing import List
from brain.ingestion.filesystem.base_parser import BaseParser
from brain.storage.models import KnowledgeObject

class DefaultParser(BaseParser):
    def can_parse(self, filepath: str) -> bool:
        # Falls back to handle any file
        return True

    def parse(self, filepath: str, project_name: str, parent_id: str) -> List[KnowledgeObject]:
        """
        Default parser that processes standard documents without deep inner AST syntax mapping.
        """
        # We don't extract nested entities inside default files, we just read them as top-level contents.
        return []
