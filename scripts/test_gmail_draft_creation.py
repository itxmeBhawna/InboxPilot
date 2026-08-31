"""Standalone verification script for Phase 5A: Gmail Draft Creation."""

import os
import sys

# Configure UTF-8 stdout encoding for Windows compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.workflows.email_triage_workflow import EmailTriageWorkflow


def main() -> None:
    """Run real email triage pipeline with Notion sync and Gmail draft creation."""
    workflow = EmailTriageWorkflow()

    res = workflow.process_latest_unread_email()

    if not res:
        print("No unread emails found.", flush=True)
        return

    email, triage_result, page_id = res
    classification = triage_result.classification

    reply_needed_str = "True" if classification.reply_needed else "False"
    draft_created_str = "True" if triage_result.draft_created else "False"
    draft_id_str = triage_result.draft_id if triage_result.draft_id else "None"

    print("========================================", flush=True)
    print("\nSubject:", flush=True)
    print(email.subject, flush=True)
    print("\nReply Needed:", flush=True)
    print(reply_needed_str, flush=True)
    print("\nDraft Created:", flush=True)
    print(draft_created_str, flush=True)
    print("\nDraft ID:", flush=True)
    print(draft_id_str, flush=True)
    print("\n========================================", flush=True)


if __name__ == "__main__":
    main()
