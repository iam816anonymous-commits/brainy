from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from brain.core.db import get_knowledge_object, save_knowledge_object
from brain.memory.manager import remember_failure

class LearningPipeline:
    @staticmethod
    def process_feedback(
        obj_id: str,
        success: bool,
        user_notes: str = "",
        project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes feedback from an AI response outcome.
        """
        obj = get_knowledge_object(obj_id)
        updates = {}

        if obj:
            if success:
                old_conf = obj.confidence
                old_imp = obj.importance
                obj.confidence = min(obj.confidence + 0.1, 1.0)
                obj.importance = min(obj.importance + 0.5, 10.0)
                obj.updated = datetime.now(timezone.utc).isoformat()
                save_knowledge_object(obj)
                updates = {
                    "confidence": f"{old_conf:.2f} -> {obj.confidence:.2f}",
                    "importance": f"{old_imp:.1f} -> {obj.importance:.1f}"
                }
            else:
                old_conf = obj.confidence
                obj.confidence = max(obj.confidence - 0.2, 0.0)
                obj.updated = datetime.now(timezone.utc).isoformat()
                save_knowledge_object(obj)
                updates = {
                    "confidence": f"{old_conf:.2f} -> {obj.confidence:.2f}"
                }

                proj = project_name or obj.project
                remember_failure(
                    project=proj,
                    attempted_action=f"Using node {obj.title} for search query",
                    reason_for_failure=user_notes or "AI context did not produce standard working outcome.",
                    resolution_or_lessons=f"Referenced node {obj.id} had issues. Adjust future prompt weighting."
                )

        return {
            "status": "Learning loop updated successfully",
            "object_id": obj_id,
            "success_registered": success,
            "updates_applied": updates
        }
