"""Standalone verification script for Phase 6B: Preference-Aware AI Classification."""

import os
import sys

# Configure UTF-8 stdout encoding for Windows compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.inbox_agent import InboxAgent
from src.memory.memory_service import MemoryService
from src.models.email_models import EmailMessage


def main() -> None:
    """Run preference-aware analysis verification workflow."""
    memory_service = MemoryService()

    target_sender = "recruiter@techcorp.com"

    # 1. Insert sample feedback for sender
    memory_service.record_feedback(
        email_id="fb_001",
        sender=target_sender,
        subject="Senior Engineering Opportunity",
        predicted_priority="MEDIUM",
        user_priority="HIGH",
        predicted_category="APPLICATION",
        user_category="APPLICATION",
        feedback_reason="Direct recruiter inquiries are high priority",
    )

    memory_service.record_feedback(
        email_id="fb_002",
        sender=target_sender,
        subject="Follow up on interview scheduling",
        predicted_priority="MEDIUM",
        user_priority="HIGH",
        predicted_category="MEETING",
        user_category="MEETING",
        feedback_reason="Interview scheduling should always be urgent",
    )

    # 2. Fetch sender preferences
    prefs = memory_service.get_sender_preferences(sender=target_sender)

    # 3. Create test EmailMessage and analyze with InboxAgent
    test_email = EmailMessage(
        id="test_msg_pref_001",
        thread_id="test_thread_001",
        sender=target_sender,
        recipient="user@company.com",
        subject="Checking in regarding engineering role",
        snippet="Hi Bhawna, I wanted to touch base regarding your application status.",
        body="Hi Bhawna, I wanted to touch base regarding your application status and see if you have time for a quick call this week.",
    )

    agent = InboxAgent(memory_service=memory_service)
    triage_result = agent.analyze_email(test_email)

    pref_context_used_str = "True" if triage_result.preference_context_used else "False"

    print("========================================", flush=True)
    print("\nSender:", flush=True)
    print(target_sender, flush=True)
    print("\nPreferred Priority:", flush=True)
    print(prefs["preferred_priority"], flush=True)
    print("\nConfidence:", flush=True)
    print(f"{prefs['confidence']:.2f}", flush=True)
    print("\nPreference Context Used:", flush=True)
    print(pref_context_used_str, flush=True)
    print("\nAI Final Priority:", flush=True)
    print(triage_result.classification.priority.value, flush=True)
    print("\n========================================", flush=True)


if __name__ == "__main__":
    main()
