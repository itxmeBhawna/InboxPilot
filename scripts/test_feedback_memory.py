"""Standalone verification script for Phase 5B: User Feedback Memory."""

import os
import sys

# Configure UTF-8 stdout encoding for Windows compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.memory.feedback_memory import FeedbackMemory
from src.memory.user_preferences import UserPreferencesMemory


def main() -> None:
    """Insert sample feedback entries, retrieve them, and calculate sender statistics."""
    feedback_mem = FeedbackMemory()
    pref_mem = UserPreferencesMemory(feedback_memory=feedback_mem)

    sender_email = "hr@company.com"

    # Insert sample feedback entries
    feedback_mem.save_feedback(
        email_id="msg_001",
        sender=sender_email,
        subject="Interview Schedule",
        predicted_priority="MEDIUM",
        user_priority="HIGH",
        predicted_category="APPLICATION",
        user_category="APPLICATION",
        feedback_reason="Recruiter emails are always high priority",
    )

    feedback_mem.save_feedback(
        email_id="msg_002",
        sender=sender_email,
        subject="Offer Letter Details",
        predicted_priority="MEDIUM",
        user_priority="HIGH",
        predicted_category="APPLICATION",
        user_category="APPLICATION",
        feedback_reason="Important offer communication",
    )

    feedback_mem.save_feedback(
        email_id="msg_003",
        sender=sender_email,
        subject="Weekly Newsletter",
        predicted_priority="LOW",
        user_priority="MEDIUM",
        predicted_category="NEWSLETTER",
        user_category="NEWSLETTER",
        feedback_reason="Company updates are medium priority",
    )

    # Read back feedback history
    history = feedback_mem.get_feedback_history(sender=sender_email)

    # Generate sender preference statistics
    stats = pref_mem.get_sender_preferences(sender=sender_email)

    print("========================================", flush=True)
    print("\nSender:", flush=True)
    print(sender_email, flush=True)
    print("\nFeedback Count:", flush=True)
    print(stats["feedback_count"], flush=True)
    print("\nPreferred Priority:", flush=True)
    print(stats["preferred_priority"], flush=True)
    print("\nConfidence:", flush=True)
    print(stats["confidence"], flush=True)
    print("\n========================================", flush=True)


if __name__ == "__main__":
    main()
