"""Standalone verification script to test duplicate email prevention and read marking."""

import logging
import os
import sys

# Configure UTF-8 stdout encoding for Windows compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure verbose logging for verification
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from src.workflows.email_triage_workflow import EmailTriageWorkflow


def main() -> None:
    """Run verification flow for duplicate email processing prevention."""
    workflow = EmailTriageWorkflow()

    print("========================================", flush=True)
    print("RUN #1: Processing latest unread email...", flush=True)
    print("========================================", flush=True)
    res1 = workflow.process_latest_unread_email()

    if res1:
        email1, triage1, page_id1 = res1
        print(f"\n[RUN 1 RESULT]")
        print(f"Email ID Processed: {email1.id}")
        print(f"Subject: {email1.subject}")
        print(f"Category: {triage1.classification.category.value}")
        print(f"Priority: {triage1.classification.priority.value}")
        print(f"Notion Synced: {triage1.synced_to_notion}")
        print(f"Draft Created: {triage1.draft_created}")
    else:
        print("\n[RUN 1 RESULT]: No unread emails found in inbox.")

    print("\n========================================", flush=True)
    print("RUN #2: Attempting to fetch latest unread email again...", flush=True)
    print("========================================", flush=True)
    res2 = workflow.process_latest_unread_email()

    if res2:
        email2, triage2, page_id2 = res2
        print(f"\n[RUN 2 FAILED DUPLICATE PREVENTION!]")
        print(f"Duplicate Email ID Returned: {email2.id}")
        print(f"Subject: {email2.subject}")
    else:
        print("\n[RUN 2 SUCCESS]: No unread emails found! Duplicate processing prevented successfully.")

    print("========================================", flush=True)


if __name__ == "__main__":
    main()
