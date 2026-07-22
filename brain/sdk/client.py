import requests
from typing import List, Dict, Any, Optional

class BrainClient:
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

    def get_context(self, project: str, user_goal: str, current_task: Optional[str] = None) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/context/{project}",
            params={"user_goal": user_goal, "current_task": current_task}
        )
        resp.raise_for_status()
        return resp.json()

    def remember(self, id: str, obj_type: str, project: str, title: str, summary: str, content: str, importance: float = 1.0, confidence: float = 1.0, tags: List[str] = []) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/remember",
            json={
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
