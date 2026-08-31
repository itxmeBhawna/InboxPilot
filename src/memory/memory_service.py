"""High-level memory orchestrator coordinating preference storage and user feedback memory.

Privacy-First Memory Design:
InboxPilot intentionally avoids retaining full inbox contents or email bodies long-term.
This service coordinates storage for user feedback corrections, learned rules,
and lightweight metadata necessary for agent personalization.
"""

import logging
from typing import Any, Dict, List, Optional

from src.config.settings import Settings, get_settings
from src.memory.feedback_memory import FeedbackMemory
from src.memory.user_preferences import UserPreferencesMemory
from src.models.email_models import UserFeedback

logger = logging.getLogger(__name__)


class MemoryService:
    """Orchestrates memory operations combining user preferences and feedback history."""

    def __init__(
        self,
        preferences_memory: Optional[UserPreferencesMemory] = None,
        feedback_memory: Optional[FeedbackMemory] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        """Initialize MemoryService with sub-memory components.

        Args:
            preferences_memory: Component for managing learned user rules and sender preferences.
            feedback_memory: Component for recording user corrections.
            settings: Global application settings.
        """
        self.settings = settings or get_settings()
        self.feedback = feedback_memory or FeedbackMemory(settings=self.settings)
        self.preferences = preferences_memory or UserPreferencesMemory(
            feedback_memory=self.feedback, settings=self.settings
        )

    def record_feedback(
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
        """Record user feedback correction to memory storage.

        Args:
            email_id: Target email message ID.
            sender: Sender email address.
            predicted_priority: Priority predicted by agent.
            user_priority: Priority selected by user.
            predicted_category: Category predicted by agent.
            user_category: Category selected by user.
            subject: Subject header of email.
            feedback_reason: Optional explanation by user.
            category_at_feedback_time: Optional category snapshot.
            priority_at_feedback_time: Optional priority snapshot.

        Returns:
            Recorded feedback entry dictionary.
        """
        return self.feedback.save_feedback(
            email_id=email_id,
            sender=sender,
            predicted_priority=predicted_priority,
            user_priority=user_priority,
            predicted_category=predicted_category,
            user_category=user_category,
            subject=subject,
            feedback_reason=feedback_reason,
            category_at_feedback_time=category_at_feedback_time,
            priority_at_feedback_time=priority_at_feedback_time,
        )

    def get_sender_preferences(self, sender: str) -> Dict[str, Any]:
        """Retrieve aggregated sender preferences calculated from historical feedback.

        Args:
            sender: Target sender email address.

        Returns:
            Dict containing preferred_priority, confidence score, and feedback_count.
        """
        return self.preferences.get_sender_preferences(sender)

    def get_feedback_history(self, sender: Optional[str] = None) -> List[dict]:
        """Fetch stored feedback records, optionally filtered by sender address.

        Args:
            sender: Optional sender email address filter.

        Returns:
            List of feedback record dictionaries.
        """
        return self.feedback.get_feedback_history(sender=sender)

    async def get_agent_context(self, user_id: str = "default") -> Dict[str, Any]:
        """Assemble personalization context for the AI agent."""
        user_prefs = await self.preferences.get_user_preferences(user_id=user_id)
        recent_corrections = await self.feedback.get_recent_feedback(limit=20, user_id=user_id)

        return {
            "preferences": user_prefs,
            "recent_corrections": recent_corrections,
        }

    async def save_user_feedback(self, feedback: UserFeedback) -> bool:
        """Record user feedback correction asynchronously."""
        return await self.feedback.record_feedback(feedback)

    async def log_audit_event(
        self, event_type: str, email_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record lightweight, privacy-compliant audit log entry for triage actions."""
        logger.info("Audit log [%s] for email ID %s: %s", event_type, email_id, metadata or {})
