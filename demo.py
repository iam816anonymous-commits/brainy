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

def run_demo():
    print("=========================================================")
    print("   AI CONTEXT OPERATING SYSTEM (THE BRAIN) - E2E DEMO   ")
    print("=========================================================\n")

    # 1. Setup local database
    db_file = "demo_brain.db"
    os.environ["BRAIN_DB_PATH"] = db_file
    if os.path.exists(db_file):
        os.remove(db_file)

    print("[1] Initializing persistent Storage Layer...")
    init_db()
    print(f" -> Database initialized successfully at '{db_file}'\n")

    # 2. Ingest a mock directory (Phase 2 - Project Model, Folder, Files)
    print("[2] Simulating Project Ingestion Layer (Filesystem AST Parser)...")
    mock_dir = "mock_project"
    os.makedirs(mock_dir, exist_ok=True)

    # Let's write a python file with methods and tests
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
    print(f" -> Successfully scanned and parsed directory tree of '{mock_dir}'")
    print(f" -> Created {len(ingested_ids)} hierarchical KnowledgeObjects (Project, Folder, Code, Class, Method, Test, Document)")
    print("")

    # 3. Seed multi-layer memories (Phase 3 - Multi-layer memory types)
    print("[3] Seeding Multi-Layer Memories...")

    # A. Active Task (Working Memory)
    remember_working_memory(
        project="BrainOS",
        current_task="Refactor storage.py cache routine",
        active_files=["storage.py"],
        branch="feature/cache-refactor",
        current_errors=["save_cache has no return value in line 7"]
    )
    print(" -> Seeded Working Memory (active task, branch, active files, current errors).")

    # B. Key Decision (Decision Memory)
    remember_decision(
        project="BrainOS",
        decision_title="Don't use Redis cache",
        reason="Due to restricted single-node Windows constraints.",
        alternatives="Use SQLite in-memory tables for transient caching."
    )
    print(" -> Seeded Decision Memory (Rationale: don't use Redis on Windows constraints).")

    # C. Known Failure (Failure Memory)
    remember_failure(
        project="BrainOS",
        attempted_action="Use Redis server docker container on local machine",
        reason_for_failure="WSL2 Docker backend port conflicts occurred repeatedly.",
        resolution_or_lessons="Stick to lightweight serverless engines like SQLite."
    )
    print(" -> Seeded Failure Memory (Tried Redis server docker, WSL port conflict).")

    # D. Workflow Pattern (Pattern Memory)
    remember_pattern(
        project="BrainOS",
        pattern_name="Cache Set Flow",
        steps=["Verify key exists", "Acquire SQLite connection", "Write statement", "Close connection"],
        description="Standardized cache set transactions."
    )
    print(" -> Seeded Pattern Memory (Cache transaction steps).")

    # E. Semantic Relation (Semantic Memory)
    remember_semantic_relation("BrainOS", "SQLite", "alternative_to", "Redis")
    print(" -> Seeded Semantic Relationship (SQLite is an alternative_to Redis).")
    print("")

    # 4. Run Retrieval and Context Ranking Orchestrator (Phases 5 & 6)
    print("[4] Executing Multi-Stage Retrieval & Unified Context Ranking...")
    orchestrator = RetrievalOrchestrator(project="BrainOS")

    # Query A: Searching for Redis rationale
    query_a = "Why not use Redis for caching?"
    print(f"\n -> Query A: '{query_a}'")
    results_a = orchestrator.retrieve_and_rank(query_a, limit=3)
    for idx, (obj, score) in enumerate(results_a):
        print(f"    [{idx+1}] [{obj.type}] {obj.title} (Score: {score:.2f})")
        print(f"        Summary: {obj.summary}")

    # Query B: Searching for Code reference
    query_b = "How does StorageManager cache save work?"
    print(f"\n -> Query B: '{query_b}'")
    results_b = orchestrator.retrieve_and_rank(query_b, limit=3)
    for idx, (obj, score) in enumerate(results_b):
        print(f"    [{idx+1}] [{obj.type}] {obj.title} (Score: {score:.2f})")

    print("")

    # 5. Assemble Context Package and call Adapters (Phases 7, 8 & 9)
    print("[5] Assembling Structured Model-Independent Context Package...")
    package = ContextAssembler.assemble_package(
        project="BrainOS",
        user_goal="Refactor caching mechanism safely",
        current_task_input="Replace save_cache with SQL table"
    )

    print(" -> Generated Standard Context Package:")
    print(json.dumps(package.model_dump(), indent=2)[:600] + "\n... [truncated for display] ...\n")

    print(" -> Dispatching Standard Context through ChatGPT Adapter...")
    gpt_response = ChatGPTAdapter.execute(package, "Should we use redis docker container or in-memory tables?")
    print(f" -> ChatGPT says:\n{gpt_response}\n")

    print(" -> Dispatching Standard Context through Claude Adapter...")
    claude_response = ClaudeAdapter.execute(package, "Refactor save_cache signature")
    print(f" -> Claude says:\n{claude_response}\n")

    # 6. Learning Loop Dynamic Feedback (Phase 10)
    print("[6] Activating Learning Pipeline Loop...")
    # Simulate a user giving negative feedback about the StorageManager class (id is from parsed python file)
    target_class_id = "file::BrainOS::storage.py::class::StorageManager"
    print(f" -> Simulating failure outcome on object '{target_class_id}'...")

    feedback_res = LearningPipeline.process_feedback(
        obj_id=target_class_id,
        success=False,
        user_notes="StorageManager class was missing constructor parameters in runtime.",
        project_name="BrainOS"
    )
    print(f" -> Feedback processed. updates: {feedback_res['updates_applied']}")

    # Verify that a Failure memory was auto-logged by the learning pipeline
    updated_obj = get_knowledge_object(target_class_id)
    print(f" -> Adjusted Confidence: {updated_obj.confidence:.2f}")

    db_failures = list_knowledge_objects(project="BrainOS", obj_type="Failure")
    print(f" -> Automatically registered failures inside database count: {len(db_failures)}")
    for f in db_failures:
        if "StorageManager" in f.content:
            print(f"    - [AUTO FAILURE] {f.title}: {f.summary}")

    # Clean up mock directories and db
    if os.path.exists(mock_dir):
        shutil.rmtree(mock_dir)
    if os.path.exists(db_file):
        os.remove(db_file)

    print("\n=========================================================")
    print("   AI CONTEXT OPERATING SYSTEM E2E DEMO COMPLETE!        ")
    print("=========================================================")

if __name__ == "__main__":
    run_demo()
