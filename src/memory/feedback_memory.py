"""Feedback memory handler for recording and retrieving classification correction history."""

import json
import logging
import os
from datetime import datetime, timezone
from typing import List, Optional

from src.config.settings import Settings, get_settings
from src.models.email_models import UserFeedback

logger = logging.getLogger(__name__)

DATA_DIR = "data"
FEEDBACK_FILE_PATH = os.path.join(DATA_DIR, "feedback_memory.json")


class FeedbackMemory:
    """Manages UserFeedback records when the user overrides an agent classification decision.

    Stores corrections locally in data/feedback_memory.json without requiring external databases.
    """

    def __init__(
        self,
        file_path: str = FEEDBACK_FILE_PATH,
        settings: Optional[Settings] = None,
    ) -> None:
        """Initialize feedback memory client with JSON file storage path.

        Args:
            file_path: Path to local JSON storage file.
            settings: Application settings instance.
        """
        self.settings = settings or get_settings()
        self.file_path = file_path
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Ensure data directory and JSON storage file exist."""
        dirname = os.path.dirname(self.file_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def save_feedback(
        self,
        email_id: str,
        sender: str,
        predicted_priority: str,
        user_priority: str,
        predicted_category: str,
        user_category: str,
        subject: str = "",
        feedback_reason: Optional[str] = None,
        category_at_feedback_time: Optional[str] = None,
        priority_at_feedback_time: Optional[str] = None,
    ) -> dict:
        """Save a user feedback correction record to local JSON storage.

        Args:
            email_id: Target email ID.
            sender: Sender email address.
            predicted_priority: Agent's predicted priority string.
            user_priority: Corrected priority string chosen by user.
            predicted_category: Agent's predicted category string.
            user_category: Corrected category string chosen by user.
            subject: Email subject header.
            feedback_reason: Optional user rationale text.
            category_at_feedback_time: Optional snapshot category.
            priority_at_feedback_time: Optional snapshot priority.

        Returns:
            Dictionary representing the stored feedback record.
        """
        self._ensure_storage_exists()

        record = {
            "email_id": email_id,
            "sender": sender,
            "subject": subject,
            "predicted_priority": str(predicted_priority),
            "user_priority": str(user_priority),
            "predicted_category": str(predicted_category),
            "user_category": str(user_category),
            "feedback_reason": feedback_reason,
            "category_at_feedback_time": category_at_feedback_time or predicted_category,
            "priority_at_feedback_time": priority_at_feedback_time or predicted_priority,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        history = self.get_feedback_history()
        history.append(record)

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        logger.info(
            "Saved feedback record for sender '%s' (email ID: %s): Priority (%s -> %s)",
            sender,
            email_id,
            predicted_priority,
            user_priority,
        )

        return record

    def get_feedback_history(self, sender: Optional[str] = None) -> List[dict]:
        """Fetch all feedback records, optionally filtered by sender address.

        Args:
            sender: Optional sender email address to filter by.

        Returns:
            List of feedback record dictionaries.
        """
        self._ensure_storage_exists()

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception as e:
            logger.error("Failed to read feedback history from %s: %s", self.file_path, e)
            return []

        if not isinstance(records, list):
            return []

        if sender:
            target_sender = sender.strip().lower()
            return [
                r for r in records
                if isinstance(r, dict) and str(r.get("sender", "")).strip().lower() == target_sender
            ]

        return records

    async def record_feedback(self, feedback: UserFeedback) -> bool:
        """Async compatibility method accepting structured UserFeedback model."""
        self.save_feedback(
            email_id=feedback.email_id,
            sender="unknown@example.com",
            predicted_priority=feedback.predicted_priority.value,
            user_priority=feedback.user_priority.value,
            predicted_category=feedback.predicted_category.value,
            user_category=feedback.user_category.value,
            feedback_reason=feedback.feedback_reason,
        )
        return True

    async def get_recent_feedback(
        self, limit: int = 50, user_id: str = "default"
    ) -> List[UserFeedback]:
        """Async compatibility method returning UserFeedback objects."""
        records = self.get_feedback_history()
        results: List[UserFeedback] = []
        for r in records[:limit]:
            try:
                results.append(
                    UserFeedback(
                        email_id=r.get("email_id", ""),
                        predicted_priority=r.get("predicted_priority", "LOW"),
                        user_priority=r.get("user_priority", "LOW"),
                        predicted_category=r.get("predicted_category", "OTHER"),
                        user_category=r.get("user_category", "OTHER"),
                        feedback_reason=r.get("feedback_reason"),
                    )
                )
            except Exception:
                continue
        return results
