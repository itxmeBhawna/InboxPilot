"""Pydantic data models for emails, classifications, user feedback, and triage results."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PriorityEnum(str, Enum):
    """Urgency and importance priority levels for email triage."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CategoryEnum(str, Enum):
    """Expanded categorization scheme supporting real-world inbox classification."""

    ACTION_REQUIRED = "ACTION_REQUIRED"
    MEETING = "MEETING"
    APPLICATION = "APPLICATION"
    FINANCE = "FINANCE"
    NEWSLETTER = "NEWSLETTER"
    PROMOTION = "PROMOTION"
    SPAM_SCAM = "SPAM_SCAM"
    PERSONAL = "PERSONAL"
    OTHER = "OTHER"


class EmailMessage(BaseModel):
    """Metadata and raw content structure of an incoming email message."""

    id: str = Field(..., description="Unique Gmail message ID")
    thread_id: str = Field(..., description="Gmail thread identifier")
    sender: str = Field(..., description="Sender email address or name")
    recipient: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject line")
    snippet: str = Field(..., description="Short text preview of the email body")
    body: str = Field(..., description="Full text content of the email body")
    received_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the email was received",
    )
    labels: List[str] = Field(
        default_factory=list, description="Labels associated with the message"
    )


class EmailClassification(BaseModel):
    """AI agent prediction result for email priority and categorization."""

    priority: PriorityEnum = Field(..., description="Predicted urgency priority")
    category: CategoryEnum = Field(..., description="Predicted email category")
    summary: str = Field(..., description="Concise AI-generated summary of email content")
    spam_score: float = Field(
        ..., ge=0.0, le=100.0, description="Estimated probability or score of spam or scam (0.0 to 100.0)"
    )
    reasoning: str = Field(..., description="Detailed explanation behind the classification")
    reply_needed: bool = Field(
        default=False, description="Whether an email response/reply is needed"
    )


class UserFeedback(BaseModel):
    """User correction model captured when a user overrides an agent classification decision."""

    email_id: str = Field(..., description="Identifier of the target email message")
    predicted_priority: PriorityEnum = Field(
        ..., description="Agent's initial priority prediction"
    )
    user_priority: PriorityEnum = Field(
        ..., description="Corrected priority assigned by the user"
    )
    predicted_category: CategoryEnum = Field(
        ..., description="Agent's initial category prediction"
    )
    user_category: CategoryEnum = Field(
        ..., description="Corrected category assigned by the user"
    )
    feedback_reason: Optional[str] = Field(
        default=None, description="User explanation for the classification correction"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when feedback was submitted",
    )


class TriageResult(BaseModel):
    """Complete summary outcome of the email triage workflow process."""

    email_id: str = Field(..., description="ID of the triaged email")
    classification: EmailClassification = Field(..., description="Classification output")
    draft_reply: Optional[str] = Field(
        default=None, description="Generated reply draft text if applicable"
    )
    synced_to_notion: bool = Field(
        default=False, description="Whether record was written to Notion dashboard"
    )
    draft_created: bool = Field(
        default=False, description="Whether a Gmail draft reply was created"
    )
    draft_id: Optional[str] = Field(
        default=None, description="Gmail Draft ID if created"
    )
    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when triage completed",
    )
