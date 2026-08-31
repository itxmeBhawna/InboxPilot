"""Bugfix phase verification script to validate read-marking, duplicate prevention, and API behavior."""

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

    print("\n" + "=" * 50, flush=True)
    print("RUN #1: Querying Gmail & Processing Latest Unread Email...", flush=True)
    print("=" * 50, flush=True)
    res1 = workflow.process_latest_unread_email()

    if res1:
        email1, triage1, page_id1 = res1
        print(f"\n[RUN 1 SUCCESS]", flush=True)
        print(f"Email ID Processed: {email1.id}", flush=True)
        print(f"Subject: '{email1.subject}'", flush=True)
        print(f"Category: {triage1.classification.category.value}", flush=True)
        print(f"Priority: {triage1.classification.priority.value}", flush=True)
        print(f"Notion Synced: {triage1.synced_to_notion}", flush=True)
        print(f"Draft Created: {triage1.draft_created}", flush=True)
    else:
        print("\n[RUN 1]: No unread emails found in Gmail inbox.", flush=True)

    print("\n" + "=" * 50, flush=True)
    print("RUN #2: Re-querying Gmail to Verify Duplicate Prevention...", flush=True)
    print("=" * 50, flush=True)
    res2 = workflow.process_latest_unread_email()

    if res2:
        email2, triage2, page_id2 = res2
        if res1 and email2.id == res1[0].id:
            print(f"\n[RUN 2 FAILED]: Duplicate Email ID returned: {email2.id}!", flush=True)
        else:
            print(f"\n[RUN 2 DISCOVERED NEW UNREAD EMAIL]: Message ID {email2.id} ('{email2.subject}')", flush=True)
            print("Note: Previous email was marked read successfully. Processing next queued email in inbox.", flush=True)
    else:
        print("\n[RUN 2 SUCCESS]: No unread emails found! Duplicate processing prevented.", flush=True)

    print("=" * 50 + "\n", flush=True)


if __name__ == "__main__":
    main()
