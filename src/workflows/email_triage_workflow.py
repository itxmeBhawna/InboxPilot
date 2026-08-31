"""Email triage workflow orchestrator connecting Gmail, Agent, Memory, and Notion services."""

import logging
from typing import List, Optional, Tuple

from src.agent.inbox_agent import InboxAgent
from src.config.settings import Settings, get_settings
from src.gmail.gmail_service import GmailService
from src.memory.memory_service import MemoryService
from src.models.email_models import EmailMessage, TriageResult
from src.notion.notion_service import NotionService

logger = logging.getLogger(__name__)


class EmailTriageWorkflow:
    """Orchestrates end-to-end email triage pipeline across components."""

    def __init__(
        self,
        gmail_service: Optional[GmailService] = None,
        agent: Optional[InboxAgent] = None,
        memory_service: Optional[MemoryService] = None,
        notion_service: Optional[NotionService] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        """Initialize workflow dependencies.

        Args:
            gmail_service: Gmail integration component.
            agent: AI Agent evaluation component.
            memory_service: Memory & personalization orchestrator.
            notion_service: Notion dashboard sync component.
            settings: Global settings instance.
        """
        self.settings = settings or get_settings()
        self.gmail = gmail_service or GmailService(settings=self.settings)
        self.agent = agent or InboxAgent(settings=self.settings)
        self.memory = memory_service or MemoryService(settings=self.settings)
        self.notion = notion_service or NotionService(settings=self.settings)

    def process_latest_unread_email(
        self,
    ) -> Optional[Tuple[EmailMessage, TriageResult]]:
        """Fetch the latest unread email from Gmail and analyze it using InboxAgent.

        Returns:
            Tuple of (EmailMessage, TriageResult) if an unread email was processed, or None.
        """
        logger.info("Fetching latest unread email for triage workflow...")
        email = self.gmail.get_latest_unread_email()
        if not email:
            logger.info("No unread email found to triage.")
            return None

        logger.info("Analyzing email ID %s via InboxAgent...", email.id)
        triage_result = self.agent.analyze_email(email)
        return email, triage_result

    async def triage_single_email(self, email: EmailMessage) -> TriageResult:
        """Process a single email through AI evaluation pipeline.

        Args:
            email: Structured EmailMessage to triage.

        Returns:
            TriageResult containing evaluation results.
        """
        logger.info("Starting workflow for email ID: %s", email.id)
        return self.agent.analyze_email(email)

    async def run_batch_triage(self, batch_size: int = 10) -> List[TriageResult]:
        """Fetch unread emails and process them through the triage pipeline.

        Args:
            batch_size: Number of unread emails to retrieve and process.

        Returns:
            List of TriageResult outcomes.
        """
        logger.info("Executing batch email triage workflow...")
        emails = self.gmail.fetch_unread_emails(max_results=batch_size)
        results = []
        for email in emails:
            try:
                res = self.agent.analyze_email(email)
                results.append(res)
            except Exception as e:
                logger.error("Failed to triage email ID %s: %s", email.id, e)
        return results
