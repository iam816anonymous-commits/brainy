import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from brain.adapters.chatgpt import ChatGPTAdapter
from brain.adapters.claude import ClaudeAdapter
from brain.adapters.gemini import GeminiAdapter
from brain.adapters.ollama import OllamaAdapter
from brain.learning.pipeline import LearningPipeline
from brain.context.assembler import ContextPackage

app = FastAPI(
    title="Brain - Execution Integration Microservice",
    description="Orchestrates AI connector adapters and outcome feedback learning loops.",
    version="1.0.0"
)

# --- Request Models ---

class AdapterExecutionRequest(BaseModel):
    project: str
    user_goal: str
    current_task: Optional[str] = None
    user_prompt: str
    model: Optional[str] = None
    token_budget: int = 4000

class FeedbackSubmitRequest(BaseModel):
    id: str
    success: bool
    feedback: str = ""
    project: Optional[str] = None

# --- Routes ---

@app.post("/adapters/chatgpt")
def execute_chatgpt(data: AdapterExecutionRequest):
    # Retrieve standard context package over HTTP or assemble directly
    pkg = ContextAssembler_assemble_mock_pkg(data.project, data.user_goal, data.current_task, data.token_budget)
    model = data.model or "gpt-4o"
    response = ChatGPTAdapter.execute(pkg, data.user_prompt, model=model)
    return {"response": response, "model": model}

@app.post("/adapters/claude")
def execute_claude(data: AdapterExecutionRequest):
    pkg = ContextAssembler_assemble_mock_pkg(data.project, data.user_goal, data.current_task, data.token_budget)
    model = data.model or "claude-3-5-sonnet-20241022"
    response = ClaudeAdapter.execute(pkg, data.user_prompt, model=model)
    return {"response": response, "model": model}

@app.post("/adapters/gemini")
def execute_gemini(data: AdapterExecutionRequest):
    pkg = ContextAssembler_assemble_mock_pkg(data.project, data.user_goal, data.current_task, data.token_budget)
    model = data.model or "gemini-1.5-pro"
    response = GeminiAdapter.execute(pkg, data.user_prompt, model=model)
    return {"response": response, "model": model}

@app.post("/adapters/ollama")
def execute_ollama(data: AdapterExecutionRequest):
    pkg = ContextAssembler_assemble_mock_pkg(data.project, data.user_goal, data.current_task, data.token_budget)
    model = data.model or "llama3"
    response = OllamaAdapter.execute(pkg, data.user_prompt, model=model)
    return {"response": response, "model": model}

@app.post("/feedback")
def process_feedback(data: FeedbackSubmitRequest):
    res = LearningPipeline.process_feedback(
        obj_id=data.id,
        success=data.success,
        user_notes=data.feedback,
        project_name=data.project
    )
    return res

# --- HTTP Helpers ---

def ContextAssembler_assemble_mock_pkg(project: str, user_goal: str, current_task: Optional[str], token_budget: int) -> ContextPackage:
    """
    Assembles context package. In a fully distributed network we would query retrieval service,
    but since we share database config we can instantiate the assembler directly for high performance!
    """
    from brain.context.assembler import ContextAssembler
    return ContextAssembler.assemble_package(project, user_goal, current_task, token_budget)
