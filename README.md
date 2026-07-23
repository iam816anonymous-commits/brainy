# AI Context Operating System (The Brain) — Version 1

Today's AI systems forget context, don't share knowledge between models, and have constrained context windows. **The Brain** solves all three by becoming the **persistent intelligence layer** that sits between users/projects and any LLM (ChatGPT, Claude, Gemini, Ollama, etc.).

This repository contains the complete, production-grade **Version 1 (v1)** implementation of the Brain as a service for single-project context management.

---

## 🚀 Architectural Overview

```
┌────────────────────────────────────────────┐
│            CLIENT LAYER                    │
├────────────────────────────────────────────┤
│ ChatGPT │ Claude │ Gemini │ Local LLM │ API│
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│          CONTEXT API GATEWAY               │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│          CONTEXT ENGINE                    │
│                                            │
│ Intent Detection                           │
│ Memory Retrieval                           │
│ Ranking                                    │
│ Compression                                │
│ Context Assembly                           │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│             KNOWLEDGE CORE                 │
├────────────────────────────────────────────┤
│ Facts      │ Decisions  │ Failures         │
│ Code       │ Docs       │ Conversations    │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│          STORAGE LAYER                     │
│ SQLite + NetworkX Graph                    │
└────────────────────────────────────────────┘
```

The Brain functions as **infrastructure**, rather than an AI agent. It never "thinks" or replaces the LLM; instead, it:
1. **Ingests and Organizes**: Parses directory structures (with native Abstract Syntax Tree extraction of python Classes/Methods/Tests) into connected Graph structures.
2. **Maintains Multi-Tier Memory**: Tracks Working Memory (active tasks), Episodic History (event series), Semantic Relations, Architectural Decisions, past Failures, and Workflow Patterns.
3. **Retrieves and Ranks**: Scores candidates dynamically based on Query Intent, Semantic Vector Similarity (local numpy TF-IDF or OpenAI), Recency, Importance, Project Match, and Graph Distance.
4. **Compresses & Packages**: Conforms the payload into a model-independent structured Context JSON Package, fitting it precisely inside standard token budgets.
5. **Continuous Learning**: Evaluates success/failure outcomes to dynamically adapt retrieval confidence weights and auto-register Failure Memories.

---

## 📦 Installation & Setup Guides

### Option A: Virtual Environment Setup (Recommended)
This keeps dependencies isolated from your system Python.

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

3. **Install the package in editable mode**:
   ```bash
   pip install --upgrade pip
   pip install -e .[dev]
   ```

---

### Option B: Global System Environment Setup
If you prefer installing packages directly onto your system environment.

1. **Install dependencies and setup package globally**:
   ```bash
   pip3 install -e .[dev]
   ```

---

## 🛠️ Configuration Options

The system runs out of the box with zero setup. You can customize behavior using Environment Variables:

| Variable | Description | Default |
| --- | --- | --- |
| `BRAIN_DB_PATH` | Path to the persistent SQLite database file | `brain.db` |
| `OPENAI_API_KEY` | Optional. If provided, enables real OpenAI Embeddings and ChatGPT API calls. If absent, falls back to local numpy TF-IDF vectors and high-fidelity mocks. | `None` |
| `ANTHROPIC_API_KEY` | Optional. Enables real Claude API completion. If absent, falls back to mocks. | `None` |
| `GEMINI_API_KEY` | Optional. Enables real Google Gemini API execution. If absent, falls back to mocks. | `None` |

---

## 🎮 How to Run

### 1. Run the Interactive End-to-End Simulation Demo
We provide a comprehensive demonstration script (`demo.py`) that showcases:
- Database creation and SQLite table setup.
- Automatic AST-based parsing of a Python source directory structure.
- Multi-layer memory logging (Working task, decisions, failures, semantic links).
- Multi-stage retrieval and unified context ranking.
- Context package assembly & dispatching to ChatGPT / Claude adapters.
- Learning pipeline processing (updating object weight parameters and auto-generating failure logs).

Run the demo using:
```bash
python3 demo.py
```

#### Expected Output of the Demo:
You will see a structured console layout highlighting:
- Success logs for database setup and directory AST scanning.
- Discovered and ranked candidate nodes for varied queries (e.g., matching "Why not use Redis?" directly to the Decision and Failure memories).
- Beautiful JSON context package outputs.
- Mock adapter execution blocks showing standard context prompts being built.
- The outcome learning loop in action: degrading confidence of a failed class from `1.0` to `0.8` and automatically creating a corresponding `Failure` record.

---

### 2. Start the REST API Gateway
Start the high-performance FastAPI server locally (defaulting to port `8000`):
```bash
uvicorn brain.api.app:app --reload --host 127.0.0.1 --port 8000
```

Once the server is running, you can access the **interactive API docs (Swagger UI)** at:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

### 3. Run the Model Context Protocol (MCP) Server
To let MCP-compatible AI clients (like Cursor, Claude Desktop, etc.) use your Brain as a context resource, run the standard stdio MCP server:
```bash
python3 -m brain.sdk.mcp_server
```

---

### 4. Run the Unit Test Suite
To execute the complete suite of 22 rigorous unit and integration tests:
```bash
python3 -m pytest
```

---

## 🔌 API Endpoints Reference

### Ingestion & Memory Logging Endpoints
* **`POST /projects`**: Initialize a new project node.
  - Body: `{"name": "MyProj", "summary": "Project summary", "description": "Longer text"}`
* **`POST /tasks`**: Save active working task state.
  - Body: `{"project": "MyProj", "task": "Active goal", "active_files": ["main.py"], "errors": []}`
* **`POST /decision`**: Record architectural decisions and rationales.
  - Body: `{"project": "MyProj", "title": "Use SQLite", "reason": "Self-contained database", "status": "approved"}`
* **`POST /failure`**: Log failed attempts to prevent future repeats.
  - Body: `{"project": "MyProj", "attempted_action": "Use Redis", "reason_for_failure": "WSL2 port conflict"}`
* **`POST /conversation`**: Record previous chat/interaction transcripts.
* **`POST /remember`**: Generic knowledge object storage conforming to the unified schema.

### Context Retrieval & Analytics Endpoints
* **`GET /context/{project}`** / **`POST /context`**: Retrieve the optimal, ranked, and compressed standard Context Package JSON for an active query.
  - URL Query params: `user_goal` (required) & `current_task` (optional).
* **`GET /graph`**: Retrieve node and edge representation of the project's knowledge graph (NetworkX model representation).
* **`GET /timeline`**: Retrieve chronologically sorted historical decisions, meetings, and failures.
* **`POST /feedback`**: Dynamically adjust object retrieval weights based on task outcome.
  - Body: `{"id": "node_id", "success": true/false}`

---

## 🛠️ Cross-Ecosystem SDK Integration

The Brain is designed to work with all popular backend services. Examples are provided in:
- **Python**: Full-featured client SDK in `brain/sdk/client.py` and MCP server in `brain/sdk/mcp_server.py`.
- **TypeScript/JavaScript**: HTTP-based client wrapper in `brain/sdk/client_example.ts`.
- **Go**: Struct-based HTTP client wrapper in `brain/sdk/client_example.go`.
