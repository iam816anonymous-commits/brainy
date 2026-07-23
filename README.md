# AI Context Operating System (The Brain) — Foundational Reference Implementation (v1)

Today's AI systems forget context, don't share knowledge between models, and have constrained context windows. **The Brain** solves all three by becoming the **persistent, model-independent intelligence layer** that sits between users/projects and any LLM (ChatGPT, Claude, Gemini, Ollama, etc.).

This repository contains the **Foundational Reference Implementation (v1)** of the Brain as a service for single-project context management.

---

## 🏛️ Reframed 6-Layer Architecture

Instead of a coupled memory table model, the Brain is designed around a clean separation of concerns mapped across six core layers:

```
                  AI Context Operating System (The Brain)

  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 1. INTEGRATION LAYER (Connectors: Filesystem, GitHub, Slack, docs, etc) │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │ Ingestion Pipeline
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 2. KNOWLEDGE LAYER (Canonical Unified KnowledgeObjects)                  │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │ Search & Expansion
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 3. RETRIEVAL LAYER (Intent Detection, Planner, Multi-Stage Search)     │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │ Score & Filter
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 4. CONTEXT LAYER (Pyramidal Compression, Standard JSON Context Package)  │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │ Adapter Injections
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 5. RUNTIME LAYER (LLM Adapters: ChatGPT, Claude, Gemini, Ollama)        │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │ Execution Feedback
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 6. LEARNING LAYER (Outcome Evaluation, Auto-Logged Failure Lessons)     │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 1. Integration Layer (Connector & Ingestion Pipelines)
This layer ingests raw events, source files, documentation, and metadata. It routes raw data through our standard ingestion pipeline:
```
Source (Filesystem/Git/Web) ──► Pluggable Parser ──► Normalizer ──► Entity Extractor ──► Store
```
* **Pluggable Parsers**: Features an abstract `BaseParser` interface. For v1, we provide a concrete `PythonParser` (with native Abstract Syntax Tree extraction of python Classes/Methods/Tests) and a `DefaultParser` for generic document text. Other language parsers (Rust, Go, TypeScript) can easily be plugged in.

### 2. Knowledge Layer (Canonical Internal Model)
Everything inside the Brain is modeled as a typed, canonical **`KnowledgeObject`**. Instead of disconnected tables, all entries share a common model mapping attributes (id, type, project, title, summary, content, importance, confidence, tags, relations). This unified data structure handles:
- **Active Task / Working Context**
- **Architectural Decisions**
- **Known Failure Logs (Lessons-Learned)**
- **Semantic Entities**
- **Design Patterns**
- **Conversation dialogue logs**
- **Code components**

**Storage Abstractions**:
Our storage contracts abstract the underlying databases so that the architecture remains decoupled:
- **Structured Storage**: Mapped to SQLite in v1. Easily replaceable with PostgreSQL.
- **Graph Storage**: Model relationships mapped using NetworkX in v1. Replaceable with Neo4j.
- **Vector Storage**: Cosine similarity calculations on local numpy TF-IDF vectors (or OpenAI embeddings) in v1. Replaceable with Qdrant, Milvus, or FAISS.

### 3. Retrieval Layer (Retrieval Planner & Pipeline)
Never rely on embedding distance alone. The Retrieval Layer employs a dedicated **Retrieval Planner** to orchestrate search.

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

* **Retrieval Planner**: Decides which specific retrieval strategies to execute based on detected query intent. For example, if a user asks for decision rationales, it dynamically focuses on Decision databases and graph traversals.
* **Unified Context Ranking**: Scores candidates based on:
  $$\text{Score} = \text{Semantic Similarity} + \text{Importance} + \text{Recency} + \text{Project Match} + \text{File Match} + \text{Dependency Distance} + \text{Historical Success} - \text{Noise}$$

### 4. Context Layer (Standardized Context Packages)
Compiles, structures, and limits the payload to fit precisely inside token budgets.
- **Pyramidal Compression**: Truncates content elegantly, presenting full detail for top hits and summaries for secondary nodes.
- **Model-Independent Context Package**: Outputs an identical JSON package regardless of which model is eventually used.

### 5. Runtime Layer (Platform Adapters)
Contains reusable, standard connectors for top AI chatbots. Adapters format standard context package payloads into model-optimized prompt completions.
- **ChatGPT / OpenAI Adapter**
- **Claude / Anthropic Adapter**
- **Gemini / Google Adapter**
- **Ollama Local Adapter**

### 6. Learning Layer (Outcome-Driven Loops)
Refines the Context OS dynamically by processing outcome feedback.
- If a chosen context results in an execution failure, the Learning Pipeline dynamically penalizes its confidence rating and automatically registers a new **Failure Memory** object to ensure future retrieval runs avoid repeating that failure.

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
- Scan of a directory structure using the Python AST parser.
- Logging of multi-tier memories (Active task, decisions, failures, patterns, semantic links).
- Dynamic Retrieval Planner execution and ranking.
- Prompt construction and execution via ChatGPT/Claude Adapters.
- Dynamically processing failures in the Learning Loop.

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
