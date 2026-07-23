# AI Context Operating System (The Brain) — Foundational Reference Implementation (v1)

Today's AI systems forget context, don't share knowledge between models, and have constrained context windows. **The Brain** solves all three by becoming the **persistent, model-independent intelligence layer** that sits between users/projects and any LLM (ChatGPT, Claude, Gemini, Ollama, etc.).

This repository contains the **Foundational Reference Implementation (v1)** of the Brain as a reusable, extensible context operating system.

---

## 🏛️ Reframed 6-Layer Architecture

Instead of a coupled memory model, the Brain is designed around a clean separation of concerns mapped across six core layers:

```
                  AI Context Operating System (The Brain)

  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 1. INTEGRATION LAYER (Ingestion Pipeline: GitHub, Filesystem, Slack)    │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │ Ingestion Pipeline Events
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 2. KNOWLEDGE LAYER (Canonical Unified KnowledgeObjects & Abstractions)  │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │ Search & Expansion
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 3. RETRIEVAL LAYER (Intent Detection, Planner, Retriever Plugins)       │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │ Score & Filter
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 4. CONTEXT LAYER (Resource Manager, Cache, Resumable Sessions, Tracing) │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │ Adapter Injections
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 5. EXECUTION INTEGRATION LAYER (LLM Adapters: Claude, ChatGPT, Gemini)   │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │ Execution Feedback
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 6. LEARNING LAYER (Outcome Evaluation, Auto-Logged Failure Lessons)     │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

### 1. Integration Layer (Connector & Ingestion Pipelines)
This layer ingests events, source files, documentation, and metadata, routing raw files through our standard ingestion pipeline:
```
Source (Filesystem/Git/Web) ──► Pluggable Parser ──► Normalizer ──► Entity Extractor ──► Store
```
* **Pluggable Parsers**: Features an abstract `BaseParser` interface. For v1, we provide a concrete `PythonParser` (with native AST extraction of python Classes/Methods/Tests) and a `DefaultParser` for generic document text. Other language parsers (Rust, Go, TypeScript) can easily be plugged in.

---

### 2. Knowledge Layer (Canonical Internal Model)
Everything inside the Brain is modeled as a typed, canonical **`KnowledgeObject`**. Instead of disconnected tables, all entries share a common model mapping attributes:
* **Knowledge Lifecycle State**: Tracks lifecycle states: `Created`, `Verified`, `Active`, `Referenced`, `Archived`, `Deleted`.
* **Knowledge Provenance**: Lineage tracking metadata (`source`, `owner`, `created_from`, `derived_from`, `verified_by`, `last_verified`) to trace exactly where facts came from.
* **Enterprise Permissions**: Fields built-in for role-based security (`visibility`, `permissions`, `group`) even if v1 allows global access.
* **Extensible Payloads**: Generic dictionaries (`metadata`, `payload`) for custom entity properties.

**Storage Abstractions**:
Our storage contracts abstract the underlying databases so that the architecture remains decoupled:
* **Structured Storage**: Mapped to SQLite in v1. Easily replaceable with PostgreSQL.
* **Graph Storage**: Model relationships mapped using NetworkX in v1. Replaceable with Neo4j.
* **Vector Storage**: Cosine similarity calculations on local numpy TF-IDF vectors (or OpenAI embeddings) in v1. Replaceable with Qdrant, Milvus, or FAISS.

---

### 3. Retrieval Layer (Retrieval Planner & Plugins)
The Retrieval Layer employs a dedicated **Retrieval Planner** to orchestrate search.

```
                      User Query
                           │
                           ▼
                   Intent Detection
                           │
                           ▼
                   Retrieval Planner
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   Keyword Search   Embedding Search   Graph Search
   (Structured DB)   (Local Vector)    (Relations)
         │                 │                 │
         └─────────────────┼─────────────────┘
                           ▼
                     Candidate Merge
                           │
                           ▼
                    Context Ranking
              (Formula-based unified score)
                           │
                           ▼
                 Context Compression
```

* **Retrieval Planner**: Decides which specific retrieval strategies to execute based on detected query intent.
* **Retriever Plugin Architecture**: Extends `BaseRetriever` so additional algorithms can be plugged in. Built-in retrievers include `KeywordRetriever`, `EmbeddingRetriever`, `GraphRetriever`, `DecisionRetriever`, `FailureRetriever`, and `RecentRetriever`.
* **Unified Context Ranking**: Scores candidates based on:
  $$\text{Score} = \text{Semantic Similarity} + \text{Importance} + \text{Recency} + \text{Project Match} + \text{File Match} + \text{Dependency Distance} + \text{Historical Success} - \text{Noise}$$

---

### 4. Context Layer (Platform Resource Management)
Compiles, caches, audits, and limits context packages dynamically.
* **Context Resource Manager**: Enforces strict Token Budgets, Latency limits, and proportional segment allocations (e.g. 40% code, 20% decisions, 15% failures, 15% rules, 10% docs) so context assembly remains predictable as projects grow.
* **Context Cache**: Stores compiled ContextPackages under a TTL to prevent redundant retrieval operations when multiple models query the same context seconds apart.
* **Resumable Context Sessions**: Keeps workspace states resumable (active files, current branch, checkpoints) so that developers can easily pause/resume tasks.
* **Context Tracing Observability**: Full execution audits recorded inside the `ObservabilityTraceRegistry` explaining exactly why each node was chosen, ranked, compressed, or discarded.

---

### 5. Execution Integration Layer (Platform Adapters)
Contains standard adapters for top AI execution environments. Adapters format standardized Context Packages into model-optimized prompt completions.
* **ChatGPT / OpenAI Adapter**
* **Claude / Anthropic Adapter**
* **Gemini / Google Adapter**
* **Ollama Local Adapter**

---

### 6. Learning Layer (Outcome-Driven Loops)
Refines the Context OS dynamically by processing outcome feedback.
* If a chosen context results in an execution failure, the Learning Pipeline dynamically penalizes its confidence rating and automatically registers a new **Failure Memory** object to ensure future retrieval runs avoid repeating that failure.

---

## 📦 Installation & Setup Guide

### Option A: Virtual Environment Setup (Recommended)
This isolates dependencies from your system's global environment.

1. **Create the virtual environment**:
   ```bash
   python3 -m venv venv
   ```

2. **Activate the environment**:
   - **On Linux / macOS**:
     ```bash
     source venv/bin/activate
     ```
   - **On Windows (Command Prompt)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **On Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

3. **Install the package**:
   ```bash
   pip install --upgrade pip
   pip install -e .[dev]
   ```

---

### Option B: Global System Environment Setup
To install packages directly into your global system Python workspace:
```bash
pip3 install -e .[dev]
```

---

## 🎮 Execution Commands

### 1. Run the Interactive Simulation Demo
We provide a comprehensive demonstration script (`demo.py`) that showcases:
- System boot and database setup.
- Scan of a directory structure using the pluggable file parser.
- Managing Context Sessions and checkpoint milestones.
- Managing knowledge provenance lineage and lifecycles.
- Context Resource Manager execution enforcing strict token budgets.
- Retrieving and auditing execution traces inside the Observability registry.

```bash
python3 demo.py
```

### 2. Start the REST API Gateway
Launch the FastAPI web service:
```bash
uvicorn brain.api.app:app --reload --host 127.0.0.1 --port 8000
```
Interactive OpenAPI/Swagger docs are automatically live at:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### 3. Start the MCP Server
To allow MCP-compatible desktop clients (like Cursor or Claude Desktop) to connect directly:
```bash
python3 -m brain.sdk.mcp_server
```

### 4. Run unit tests
```bash
python3 -m pytest
```

---

## 🛠️ Configuration Options

| Variable | Description | Default |
| --- | --- | --- |
| `BRAIN_DB_PATH` | File path for persistent SQLite database | `brain.db` |
| `OPENAI_API_KEY` | Optional OpenAI key for embeddings & ChatGPT API completion | `None` (triggers local TF-IDF & mock) |
| `ANTHROPIC_API_KEY` | Optional Anthropic key for real Claude execution | `None` (triggers high-fidelity mock) |
| `GEMINI_API_KEY` | Optional Google key for real Gemini execution | `None` (triggers high-fidelity mock) |
