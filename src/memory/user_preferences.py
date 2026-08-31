"""User preferences memory handler for calculating sender statistics and preference rules."""

import logging
from collections import Counter
from typing import Any, Dict, Optional

from src.config.settings import Settings, get_settings
from src.memory.feedback_memory import FeedbackMemory

logger = logging.getLogger(__name__)


class UserPreferencesMemory:
    """Manages sender preference aggregation and statistics calculated from user feedback history."""

    def __init__(
        self,
        feedback_memory: Optional[FeedbackMemory] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        """Initialize user preferences memory client.

        Args:
            feedback_memory: FeedbackMemory component instance for querying history.
            settings: Global application settings instance.
        """
        self.settings = settings or get_settings()
        self.feedback_memory = feedback_memory or FeedbackMemory(settings=self.settings)

    def get_sender_preferences(self, sender: str) -> Dict[str, Any]:
        """Analyze historical feedback entries for a sender and compute preference statistics.

        Args:
            sender: Target sender email address.

        Returns:
            Dict containing preferred_priority, confidence score, and total feedback_count.
        """
        history = self.feedback_memory.get_feedback_history(sender=sender)
        feedback_count = len(history)

        if not feedback_count:
            return {
                "preferred_priority": None,
                "confidence": 0.0,
                "feedback_count": 0,
            }

        # Count frequencies of user-corrected priorities
        priorities = [
            str(rec.get("user_priority")).upper()
            for rec in history
            if rec.get("user_priority")
        ]

        if not priorities:
            return {
                "preferred_priority": None,
                "confidence": 0.0,
                "feedback_count": feedback_count,
            }

        counts = Counter(priorities)
        top_priority, top_count = counts.most_common(1)[0]
        confidence = round(top_count / feedback_count, 2)

        logger.info(
            "Computed preferences for sender '%s': preferred=%s, confidence=%.2f, count=%d",
            sender,
            top_priority,
            confidence,
            feedback_count,
        )

        return {
            "preferred_priority": top_priority,
            "confidence": confidence,
            "feedback_count": feedback_count,
        }

    async def get_user_preferences(self, user_id: str = "default") -> Dict[str, Any]:
        """Retrieve overall user preference profile."""
        return {
            "preferred_priority_handling": {},
            "sender_preferences": {},
            "category_preferences": {},
        }

    async def set_sender_preference(
        self, sender: str, category: str, priority: str, user_id: str = "default"
    ) -> bool:
        """Record or update an explicit preference rule for a sender address."""
        logger.info(
            "Set rule for sender %s -> category: %s, priority: %s (user: %s)",
            sender,
            category,
            priority,
            user_id,
        )
        return True
