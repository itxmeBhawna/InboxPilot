"""Standalone verification script for Phase 4A: Notion Dashboard Integration."""

import os
import sys

# Configure UTF-8 stdout encoding for Windows compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.workflows.email_triage_workflow import EmailTriageWorkflow


def main() -> None:
    """Run real email triage pipeline with Notion sync and print results."""
    workflow = EmailTriageWorkflow()

    res = workflow.process_latest_unread_email()

    if not res:
        print("No unread emails found.", flush=True)
        return

    email, triage_result, page_id = res
    classification = triage_result.classification

    sync_status = "True" if triage_result.synced_to_notion else "False"
    page_id_str = page_id if page_id else "None"

    print("========================================", flush=True)
    print("\nSubject:", flush=True)
    print(email.subject, flush=True)
    print("\nNotion Sync:", flush=True)
    print(sync_status, flush=True)
    print("\nNotion Page ID:", flush=True)
    print(page_id_str, flush=True)
    print("\nCategory:", flush=True)
    print(classification.category.value, flush=True)
    print("\nPriority:", flush=True)
    print(classification.priority.value, flush=True)
    print("\n========================================", flush=True)


if __name__ == "__main__":
    main()
