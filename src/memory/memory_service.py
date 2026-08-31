"""High-level memory orchestrator coordinating preference storage and user feedback memory.

Privacy-First Memory Design:
InboxPilot intentionally avoids retaining full inbox contents or email bodies long-term.
This service only coordinates storage for user feedback corrections, learned rules,
and lightweight audit metadata necessary for agent personalization.
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
        self.preferences = preferences_memory or UserPreferencesMemory(settings=self.settings)
        self.feedback = feedback_memory or FeedbackMemory(settings=self.settings)
        # TODO: Initialize Firestore connection for audit metadata

    async def get_agent_context(self, user_id: str = "default") -> Dict[str, Any]:
        """Assemble personalization context for the AI agent (preferences + recent feedback).

        Args:
            user_id: User identifier.

        Returns:
            Dictionary containing user preferences and past corrections to inject into agent prompt.
        """
        # TODO: Fetch preferences and recent corrections to construct dynamic context window
        user_prefs = await self.preferences.get_user_preferences(user_id=user_id)
        recent_corrections = await self.feedback.get_recent_feedback(limit=20, user_id=user_id)

        return {
            "preferences": user_prefs,
            "recent_corrections": recent_corrections,
        }

    async def save_user_feedback(self, feedback: UserFeedback) -> bool:
        """Record user feedback correction and update learned rules if applicable.

        Args:
            feedback: Structured feedback object.

        Returns:
            Boolean indicating successful memory update.
        """
        success = await self.feedback.record_feedback(feedback)
        # TODO: Trigger background rule update in user_preferences based on feedback analysis
        return success

    async def log_audit_event(
        self, event_type: str, email_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record lightweight, privacy-compliant audit log entry for triage actions.

        Args:
            event_type: Type of event (e.g. "EMAIL_TRIAGED", "DRAFT_GENERATED").
            email_id: Target email ID.
            metadata: Non-sensitive operational metadata (e.g. processing time, priority score).
        """
        # TODO: Write audit event to Firestore logs collection without email body text
        logger.info("Audit log [%s] for email ID %s: %s", event_type, email_id, metadata or {})
