"""Standalone verification script for Phase 3B: Real Email Analysis Pipeline (Gmail -> Gemini)."""

import os
import sys

# Configure UTF-8 stdout encoding to avoid Windows console UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.workflows.email_triage_workflow import EmailTriageWorkflow


def main() -> None:
    """Run real email triage pipeline via EmailTriageWorkflow and display output."""
    workflow = EmailTriageWorkflow()

    res = workflow.process_latest_unread_email()

    if not res:
        print("No unread emails found.", flush=True)
        return

    email, triage_result = res
    classification = triage_result.classification

    reply_needed_str = "true" if triage_result.draft_reply is not None else "false"
    draft_reply_str = (
        triage_result.draft_reply
        if triage_result.draft_reply is not None
        else "None"
    )

    print("==================================================", flush=True)
    print("\nSubject:", flush=True)
    print(email.subject, flush=True)
    print("\nSender:", flush=True)
    print(email.sender, flush=True)
    print("\nCategory:", flush=True)
    print(classification.category.value, flush=True)
    print("\nPriority:", flush=True)
    print(classification.priority.value, flush=True)
    print("\nSpam Score:", flush=True)
    print(classification.spam_score, flush=True)
    print("\nSummary:", flush=True)
    print(classification.summary, flush=True)
    print("\nReasoning:", flush=True)
    print(classification.reasoning, flush=True)
    print("\nReply Needed:", flush=True)
    print(reply_needed_str, flush=True)
    print("\nDraft Reply:", flush=True)
    print(draft_reply_str, flush=True)
    print("\n==================================================", flush=True)


if __name__ == "__main__":
    main()
