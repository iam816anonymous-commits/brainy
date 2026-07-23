import requests
from typing import List, Dict, Any, Optional

class BrainClient:
    """
    The canonical Python Client SDK for the AI Context Operating System.
    """
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def create_project(self, name: str, summary: str = "", description: str = "") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/projects",
            json={"name": name, "summary": summary, "description": description}
        )
        resp.raise_for_status()
        return resp.json()

    def create_task(self, project: str, task: str, active_files: List[str] = [], branch: str = "main", errors: List[str] = []) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/tasks",
            json={
                "project": project,
                "task": task,
                "active_files": active_files,
                "branch": branch,
                "errors": errors
            }
        )
        resp.raise_for_status()
        return resp.json()

    def get_context(self, project: str, user_goal: str, current_task: Optional[str] = None, token_budget: int = 4000) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/context/{project}",
            params={"user_goal": user_goal, "current_task": current_task, "token_budget": token_budget}
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
        # Mix in platform engineering properties
        payload.update(kwargs)

        resp = requests.post(
            f"{self.base_url}/remember",
            json=payload
        )
        resp.raise_for_status()
        return resp.json()

    def submit_feedback(self, obj_id: str, success: bool, feedback: str = "") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/feedback",
            json={"id": obj_id, "success": success, "feedback": feedback}
        )
        resp.raise_for_status()
        return resp.json()

    def get_graph(self, project: Optional[str] = None) -> Dict[str, Any]:
        params = {"project": project} if project else {}
        resp = requests.get(f"{self.base_url}/graph", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_timeline(self, project: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"project": project} if project else {}
        resp = requests.get(f"{self.base_url}/timeline", params=params)
        resp.raise_for_status()
        return resp.json()

    # --- Resumable Context Sessions ---

    def create_session(self, project: str, goal: str = "", current_task: str = "", active_files: List[str] = [], branch: str = "main") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/sessions",
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
        resp = requests.get(f"{self.base_url}/sessions/{session_id}")
        resp.raise_for_status()
        return resp.json()

    def add_session_checkpoint(self, session_id: str, name: str, notes: str = "") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/sessions/{session_id}/checkpoints",
            json={"name": name, "notes": notes}
        )
        resp.raise_for_status()
        return resp.json()

    def list_sessions(self, project: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"project": project} if project else {}
        resp = requests.get(f"{self.base_url}/sessions", params=params)
        resp.raise_for_status()
        return resp.json()

    # --- Observability Traces ---

    def get_explainability_traces(self) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.base_url}/traces")
        resp.raise_for_status()
        return resp.json()
