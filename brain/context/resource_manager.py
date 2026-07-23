import time
from typing import Dict, Any, List

class ContextResourceManager:
    """
    Acts as the OS Memory & Resource Scheduler. Manages Token budgets, Latency budgets,
    retrieval time constraints, and dynamic segment allocations.
    """
    def __init__(
        self,
        token_budget: int = 4000,       # Max tokens allowed for entire package
        latency_budget_ms: float = 800,  # Max processing time allowed
        retrieval_limit: int = 20        # Max raw candidate nodes
    ):
        self.token_budget = token_budget
        self.latency_budget_ms = latency_budget_ms
        self.retrieval_limit = retrieval_limit
        self.start_time = time.time()

    def is_latency_exceeded(self) -> bool:
        """
        True if current processing duration exceeds the budgeted latency window.
        """
        elapsed_ms = (time.time() - self.start_time) * 1000.0
        return elapsed_ms > self.latency_budget_ms

    def get_segment_allocations(self) -> Dict[str, int]:
        """
        Distributes total token budget proportionally across standard context segments.
        Proportional allocations:
        - Relevant Code: 40%
        - Architectural Decisions: 20%
        - Project Constraints/Rules: 15%
        - Known Failures: 15%
        - Documentation: 10%
        """
        return {
            "relevant_code": int(self.token_budget * 0.40),
            "decisions": int(self.token_budget * 0.20),
            "constraints": int(self.token_budget * 0.15),
            "known_failures": int(self.token_budget * 0.15),
            "related_docs": int(self.token_budget * 0.10)
        }

    def allocate_tokens_to_segment(self, candidates: List[Dict[str, Any]], max_segment_tokens: int) -> List[Dict[str, Any]]:
        """
        Compresses and filters a segment's candidates to strictly enforce the token allocation constraint.
        """
        from brain.compression.compressor import ContextCompressor
        allocated_items = []
        accumulated_tokens = 0

        for item in candidates:
            content = item.get("content", "")
            item_tokens = ContextCompressor.estimate_tokens(content)

            if accumulated_tokens + item_tokens <= max_segment_tokens:
                allocated_items.append(item)
                accumulated_tokens += item_tokens
            else:
                # Compress to fit remaining budget
                remaining_budget = max_segment_tokens - accumulated_tokens
                if remaining_budget >= 5:
                    compressed_content = ContextCompressor.compress_content(content, max_tokens=remaining_budget)
                    item["content"] = compressed_content
                    allocated_items.append(item)
                    accumulated_tokens += ContextCompressor.estimate_tokens(compressed_content)
                break

        return allocated_items
