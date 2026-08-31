"""Notion SDK service integration for creating triage database records."""

import logging
from typing import Optional

from notion_client import Client
from notion_client.errors import APIResponseError

from src.config.settings import Settings, get_settings
from src.models.email_models import EmailMessage, TriageResult

logger = logging.getLogger(__name__)


class NotionService:
    """Service wrapper for interacting with Notion API to create email triage database pages."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initialize Notion service client with configuration.

        Args:
            settings: Global application settings instance.
        """
        self.settings = settings or get_settings()
        self._client: Optional[Client] = None

    def get_client(self) -> Client:
        """Get or initialize authenticated notion_client.Client instance.

        Returns:
            Authenticated notion_client.Client.

        Raises:
            ValueError: If NOTION_API_KEY is not configured.
        """
        if self._client is None:
            if not self.settings.notion_api_key:
                logger.error("NOTION_API_KEY is not configured in Settings.")
                raise ValueError("NOTION_API_KEY is not configured in Settings.")
            self._client = Client(auth=self.settings.notion_api_key)
        return self._client

    def create_email_record(
        self, email: EmailMessage, triage_result: TriageResult
    ) -> str:
        """Create a new page in the Notion database for a triaged email.

        Args:
            email: Original EmailMessage object.
            triage_result: TriageResult containing AI classification and draft info.

        Returns:
            Created Notion page ID string.

        Raises:
            ValueError: If NOTION_API_KEY or NOTION_DATABASE_ID is missing or invalid.
            APIResponseError / Exception: On Notion API execution failure.
        """
        if not self.settings.notion_api_key:
            logger.error("Cannot create Notion record: NOTION_API_KEY is missing.")
            raise ValueError("NOTION_API_KEY is missing.")

        if not self.settings.notion_database_id:
            logger.error("Cannot create Notion record: NOTION_DATABASE_ID is missing.")
            raise ValueError("NOTION_DATABASE_ID is missing.")

        client = self.get_client()
        database_id = self.settings.notion_database_id

        logger.info(
            "Creating Notion database record for email ID %s in database %s",
            email.id,
            database_id,
        )

        reply_needed = triage_result.draft_reply is not None

        properties = {
            "Subject": {"title": [{"text": {"content": email.subject}}]},
            "Sender": {"rich_text": [{"text": {"content": email.sender}}]},
            "Category": {"select": {"name": triage_result.classification.category.value}},
            "Priority": {"select": {"name": triage_result.classification.priority.value}},
            "Spam Score": {"number": float(triage_result.classification.spam_score)},
            "Reply Needed": {"checkbox": reply_needed},
            "Summary": {"rich_text": [{"text": {"content": triage_result.classification.summary}}]},
            "Received At": {"date": {"start": email.received_at.isoformat()}},
        }

        try:
            response = client.pages.create(
                parent={"database_id": database_id},
                properties=properties,
            )
            page_id = response.get("id", "")
            logger.info("Successfully created Notion page record ID: %s", page_id)
            return page_id
        except APIResponseError as err:
            logger.error(
                "Notion API Response Error (Database ID: %s): %s", database_id, err
            )
            raise
        except Exception as err:
            logger.error(
                "Unexpected failure creating Notion page (Database ID: %s): %s",
                database_id,
                err,
            )
            raise

    async def update_dashboard(
        self, email: EmailMessage, triage_result: TriageResult
    ) -> Optional[str]:
        """Async compatibility wrapper to create a record entry in Notion."""
        try:
            return self.create_email_record(email, triage_result)
        except Exception as e:
            logger.error("Async update_dashboard failed: %s", e)
            return None
