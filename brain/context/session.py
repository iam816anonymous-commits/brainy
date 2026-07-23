import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ContextSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project: str
    goal: str = ""
    current_task: str = ""
    active_files: List[str] = Field(default_factory=list)
    branch: str = "main"
    checkpoints: List[Dict[str, Any]] = Field(default_factory=list) # checkpoints of achievements
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ContextSessionManager:
    """
    Subsystem inside the Context Layer that manages active, paused, and resumed Context Sessions.
    """
    _sessions: Dict[str, ContextSession] = {}

    @classmethod
    def create_session(
        cls,
        project: str,
        goal: str = "",
        current_task: str = "",
        active_files: List[str] = [],
        branch: str = "main"
    ) -> ContextSession:
        """
        Creates a new context session.
        """
        session = ContextSession(
            project=project,
            goal=goal,
            current_task=current_task,
            active_files=active_files,
            branch=branch
        )
        cls._sessions[session.id] = session
        return session

    @classmethod
    def get_session(cls, session_id: str) -> Optional[ContextSession]:
        """
        Retrieves a session by its unique ID.
        """
        return cls._sessions.get(session_id)

    @classmethod
    def add_checkpoint(cls, session_id: str, checkpoint_name: str, notes: str = "") -> Optional[ContextSession]:
        """
        Records a checkpoint state inside an active session.
        """
        session = cls.get_session(session_id)
        if session:
            session.checkpoints.append({
                "name": checkpoint_name,
                "notes": notes,
                "timestamp": uuid.uuid4().hex[:6]  # simplified revision marker
            })
        return session

    @classmethod
    def list_sessions(cls, project: Optional[str] = None) -> List[ContextSession]:
        """
        Lists all sessions, optionally filtered by project.
        """
        all_s = list(cls._sessions.values())
        if project:
            return [s for s in all_s if s.project.lower() == project.lower()]
        return all_s

    @classmethod
    def clear(cls) -> None:
        cls._sessions.clear()
