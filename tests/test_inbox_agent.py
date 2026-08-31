"""Unit tests for InboxAgent AI classification pipeline, parsing, validation, and reply drafting."""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.agent.exceptions import InvalidAgentOutputError
from src.agent.inbox_agent import InboxAgent
from src.models.email_models import CategoryEnum, EmailMessage, PriorityEnum


def create_mock_agent(mock_response_text: str) -> InboxAgent:
    """Helper to instantiate an InboxAgent with a mocked Gemini client returning specific raw text."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = mock_response_text
    mock_client.models.generate_content.return_value = mock_response
    return InboxAgent(client=mock_client)


def test_analyze_internship_opportunity():
    """Verify classification pipeline for a legitimate internship opportunity email."""
    mock_json = json.dumps({
        "category": "APPLICATION",
        "priority": "HIGH",
        "spam_score": 5.0,
        "summary": "Invitation to schedule a technical interview for Summer 2026 Software Engineer Internship.",
        "reasoning": "Legitimate recruiter outreach regarding an active job application requiring interview scheduling.",
        "reply_needed": True,
        "draft_reply": "Hi Sarah,\n\nThank you for reaching out! I would love to schedule the technical interview. I am available this Thursday and Friday afternoon.\n\nBest regards,\nCandidate",
    })
    agent = create_mock_agent(mock_json)

    email = EmailMessage(
        id="msg_intern_01",
        thread_id="thread_intern_01",
        sender="sarah.recruiter@techcorp.com",
        recipient="user@example.com",
        subject="Software Engineering Internship - Interview Invitation",
        snippet="We reviewed your application and would like to invite you for an interview...",
        body="Dear Candidate,\n\nWe reviewed your application for the Software Engineering Internship position at TechCorp. We were very impressed with your background and would like to schedule a 45-minute technical interview.\n\nPlease reply with your availability for next week.\n\nBest regards,\nSarah Johnson\nTechCorp Talent Acquisition",
        received_at=datetime.now(timezone.utc),
        labels=["INBOX", "IMPORTANT"],
    )

    result = agent.analyze_email(email)

    assert result.email_id == "msg_intern_01"
    assert result.classification.category == CategoryEnum.APPLICATION
    assert result.classification.priority == PriorityEnum.HIGH
    assert result.classification.spam_score == 5.0
    assert "interview" in result.classification.summary.lower()
    assert result.draft_reply is not None
    assert "Thank you for reaching out" in result.draft_reply


def test_analyze_meeting_invite():
    """Verify classification pipeline for a team meeting request email."""
    mock_json = json.dumps({
        "category": "MEETING",
        "priority": "HIGH",
        "spam_score": 0.0,
        "summary": "Request to sync on Q3 roadmap and project milestones tomorrow at 2 PM.",
        "reasoning": "Direct meeting invitation from a team manager requiring scheduling confirmation.",
        "reply_needed": True,
        "draft_reply": "Hi Alex,\n\nI have reviewed the proposed time and 2 PM tomorrow works great for me. See you then!\n\nBest,\nUser",
    })
    agent = create_mock_agent(mock_json)

    email = EmailMessage(
        id="msg_meeting_02",
        thread_id="thread_meeting_02",
        sender="alex.manager@company.com",
        recipient="user@example.com",
        subject="Sync on Q3 Roadmap & Milestones",
        snippet="Can we meet tomorrow at 2 PM to review Q3 roadmap deliverables?",
        body="Hi team,\n\nCan we set up a quick 30-minute sync tomorrow at 2 PM PST to align on our Q3 project roadmap deliverables?\n\nLet me know if this time works for everyone.\n\nBest,\nAlex",
        received_at=datetime.now(timezone.utc),
        labels=["INBOX", "WORK"],
    )

    result = agent.analyze_email(email)

    assert result.email_id == "msg_meeting_02"
    assert result.classification.category == CategoryEnum.MEETING
    assert result.classification.priority == PriorityEnum.HIGH
    assert result.classification.spam_score == 0.0
    assert result.draft_reply is not None
    assert "2 PM tomorrow works" in result.draft_reply


def test_analyze_newsletter():
    """Verify classification pipeline for a tech newsletter digest (no reply should be drafted)."""
    mock_json = json.dumps({
        "category": "NEWSLETTER",
        "priority": "LOW",
        "spam_score": 2.0,
        "summary": "Weekly issue summarizing recent updates in AI architecture and developer tools.",
        "reasoning": "Automated broadcast publication sent to subscribers. No direct action or reply needed.",
        "reply_needed": False,
        "draft_reply": None,
    })
    agent = create_mock_agent(mock_json)

    email = EmailMessage(
        id="msg_newsletter_03",
        thread_id="thread_newsletter_03",
        sender="updates@techdigest.io",
        recipient="user@example.com",
        subject="Tech Weekly Digest #142: Breakthroughs in LLM Reasoning",
        snippet="Here are the top stories in software engineering and AI this week...",
        body="Welcome to Tech Weekly Digest #142!\n\nIn this issue:\n1. Latest developments in AI reasoning engines.\n2. Standardizing API contracts in distributed microservices.\n\nClick here to read the full issue online.\n\nTo unsubscribe, click the link below.",
        received_at=datetime.now(timezone.utc),
        labels=["INBOX", "NEWSLETTER"],
    )

    result = agent.analyze_email(email)

    assert result.email_id == "msg_newsletter_03"
    assert result.classification.category == CategoryEnum.NEWSLETTER
    assert result.classification.priority == PriorityEnum.LOW
    assert result.classification.spam_score <= 10.0
    assert result.draft_reply is None


def test_analyze_scam_internship():
    """Verify classification pipeline for a fraudulent scam internship email (high spam score, no reply)."""
    mock_json = json.dumps({
        "category": "SPAM_SCAM",
        "priority": "LOW",
        "spam_score": 95.0,
        "summary": "Fraudulent internship offer requiring an immediate $150 wire transfer processing fee.",
        "reasoning": "Classic phishing scam demanding upfront payment for a fake remote position from an unverified domain.",
        "reply_needed": False,
        "draft_reply": None,
    })
    agent = create_mock_agent(mock_json)

    email = EmailMessage(
        id="msg_scam_04",
        thread_id="thread_scam_04",
        sender="hr-urgent-offer992@suspicious-job-portal.xyz",
        recipient="user@example.com",
        subject="URGENT: Guaranteed Remote Internship Offer - Earn $4000/Week!",
        snippet="Congratulations! You are selected. Wire $150 registration fee immediately...",
        body="CONGRATULATIONS!\n\nYou have been selected for our High-Paying Remote Global Internship! Earn $4,000 per week working 5 hours.\n\nTo secure your position and receive your company laptop, you MUST wire transfer a $150 background check processing fee via Gift Card or Zelle within 24 hours.\n\nClick link to submit payment immediately!",
        received_at=datetime.now(timezone.utc),
        labels=["INBOX", "SPAM"],
    )

    result = agent.analyze_email(email)

    assert result.email_id == "msg_scam_04"
    assert result.classification.category == CategoryEnum.SPAM_SCAM
    assert result.classification.priority == PriorityEnum.LOW
    assert result.classification.spam_score >= 80.0
    assert result.draft_reply is None


def test_analyze_bank_alert():
    """Verify classification pipeline for an urgent bank financial notification."""
    mock_json = json.dumps({
        "category": "FINANCE",
        "priority": "HIGH",
        "spam_score": 0.0,
        "summary": "Official bank security alert notifying of a new sign-in attempt from an unrecognized device.",
        "reasoning": "Critical account security notice requiring immediate user review of account access history.",
        "reply_needed": False,
        "draft_reply": None,
    })
    agent = create_mock_agent(mock_json)

    email = EmailMessage(
        id="msg_bank_05",
        thread_id="thread_bank_05",
        sender="security@firstnationalbank.com",
        recipient="user@example.com",
        subject="Security Notice: New Login Attempt Detected",
        snippet="We detected a new login to your online banking account from Chrome on Linux...",
        body="Dear Customer,\n\nWe detected a sign-in attempt to your online banking account on August 31 at 12:15 PM UTC from an unrecognized device (Chrome on Linux).\n\nIf this was you, no action is needed. If you did not authorize this login, please sign in to your official mobile banking app immediately to freeze your card and update your password.\n\nFirst National Bank Security Team",
        received_at=datetime.now(timezone.utc),
        labels=["INBOX", "FINANCE"],
    )

    result = agent.analyze_email(email)

    assert result.email_id == "msg_bank_05"
    assert result.classification.category == CategoryEnum.FINANCE
    assert result.classification.priority == PriorityEnum.HIGH
    assert result.classification.spam_score == 0.0
    assert result.draft_reply is None


def test_malformed_json_raises_custom_exception():
    """Verify that malformed unparseable JSON from Gemini raises InvalidAgentOutputError."""
    agent = create_mock_agent("This is invalid raw text, not JSON at all!")

    email = EmailMessage(
        id="msg_err_01",
        thread_id="thread_err_01",
        sender="sender@example.com",
        recipient="user@example.com",
        subject="Test Error Subject",
        snippet="Test snippet",
        body="Test body",
    )

    with pytest.raises(InvalidAgentOutputError) as exc_info:
        agent.analyze_email(email)

    assert "not valid JSON" in str(exc_info.value)
    assert exc_info.value.raw_output == "This is invalid raw text, not JSON at all!"


def test_missing_schema_field_raises_custom_exception():
    """Verify that JSON missing required fields (e.g. missing category) raises InvalidAgentOutputError."""
    incomplete_json = json.dumps({
        "priority": "HIGH",
        "spam_score": 0.0,
        "summary": "Missing category field",
        "reasoning": "Missing required fields",
        "reply_needed": False,
        "draft_reply": None,
    })
    agent = create_mock_agent(incomplete_json)

    email = EmailMessage(
        id="msg_err_02",
        thread_id="thread_err_02",
        sender="sender@example.com",
        recipient="user@example.com",
        subject="Test Incomplete Subject",
        snippet="Test snippet",
        body="Test body",
    )

    with pytest.raises(InvalidAgentOutputError) as exc_info:
        agent.analyze_email(email)

    assert "missing required fields" in str(exc_info.value).lower()


def test_invalid_enum_category_raises_custom_exception():
    """Verify that an invalid category enum string raises InvalidAgentOutputError."""
    invalid_category_json = json.dumps({
        "category": "SUPER_INVALID_CATEGORY",
        "priority": "HIGH",
        "spam_score": 0.0,
        "summary": "Test summary",
        "reasoning": "Test reasoning",
        "reply_needed": False,
        "draft_reply": None,
    })
    agent = create_mock_agent(invalid_category_json)

    email = EmailMessage(
        id="msg_err_03",
        thread_id="thread_err_03",
        sender="sender@example.com",
        recipient="user@example.com",
        subject="Test Invalid Enum",
        snippet="Test snippet",
        body="Test body",
    )

    with pytest.raises(InvalidAgentOutputError) as exc_info:
        agent.analyze_email(email)

    assert "Invalid category value" in str(exc_info.value)
