import re
from typing import List, Dict, Any

class ContextCompressor:
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Quick approximate token estimation (typically ~4 characters per token).
        """
        return int(len(text) / 4)

    @classmethod
    def compress_content(cls, content: str, max_tokens: int = 150) -> str:
        """
        Compresses content down to fit within a token limit.
        If content fits, returns it intact. Otherwise, truncates with a smart preview
        or summarizes sections.
        """
        if cls.estimate_tokens(content) <= max_tokens:
            return content

        # Simple semantic truncation: extract first few paragraphs or lines
        lines = content.splitlines()
        compressed = []
        token_count = 0

        for line in lines:
            line_tokens = cls.estimate_tokens(line)
            if token_count + line_tokens > max_tokens - 10:
                compressed.append("[... content truncated to preserve context budget ...]")
                break
            compressed.append(line)
            token_count += line_tokens

        return "\n".join(compressed)

    @classmethod
    def build_pyramid_hierarchy(cls, candidates: List[Any]) -> List[Dict[str, Any]]:
        """
        Assembles a hierarchical view of code files/folders (pyramid)
        so that we only present deeper content of highest scoring components.
        """
        hierarchy = []
        for obj in candidates:
            # We can represent items cleanly
            hierarchy.append({
                "id": obj.id,
                "type": obj.type,
                "title": obj.title,
                "summary": obj.summary
            })
        return hierarchy
