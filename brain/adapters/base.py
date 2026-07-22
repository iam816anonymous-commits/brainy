from typing import Dict, Any, List
from brain.context.assembler import ContextPackage

class BaseAIAdapter:
    @staticmethod
    def format_system_prompt(pkg: ContextPackage, user_prompt: str) -> str:
        """
        Structures standard context into an advanced system prompt context injection.
        """
        lines = []
        lines.append("=== SYSTEM CONTEXT OPERATING SYSTEM INJECTION ===")
        lines.append(f"Project context: {pkg.project}")
        lines.append(f"Active task: {pkg.current_task}")
        lines.append(f"User overall goal: {pkg.goal}")

        if pkg.architecture:
            lines.append("\n[Architecture Overview]")
            lines.append(pkg.architecture)

        if pkg.decisions:
            lines.append("\n[Key Architectural Decisions]")
            for d in pkg.decisions:
                lines.append(f"- {d['title']}: {d['summary']}")

        if pkg.constraints:
            lines.append("\n[Project Rules & Constraints]")
            for c in pkg.constraints:
                lines.append(f"- {c['title']}: {c['content']}")

        if pkg.known_failures:
            lines.append("\n[CRITICAL: Avoid Previous Failures]")
            for f in pkg.known_failures:
                lines.append(f"- FAILED ATTEMPT: {f['title']}")
                lines.append(f"  Reason for Failure: {f['summary']}")
                lines.append(f"  Lesson: {f['content']}")

        if pkg.related_docs:
            lines.append("\n[Related Documentation]")
            for doc in pkg.related_docs:
                lines.append(f"--- Document: {doc['title']} ---")
                lines.append(doc['content'])

        if pkg.relevant_code:
            lines.append("\n[Relevant Code & AST Structure]")
            for c in pkg.relevant_code:
                lines.append(f"--- File/Class: {c['title']} ---")
                lines.append(c['content'])

        if pkg.important_conversations:
            lines.append("\n[Relevant Previous Conversations]")
            for conv in pkg.important_conversations:
                lines.append(conv['content'])

        if pkg.recommended_actions:
            lines.append("\n[Recommended Actions]")
            for act in pkg.recommended_actions:
                lines.append(f"- {act}")

        lines.append("\n================================================")
        lines.append("Use the context above to generate the best possible answer.")

        return "\n".join(lines)
