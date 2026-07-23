import time
from brain.context.resource_manager import ContextResourceManager

def test_resource_manager_token_allocations():
    mgr = ContextResourceManager(token_budget=1000)
    allocations = mgr.get_segment_allocations()

    assert allocations["relevant_code"] == 400
    assert allocations["decisions"] == 200
    assert allocations["known_failures"] == 150
    assert allocations["related_docs"] == 100

def test_resource_manager_latency_checks():
    mgr = ContextResourceManager(latency_budget_ms=10)
    assert mgr.is_latency_exceeded() is False

    # Sleep to trigger timeout
    time.sleep(0.015)
    assert mgr.is_latency_exceeded() is True

def test_token_allocation_truncation():
    mgr = ContextResourceManager(token_budget=100)
    allocs = mgr.get_segment_allocations() # related_docs gets 10% -> 10 tokens

    candidates = [
        {"id": "doc-1", "content": "This is a super long sentence which easily exceeds ten tokens in character length budget calculations"}
    ]

    allocated = mgr.allocate_tokens_to_segment(candidates, allocs["related_docs"])
    assert len(allocated) == 1
    # Check that it was compressed/truncated
    assert "[... content" in allocated[0]["content"]
