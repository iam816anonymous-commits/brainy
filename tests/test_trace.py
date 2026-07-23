import os
import pytest
from brain.storage.db import init_db, save_knowledge_object
from brain.storage.models import KnowledgeObject
from brain.context.assembler import ContextAssembler
from brain.context.trace import ObservabilityTraceRegistry

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_brain_trace.db"
    os.environ["BRAIN_DB_PATH"] = str(db_file)
    init_db()
    yield
    if "BRAIN_DB_PATH" in os.environ:
        del os.environ["BRAIN_DB_PATH"]

def test_context_tracing_observability_logs():
    ObservabilityTraceRegistry.clear()

    # Seed a decision object
    save_knowledge_object(KnowledgeObject(
        id="aud-1", type="Decision", project="TraceProj", title="Decision Chosen", summary="Selected SQLite", content="We chose SQLite"
    ))

    # Build package
    pkg = ContextAssembler.assemble_package("TraceProj", "How did we choose SQLite?")

    # Verify a trace was automatically recorded!
    latest = ObservabilityTraceRegistry.get_latest_trace()
    assert latest is not None
    assert "sqlite" in latest.query.lower()
    assert latest.total_candidates_processed >= 1
    assert latest.execution_time_ms > 0.0

    # Check that individual node metrics exist
    node_t = latest.traces[0]
    assert node_t.id == "aud-1"
    assert node_t.raw_similarity > 0.0
    assert node_t.is_included is True
