"""Gmail API service integration for authenticating, reading, and drafting emails."""

import base64
import logging
import os
import re
from datetime import datetime, timezone
from email.mime.text import MIMEText
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from src.config.settings import Settings, get_settings
from src.models.email_models import EmailMessage

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailService:
    """Service wrapper for interacting with Gmail API via Google API Client Libraries."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initialize Gmail API service with configuration paths.

        Args:
            settings: Global application settings.
        """
        self.settings = settings or get_settings()
        self._service: Optional[Resource] = None
        self._creds: Optional[Credentials] = None

    def authenticate(self) -> Credentials:
        """Authenticate with Gmail API using OAuth 2.0 credentials and token files.

        Returns:
            Authenticated Credentials object.
        """
        token_path = self.settings.gmail_token_file
        credentials_path = self.settings.gmail_credentials_file

        creds = None
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception as e:
                logger.warning(
                    "Failed to load existing credentials from %s: %s", token_path, e
                )
                creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Refreshing expired Gmail access token...")
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(
                        "Token refresh failed: %s. Initiating re-authentication flow...",
                        e,
                    )
                    creds = None

            if not creds:
                logger.info(
                    "Launching browser authentication flow using credentials file: %s",
                    credentials_path,
                )
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save generated credentials to token file
            with open(token_path, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())
            logger.info("Saved fresh credentials to %s", token_path)

        self._creds = creds
        return creds

    def get_service(self) -> Resource:
        """Returns authenticated Gmail API service instance."""
        if self._service is None:
            creds = self.authenticate()
            self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def get_latest_unread_email(self) -> Optional[EmailMessage]:
        """Fetch the most recent unread email from the inbox.

        Returns:
            EmailMessage instance if an unread email is found, or None if inbox has no unread emails.
        """
        service = self.get_service()
        user_id = self.settings.gmail_user_id

        response = (
            service.users()
            .messages()
            .list(userId=user_id, q="is:unread", maxResults=1)
            .execute()
        )

        messages = response.get("messages", [])
        if not messages:
            logger.info("No unread emails found.")
            return None

        msg_id = messages[0]["id"]
        return self._fetch_email_by_id(msg_id)

    def fetch_unread_emails(self, max_results: int = 10) -> List[EmailMessage]:
        """Fetch up to max_results unread emails from the inbox.

        Args:
            max_results: Maximum number of unread email messages to retrieve.

        Returns:
            List of EmailMessage objects.
        """
        service = self.get_service()
        user_id = self.settings.gmail_user_id

        response = (
            service.users()
            .messages()
            .list(userId=user_id, q="is:unread", maxResults=max_results)
            .execute()
        )

        messages = response.get("messages", [])
        email_messages: List[EmailMessage] = []
        for msg in messages:
            try:
                email_obj = self._fetch_email_by_id(msg["id"])
                email_messages.append(email_obj)
            except Exception as e:
                logger.error("Failed to fetch message ID %s: %s", msg["id"], e)

        return email_messages

    def create_draft_reply(
        self, original_email: EmailMessage, draft_body: str
    ) -> Optional[str]:
        """Create a reply draft in Gmail for an email message.

        Args:
            original_email: Original EmailMessage being responded to.
            draft_body: Body text for the reply draft.

        Returns:
            Gmail Draft ID string if created successfully.

        Raises:
            Exception: If Gmail API draft creation fails.
        """
        logger.info("Creating Gmail draft reply for email ID %s", original_email.id)
        if not draft_body or not draft_body.strip():
            logger.warning(
                "Draft body is empty for email ID %s. Skipping draft creation.",
                original_email.id,
            )
            return None

        service = self.get_service()
        user_id = self.settings.gmail_user_id

        # Prepare MIME message
        mime_msg = MIMEText(draft_body, "plain", "utf-8")
        mime_msg["To"] = original_email.sender

        subject = original_email.subject or ""
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"
        mime_msg["Subject"] = subject

        mime_msg["In-Reply-To"] = original_email.id
        mime_msg["References"] = original_email.id

        raw_bytes = mime_msg.as_bytes()
        raw_encoded = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")

        body = {
            "message": {
                "raw": raw_encoded,
                "threadId": original_email.thread_id,
            }
        }

        try:
            draft = service.users().drafts().create(userId=user_id, body=body).execute()
            draft_id = draft.get("id")
            logger.info(
                "Successfully created Gmail draft ID %s for email ID %s",
                draft_id,
                original_email.id,
            )
            return draft_id
        except Exception as err:
            logger.error(
                "Failed to create Gmail draft for email ID %s: %s",
                original_email.id,
                err,
            )
            raise

    def create_draft(self, email_id: str, reply_body: str) -> Optional[str]:
        """Backward compatible helper to create a reply draft by email ID."""
        logger.info("Creating Gmail draft reply for email ID %s", email_id)
        email = self._fetch_email_by_id(email_id)
        return self.create_draft_reply(email, reply_body)

    def _fetch_email_by_id(self, msg_id: str) -> EmailMessage:
        """Helper to fetch and parse full message content by ID."""
        service = self.get_service()
        user_id = self.settings.gmail_user_id

        msg_detail = (
            service.users()
            .messages()
            .get(userId=user_id, id=msg_id, format="full")
            .execute()
        )

        payload = msg_detail.get("payload", {})
        headers = payload.get("headers", [])

        # Extract headers case-insensitively
        header_dict = {
            h["name"].lower(): h["value"]
            for h in headers
            if "name" in h and "value" in h
        }
        subject = header_dict.get("subject", "(No Subject)")
        sender = header_dict.get("from", "Unknown Sender")
        recipient = header_dict.get("to", "Unknown Recipient")

        # Received timestamp: internalDate is Unix timestamp in milliseconds
        internal_date = msg_detail.get("internalDate")
        if internal_date:
            received_at = datetime.fromtimestamp(
                int(internal_date) / 1000.0, tz=timezone.utc
            )
        else:
            received_at = datetime.now(timezone.utc)

        # Extract body (plain text preferred)
        body = self._extract_body(payload)
        snippet = msg_detail.get("snippet", body[:200] if body else "")

        return EmailMessage(
            id=msg_detail["id"],
            thread_id=msg_detail.get("threadId", msg_detail["id"]),
            sender=sender,
            recipient=recipient,
            subject=subject,
            snippet=snippet,
            body=body,
            received_at=received_at,
            labels=msg_detail.get("labelIds", []),
        )

    def _extract_body(self, payload: dict) -> str:
        """Extract plain text body from message payload, falling back to HTML if plain text unavailable."""
        if not payload:
            return ""

        mime_type = payload.get("mimeType", "")
        body_data = payload.get("body", {}).get("data")

        if mime_type == "text/plain" and body_data:
            return self._decode_base64url(body_data)

        parts = payload.get("parts", [])
        plain_text_body = ""
        html_body = ""

        def parse_parts(part_list: list) -> None:
            nonlocal plain_text_body, html_body
            for part in part_list:
                part_mime = part.get("mimeType", "")
                part_data = part.get("body", {}).get("data")

                if part_mime == "text/plain" and part_data and not plain_text_body:
                    plain_text_body = self._decode_base64url(part_data)
                elif part_mime == "text/html" and part_data and not html_body:
                    html_body = self._decode_base64url(part_data)

                if "parts" in part:
                    parse_parts(part["parts"])

        parse_parts(parts)

        if plain_text_body:
            return plain_text_body
        if html_body:
            clean_text = re.sub(r"<[^>]+>", " ", html_body)
            return " ".join(clean_text.split())

        if body_data:
            return self._decode_base64url(body_data)

        return ""

    @staticmethod
    def _decode_base64url(data: str) -> str:
        """Decode base64url encoded string from Gmail API payload."""
        try:
            decoded_bytes = base64.urlsafe_b64decode(data.encode("UTF-8"))
            return decoded_bytes.decode("UTF-8", errors="replace")
        except Exception as e:
            logger.warning("Failed to decode message body: %s", e)
            return ""
