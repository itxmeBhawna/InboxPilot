"""Email triage workflow orchestrator connecting Gmail, Agent, Memory, and Notion services."""

import logging
from typing import List, Optional
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

    async def triage_single_email(self, email: EmailMessage) -> TriageResult:
        """Process a single email through classification, memory context lookup, drafting, and sync.

        Args:
            email: Structured EmailMessage to triage.

        Returns:
            TriageResult containing processing metrics and output state.
        """
        logger.info("Starting workflow for email ID: %s", email.id)

        # 1. Fetch personalization context from memory
        context = await self.memory.get_agent_context()

        # 2. Evaluate email with AI agent
        classification = await self.agent.classify_email(email, user_context=context)

        # 3. Draft reply if applicable
        draft = await self.agent.draft_reply(email, classification, user_context=context)
        if draft:
            # TODO: Create draft in Gmail via self.gmail.create_draft()
            pass

        # 4. Construct triage result
        triage_result = TriageResult(
            email_id=email.id,
            classification=classification,
            draft_reply=draft,
            synced_to_notion=False,
        )

        # 5. Sync to Notion dashboard
        # page_id = await self.notion.update_dashboard(email, triage_result)
        # triage_result.synced_to_notion = bool(page_id)

        # 6. Record privacy-compliant audit log entry
        await self.memory.log_audit_event(
            event_type="EMAIL_TRIAGED",
            email_id=email.id,
            metadata={
                "priority": classification.priority,
                "category": classification.category,
                "spam_score": classification.spam_score,
            },
        )

        return triage_result

    async def run_batch_triage(self, batch_size: int = 10) -> List[TriageResult]:
        """Fetch unread emails and process them through the triage pipeline.

        Args:
            batch_size: Number of unread emails to retrieve and process.

        Returns:
            List of TriageResult outcomes.
        """
        logger.info("Executing batch email triage workflow...")
        # TODO: Fetch unread messages via self.gmail.fetch_unread_emails(max_results=batch_size)
        # TODO: Loop over fetched emails and execute triage_single_email()
        return []
