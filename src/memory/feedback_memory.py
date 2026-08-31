"""Feedback memory handler for recording and retrieving classification correction history."""

import logging
from typing import List, Optional
from src.config.settings import Settings, get_settings
from src.models.email_models import UserFeedback

logger = logging.getLogger(__name__)


class FeedbackMemory:
    """Manages UserFeedback records when the user overrides an agent classification decision.

    Privacy Note: Stores metadata about misclassification (predicted vs actual category/priority
    and optional user feedback reason), but strictly avoids storing full email content.
    """

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initialize feedback memory client.

        Args:
            settings: Application settings instance (defaults to global settings).
        """
        self.settings = settings or get_settings()
        # TODO: Initialize Firestore feedback collection reference

    async def record_feedback(self, feedback: UserFeedback) -> bool:
        """Store a user feedback correction record.

        Args:
            feedback: Structured UserFeedback object containing predictions and corrections.

        Returns:
            Boolean indicating successful storage.
        """
        # TODO: Implement Firestore persistence for feedback record
        logger.info(
            "Recording user feedback for email %s: Priority (%s -> %s), Category (%s -> %s)",
            feedback.email_id,
            feedback.predicted_priority,
            feedback.user_priority,
            feedback.predicted_category,
            feedback.user_category,
        )
        return True

    async def get_recent_feedback(
        self, limit: int = 50, user_id: str = "default"
    ) -> List[UserFeedback]:
        """Fetch recent user feedback corrections for model fine-tuning or context prompt assembly.

        Args:
            limit: Maximum number of feedback records to retrieve.
            user_id: User identifier.

        Returns:
            List of historical UserFeedback entries.
        """
        # TODO: Implement Firestore query ordering by created_at desc with limit
        logger.info("Fetching recent %d feedback records for user %s", limit, user_id)
        return []
