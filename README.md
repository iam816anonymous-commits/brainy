# AI Context Operating System (The Brain) — Foundational Reference Implementation (v1)

Today's AI systems forget context, don't share knowledge between models, and have constrained context windows. **The Brain** solves all three by becoming the **persistent, model-independent intelligence layer** that sits between users/projects and any LLM (ChatGPT, Claude, Gemini, Ollama, etc.).

This repository contains the **Foundational Reference Implementation (v1)** of the Brain as a modular, **distributed microservices architecture**.

---

## 🏛️ Distributed Microservices & 6-Layer Architecture

Instead of a monolithic design, the Brain is decoupled into three dedicated, standalone microservices communicating over HTTP:

```
                  AI Context Operating System (The Brain)

  ┌─────────────────────────────────────────────────────────────┐
  │ INTEGRATION & KNOWLEDGE SERVICE (Port 8001)                 │
  │   - Pluggable base parsing & AST PythonParser               │
  │   - Ingestion (GitHub commits/issues, markdown doc files)   │
  │   - Unified canonical Storage (SQLite + NetworkX)           │
  └─────────────────────────────────────────────────────────────┘
                               ▲
                               │ HTTP REST Queries
                               ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ RETRIEVAL & CONTEXT SERVICE (Port 8002)                     │
  │   - Intent Detection & Retrieval Planner                    │
  │   - Retriever Plugins (Keyword, Vector, Graph, Failure)     │
  │   - Token budgets (Resource Manager) & Context Cache        │
  │   - Resumable Session checkpointing & Traces Auditing       │
  └─────────────────────────────────────────────────────────────┘
                               ▲
                               │ HTTP REST Queries
                               ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ EXECUTION INTEGRATION SERVICE (Port 8003)                   │
  │   - LLM Chatbot Platform Adapters (ChatGPT, Claude, Gemini) │
  │   - Learning Loops (Failure penalty outcome feedback)       │
  └─────────────────────────────────────────────────────────────┘
```

The Brain's features map across six logical operating system layers:
1. **Integration Layer**: Routes events, file structures, and documentation through pluggable language parsers (featuring `BaseParser`, `PythonParser`, and `DefaultParser`).
2. **Knowledge Layer**: Models and links everything inside a unified, canonical **`KnowledgeObject`** containing lifecycle state machines (`Created`, `Verified`, `Active`), lineage provenance records, enterprise visibility permissions, and metadata payloads.
3. **Retrieval Layer**: Coordinates search strategies dynamically via a **Retrieval Planner** and pluggable Retriever plugins (`KeywordRetriever`, `EmbeddingRetriever`, `GraphRetriever`, `RecentRetriever`, etc.).
4. **Context Layer**: Schedules resources using the **Context ResourceManager** (enforcing strict Token Budgets, Latency budgets, and proportional segment allocations), caches compiled context under a TTL, manages resumable sessions, and writes explainability tracing logs.
5. **Execution Integration Layer**: Translates Context Packages into model-optimized prompts via platform adapters (ChatGPT, Claude, Gemini, Ollama).
6. **Learning Layer**: Penalizes retrieved object confidence dynamically on failure and auto-creates failure-learned memory packages.

---

## 📦 Distributed Port Mappings

| Service | Port | Description |
| --- | --- | --- |
| **Knowledge & Ingestion** | `8001` | CRUD on KnowledgeObjects, AST directory scanning, and GitHub uploads |
| **Retrieval & Context** | `8002` | Context assembly, session checkpointing, and tracing logs |
| **Execution Integration** | `8003` | LLM model adapters and outcome feedback processing |

---

## 🚀 Installation & Setup Guide

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
The interactive demo script (`demo.py`) bootstraps, populates, and orchestrates the distributed services:
```bash
python3 demo.py
```

### 2. Start each Microservice Individually
Launch the independent services on their respective ports:

* **Start Ingestion & Knowledge Service (Port 8001)**:
  ```bash
  uvicorn brain.services.knowledge.app:app --host 127.0.0.1 --port 8001
  ```
* **Start Retrieval & Context Service (Port 8002)**:
  ```bash
  uvicorn brain.services.retrieval.app:app --host 127.0.0.1 --port 8002
  ```
* **Start Execution Integration Service (Port 8003)**:
  ```bash
  uvicorn brain.services.execution.app:app --host 127.0.0.1 --port 8003
  ```

Interactive Swagger documentations can be accessed at:
👉 Knowledge service: `http://localhost:8001/docs`
👉 Retrieval service: `http://localhost:8002/docs`
👉 Execution service: `http://localhost:8003/docs`

### 3. Start the MCP Server
```bash
python3 -m brain.sdk.mcp_server
```

### 4. Run the complete test suite
```bash
python3 -m pytest
```

---

## 🛠️ Configuration Options

| Variable | Description | Default |
| --- | --- | --- |
| `BRAIN_DB_PATH` | File path for persistent SQLite database | `brain.db` |
| `BRAIN_KNOWLEDGE_SERVICE_URL` | Destination URL for the Knowledge microservice | `http://localhost:8001` |
| `BRAIN_RETRIEVAL_SERVICE_URL` | Destination URL for the Retrieval microservice | `http://localhost:8002` |
| `BRAIN_EXECUTION_SERVICE_URL` | Destination URL for the Execution microservice | `http://localhost:8003` |
| `OPENAI_API_KEY` | Optional OpenAI key for embeddings & ChatGPT API completion | `None` (local fallback triggered) |
| `ANTHROPIC_API_KEY` | Optional Anthropic key for real Claude execution | `None` (local fallback triggered) |
| `GEMINI_API_KEY` | Optional Google key for real Gemini execution | `None` (local fallback triggered) |
