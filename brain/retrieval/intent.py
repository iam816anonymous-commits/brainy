import re
from typing import Dict, Any

class IntentDetector:
    @staticmethod
    def detect_intent(query: str) -> str:
        """
        Rule-based intent detection that categorizes standard developer queries.
        """
        query_lower = query.lower()

        # 1. Debug/Error Intent
        error_keywords = ["error", "traceback", "exception", "failed", "bug", "issue", "crash", "fail", "broken"]
        if any(kw in query_lower for kw in error_keywords) or re.search(r"line \d+", query_lower):
            return "DEBUG_ERROR"

        # 2. Decision History Intent
        decision_keywords = ["why did we", "why not", "why was", "rationale", "decision", "decided", "choose", "chose"]
        if any(kw in query_lower for kw in decision_keywords):
            return "DECISION_HISTORY"

        # 3. Task Status/Working Memory Intent
        task_keywords = ["current task", "active task", "what am i doing", "todo", "progress", "working on", "status"]
        if any(kw in query_lower for kw in task_keywords):
            return "TASK_STATUS"

        # 4. Architecture Intent
        arch_keywords = ["architecture", "design", "structure", "module", "relation", "dependency", "diagram", "components"]
        if any(kw in query_lower for kw in arch_keywords):
            return "ARCHITECTURE"

        # 5. Code Search Intent
        code_keywords = ["class", "method", "function", "file", "code", "implementation", "write a", "syntax", "how to use"]
        if any(kw in query_lower for kw in code_keywords):
            return "CODE_SEARCH"

        return "GENERAL"
