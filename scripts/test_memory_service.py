"""Standalone verification script for Phase 5B: MemoryService Orchestration."""

import os
import sys

# Configure UTF-8 stdout encoding for Windows compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.memory.memory_service import MemoryService


def main() -> None:
    """Test MemoryService orchestration without external Gmail, Gemini, or Notion dependencies."""
    memory_service = MemoryService()

    sender = "support@service.com"

    # 1. Test record_feedback()
    rec1 = memory_service.record_feedback(
        email_id="srv_01",
        sender=sender,
        subject="Monthly Invoice",
        predicted_priority="LOW",
        user_priority="HIGH",
        predicted_category="PROMOTION",
        user_category="FINANCE",
        feedback_reason="Billing issues must be handled quickly",
    )

    rec2 = memory_service.record_feedback(
        email_id="srv_02",
        sender=sender,
        subject="Payment Receipt",
        predicted_priority="MEDIUM",
        user_priority="HIGH",
        predicted_category="FINANCE",
        user_category="FINANCE",
        feedback_reason="Finance items are high priority",
    )

    # 2. Test feedback retrieval
    history = memory_service.get_feedback_history(sender=sender)
    assert len(history) >= 2, f"Expected at least 2 history items for {sender}, got {len(history)}"

    # 3. Test preference aggregation
    prefs = memory_service.get_sender_preferences(sender=sender)
    assert prefs["preferred_priority"] == "HIGH", f"Expected preferred_priority HIGH, got {prefs['preferred_priority']}"
    assert prefs["feedback_count"] >= 2, f"Expected feedback_count >= 2, got {prefs['feedback_count']}"

    print("========================================", flush=True)
    print("MemoryService Verification Successful!", flush=True)
    print("\nSender:", flush=True)
    print(sender, flush=True)
    print("\nTotal Records Retained:", flush=True)
    print(len(history), flush=True)
    print("\nAggregated Preferences:", flush=True)
    print(f"Preferred Priority: {prefs['preferred_priority']}", flush=True)
    print(f"Confidence: {prefs['confidence']}", flush=True)
    print(f"Feedback Count: {prefs['feedback_count']}", flush=True)
    print("\nLatest Stored Subject:", flush=True)
    print(history[-1].get("subject", ""), flush=True)
    print("========================================", flush=True)


if __name__ == "__main__":
    main()
