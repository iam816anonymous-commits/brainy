import requests
from typing import List, Dict, Any, Optional
from brain.core.service_config import KNOWLEDGE_SERVICE_URL, RETRIEVAL_SERVICE_URL, EXECUTION_SERVICE_URL

class BrainClient:
    """
    Unified API Gateway SDK Client orchestrating the distributed microservices:
    - Port 8001: Knowledge & Ingestion Service
    - Port 8002: Retrieval & Context Service
    - Port 8003: Execution Integration Service
    """
    def __init__(
        self,
        knowledge_url: str = KNOWLEDGE_SERVICE_URL,
        retrieval_url: str = RETRIEVAL_SERVICE_URL,
        execution_url: str = EXECUTION_SERVICE_URL
    ):
        self.knowledge_url = knowledge_url.rstrip("/")
        self.retrieval_url = retrieval_url.rstrip("/")
        self.execution_url = execution_url.rstrip("/")

    # --- 1. Knowledge & Ingestion Router (8001) ---

    def create_project(self, name: str, summary: str = "", description: str = "") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.knowledge_url}/projects",
            json={"name": name, "summary": summary, "description": description}
        )
        resp.raise_for_status()
        return resp.json()

    def ingest_directory(self, directory_path: str, project_name: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.knowledge_url}/ingest/directory",
            json={"directory_path": directory_path, "project_name": project_name}
        )
        resp.raise_for_status()
        return resp.json()

    def remember(self, id: str, obj_type: str, project: str, title: str, summary: str, content: str, importance: float = 1.0, confidence: float = 1.0, tags: List[str] = [], **kwargs) -> Dict[str, Any]:
        payload = {
            "id": id,
            "type": obj_type,
            "project": project,
            "title": title,
            "summary": summary,
            "content": content,
            "importance": importance,
            "confidence": confidence,
            "tags": tags
        }
        payload.update(kwargs)
        resp = requests.post(f"{self.knowledge_url}/objects", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_object(self, obj_id: str) -> Dict[str, Any]:
        resp = requests.get(f"{self.knowledge_url}/objects/{obj_id}")
        resp.raise_for_status()
        return resp.json()

    def list_objects(self, project: Optional[str] = None, type: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {}
        if project: params["project"] = project
        if type: params["type"] = type
        resp = requests.get(f"{self.knowledge_url}/objects", params=params)
        resp.raise_for_status()
        return resp.json()

    # --- 2. Retrieval & Context Router (8002) ---

    def get_context(self, project: str, user_goal: str, current_task: Optional[str] = None, token_budget: int = 4000) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.retrieval_url}/context/{project}",
            params={"user_goal": user_goal, "current_task": current_task, "token_budget": token_budget}
        )
        resp.raise_for_status()
        return resp.json()

    def get_graph(self, project: Optional[str] = None) -> Dict[str, Any]:
        params = {"project": project} if project else {}
        resp = requests.get(f"{self.retrieval_url}/graph", params=params)
        resp.raise_for_status()
        return resp.json()

    def create_session(self, project: str, goal: str = "", current_task: str = "", active_files: List[str] = [], branch: str = "main") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.retrieval_url}/sessions",
            json={
                "project": project,
                "goal": goal,
                "current_task": current_task,
                "active_files": active_files,
                "branch": branch
            }
        )
        resp.raise_for_status()
        return resp.json()

    def get_session(self, session_id: str) -> Dict[str, Any]:
        resp = requests.get(f"{self.retrieval_url}/sessions/{session_id}")
        resp.raise_for_status()
        return resp.json()

    def add_session_checkpoint(self, session_id: str, name: str, notes: str = "") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.retrieval_url}/sessions/{session_id}/checkpoints",
            json={"name": name, "notes": notes}
        )
        resp.raise_for_status()
        return resp.json()

    def list_sessions(self, project: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"project": project} if project else {}
        resp = requests.get(f"{self.retrieval_url}/sessions", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_explainability_traces(self) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.retrieval_url}/traces")
        resp.raise_for_status()
        return resp.json()

    # --- 3. Execution Integration Router (8003) ---

    def execute_chatgpt(self, project: str, user_goal: str, user_prompt: str, current_task: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.execution_url}/adapters/chatgpt",
            json={
                "project": project,
                "user_goal": user_goal,
                "current_task": current_task,
                "user_prompt": user_prompt,
                "model": model
            }
        )
        resp.raise_for_status()
        return resp.json()

    def execute_claude(self, project: str, user_goal: str, user_prompt: str, current_task: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.execution_url}/adapters/claude",
            json={
                "project": project,
                "user_goal": user_goal,
                "current_task": current_task,
                "user_prompt": user_prompt,
                "model": model
            }
        )
        resp.raise_for_status()
        return resp.json()

    def submit_feedback(self, obj_id: str, success: bool, feedback: str = "", project: Optional[str] = None) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.execution_url}/feedback",
            json={"id": obj_id, "success": success, "feedback": feedback, "project": project}
        )
        resp.raise_for_status()
        return resp.json()
