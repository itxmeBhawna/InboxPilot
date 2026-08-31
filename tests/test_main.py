"""Unit tests for InboxPilot main API endpoints and models."""

from datetime import datetime, timezone
from fastapi.testclient import TestClient
from src.main import app
from src.models.email_models import (
    CategoryEnum,
    EmailClassification,
    EmailMessage,
    PriorityEnum,
    UserFeedback,
)

client = TestClient(app)


def test_health_check():
    """Verify GET /health returns 200 OK with expected JSON structure."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "InboxPilot",
    }


def test_category_enum_values():
    """Verify expanded CategoryEnum contains all required triage categories."""
    expected_categories = {
        "ACTION_REQUIRED",
        "MEETING",
        "APPLICATION",
        "FINANCE",
        "NEWSLETTER",
        "PROMOTION",
        "SPAM_SCAM",
        "PERSONAL",
        "OTHER",
    }
    actual_categories = {category.value for category in CategoryEnum}
    assert expected_categories == actual_categories


def test_user_feedback_model():
    """Verify UserFeedback Pydantic model creation and validation."""
    feedback = UserFeedback(
        email_id="msg_12345",
        predicted_priority=PriorityEnum.HIGH,
        user_priority=PriorityEnum.LOW,
        predicted_category=CategoryEnum.ACTION_REQUIRED,
        user_category=CategoryEnum.NEWSLETTER,
        feedback_reason="Sender always sends automated weekly updates.",
    )
    assert feedback.email_id == "msg_12345"
    assert feedback.predicted_priority == PriorityEnum.HIGH
    assert feedback.user_priority == PriorityEnum.LOW
    assert feedback.predicted_category == CategoryEnum.ACTION_REQUIRED
    assert feedback.user_category == CategoryEnum.NEWSLETTER
    assert feedback.feedback_reason == "Sender always sends automated weekly updates."
    assert isinstance(feedback.created_at, datetime)
