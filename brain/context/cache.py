import time
from typing import Dict, Any, Optional, Tuple
from brain.context.assembler import ContextPackage

class ContextCache:
    """
    Subsystem inside the Context Layer that caches computed ContextPackage instances,
    preventing duplicate retrieval and ranking operations.
    """
    _cache: Dict[Tuple[str, str, str], Tuple[ContextPackage, float]] = {}

    @classmethod
    def _make_key(cls, project: str, user_goal: str, current_task: Optional[str]) -> Tuple[str, str, str]:
        return (project.lower(), user_goal.lower().strip(), (current_task or "").lower().strip())

    @classmethod
    def get(cls, project: str, user_goal: str, current_task: Optional[str], ttl_seconds: float = 30.0) -> Optional[ContextPackage]:
        """
        Retrieves cached ContextPackage if it exists and falls within the TTL window.
        """
        key = cls._make_key(project, user_goal, current_task)
        if key in cls._cache:
            package, timestamp = cls._cache[key]
            if time.time() - timestamp <= ttl_seconds:
                return package
            else:
                # Evict expired item
                del cls._cache[key]
        return None

    @classmethod
    def set(cls, project: str, user_goal: str, current_task: Optional[str], package: ContextPackage) -> None:
        """
        Saves computed ContextPackage into the global cache with a timestamp.
        """
        key = cls._make_key(project, user_goal, current_task)
        cls._cache[key] = (package, time.time())

    @classmethod
    def clear(cls) -> None:
        cls._cache.clear()
