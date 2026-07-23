import os
import shutil
import json
from brain.storage.db import init_db, list_knowledge_objects, get_knowledge_object
from brain.ingestion.filesystem.parser import ingest_directory
from brain.memory.manager import (
    remember_working_memory,
    remember_decision,
    remember_failure,
    remember_pattern,
    remember_semantic_relation
)
from brain.retrieval.ranking.orchestrator import RetrievalOrchestrator
from brain.context.assembler import ContextAssembler
from brain.adapters.chatgpt import ChatGPTAdapter
from brain.adapters.claude import ClaudeAdapter
from brain.learning.pipeline import LearningPipeline
from brain.context.session import ContextSessionManager
from brain.context.trace import ObservabilityTraceRegistry

def run_demo():
    print("=========================================================================")
    print("      AI CONTEXT OPERATING SYSTEM (THE BRAIN) - PLATFORM DEMO            ")
    print("=========================================================================\n")

    # 1. Setup local database
    db_file = "demo_brain.db"
    os.environ["BRAIN_DB_PATH"] = db_file
    if os.path.exists(db_file):
        os.remove(db_file)

    print("[1] Initializing persistent storage layer configurations...")
    init_db()
    print(f" -> SQLite Structured and Graph database created at '{db_file}'\n")

    # 2. Ingest a mock directory using our pluggable filesystem parser
    print("[2] Running Ingestor with pluggable base parsing framework...")
    mock_dir = "mock_project"
    os.makedirs(mock_dir, exist_ok=True)

    py_code = """
class StorageManager:
    \"\"\"Handles caching and db connections.\"\"\"
    def __init__(self, dsn):
        self.dsn = dsn

    def save_cache(self, key, value):
        \"\"\"Caches value. Deprecated: use SQL instead.\"\"\"
        pass

    def test_cache_save(self):
        sm = StorageManager("sqlite://")
        assert sm.save_cache("a", 1) is None
"""
    with open(os.path.join(mock_dir, "storage.py"), "w") as f:
        f.write(py_code)

    with open(os.path.join(mock_dir, "README.md"), "w") as f:
        f.write("# Project BrainOS Mock\nThis is a mock project for context demonstration.")

    ingested_ids = ingest_directory(mock_dir, "BrainOS")
    print(f" -> Ingestion pipeline successfully matched and executed.")
    print(f" -> Saved {len(ingested_ids)} canonical KnowledgeObjects (Project, Folder, Code, Class, Method, Test, Document)")
    print("")

    # 3. Show dynamic Resumable Context Sessions
    print("[3] Simulating Context Session Manager (Platform Resumability)...")
    session = ContextSessionManager.create_session(
        project="BrainOS",
        goal="Complete cache refactoring task",
        current_task="Implement SQL execution blocks",
        active_files=["storage.py"],
        branch="feature/cache-sql"
    )
    print(f" -> Session '{session.id}' created and active.")
    print(f"    - Current Task: {session.current_task}")
    print(f"    - Branch: {session.branch}")

    # Pause session and write checkpoint
    ContextSessionManager.add_checkpoint(
        session_id=session.id,
        checkpoint_name="AST Parsed Successfully",
        notes="Pluggable PythonParser parsed and indexed class StorageManager"
    )
    print(" -> Added checkpoint marker to the current session (milestone saved).")
    print(f" -> Retreived session checkpoints: {ContextSessionManager.get_session(session.id).checkpoints}")
    print("")

    # 4. Show Knowledge Provenance, Lineage, and Lifecycle
    print("[4] Checking Knowledge Provenance Lineage & Lifecycles...")
    # Seed decision object with detailed Lineage & Lifecycle
    remember_decision(
        project="BrainOS",
        decision_title="Don't use Redis cache",
        reason="Redis lacks single-node Windows deployment support in target environments.",
        alternatives="Use SQLite in-memory tables for transient caching."
    )

    # Retrieve and inspect platform fields
    dec_id = "decision::brainos::don't_use_redis_cache"
    dec_obj = get_knowledge_object(dec_id)
    if dec_obj:
        # Enforce lifecycle and provenance
        dec_obj.lifecycle = "Active"
        dec_obj.visibility = "internal"
        dec_obj.created_from = "Architectural Review Meeting"
        dec_obj.verified_by = "Technical Director"
        print(f" -> Canonical Object: {dec_obj.title}")
        print(f"    - Lifecycle State: {dec_obj.lifecycle}")
        print(f"    - Visibility Tier: {dec_obj.visibility}")
        print(f"    - Provenance Source: {dec_obj.created_from}")
        print(f"    - Verified By: {dec_obj.verified_by}")
    print("")

    # 5. Multi-stage query routing through our dynamic Retrieval Planner
    print("[5] Query execution via dynamic Retrieval Planner...")
    orchestrator = RetrievalOrchestrator(project="BrainOS")

    query = "Why did we decide not to use Redis?"
    print(f" -> Executing Query: '{query}'")
    results = orchestrator.retrieve_and_rank(query, limit=3)
    for idx, (obj, score, trace_metrics) in enumerate(results):
        print(f"    [{idx+1}] [{obj.type}] {obj.title} (Score: {score:.1f})")
        print(f"        Intent Routed: {trace_metrics.get('intent')}")
    print("")

    # 6. Assemble context with Resource Manager Constraints (Token Budgets)
    print("[6] Context Assembly & Resource Manager Constraint Enforcement...")
    # Allocate small budget to trigger pyramidal compression!
    package = ContextAssembler.assemble_package(
        project="BrainOS",
        user_goal="Write secure cache SQL tables",
        current_task_input="Refactor StorageManager",
        token_budget=150  # extremely tight budget to showcase Resource limits
    )
    print(" -> Standard Context Package successfully assembled with token limits:")
    print(json.dumps(package.model_dump(), indent=2)[:650] + "\n... [truncated] ...\n")

    # 7. Observability Traces
    print("[7] Auditing Observability Trails (Explainable Context traces)...")
    latest_trace = ObservabilityTraceRegistry.get_latest_trace()
    if latest_trace:
        print(f" -> Trace Query: '{latest_trace.query}'")
        print(f" -> Overall Execution Time: {latest_trace.execution_time_ms:.2f} ms")
        print(f" -> Top Node Trace Details:")
        for t in latest_trace.traces[:2]:
            print(f"    - Object: {t.title} [{t.type}]")
            print(f"      Similarity Score: {t.raw_similarity:.2f}")
            print(f"      Included: {t.is_included} (Compression Ratio: {t.compression_ratio:.3f})")
    print("")

    # Clean up mock directories and db
    if os.path.exists(mock_dir):
        shutil.rmtree(mock_dir)
    if os.path.exists(db_file):
        os.remove(db_file)

    print("=========================================================================")
    print("               PLATFORM REFERENCE SIMULATION COMPLETE!                  ")
    print("=========================================================================")

if __name__ == "__main__":
    run_demo()
    os.system("rm -f demo_brain.db")
