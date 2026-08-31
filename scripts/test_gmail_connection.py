"""Standalone test script for verifying Gmail API OAuth authentication and unread email retrieval."""

import os
import sys

# Reconfigure stdout to use utf-8 encoding to prevent Windows cp1252 console UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.gmail.gmail_service import GmailService


def main() -> None:
    """Authenticate with Gmail and fetch the latest unread email message."""
    print("Initializing GmailService...", flush=True)
    gmail_service = GmailService()

    print("Authenticating with Gmail API...", flush=True)
    gmail_service.get_service()
    print("Authentication successful.", flush=True)

    print("Fetching latest unread email...", flush=True)
    email = gmail_service.get_latest_unread_email()

    if email:
        print("\nSubject:", email.subject, flush=True)
        print("Sender:", email.sender, flush=True)
        print("Received:", email.received_at, flush=True)
        print("Preview:", email.snippet, flush=True)
    else:
        print("\nNo unread emails found in inbox.", flush=True)


if __name__ == "__main__":
    main()
