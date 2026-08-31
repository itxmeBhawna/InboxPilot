"""Domain models package for InboxPilot."""

from src.models.email_models import (
    CategoryEnum,
    EmailClassification,
    EmailMessage,
    PriorityEnum,
    TriageResult,
    UserFeedback,
)

__all__ = [
    "PriorityEnum",
    "CategoryEnum",
    "EmailMessage",
    "EmailClassification",
    "UserFeedback",
    "TriageResult",
]
