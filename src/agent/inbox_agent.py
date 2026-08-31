"""Google Gemini-powered AI reasoning engine for autonomous email triage, classification, and reply drafting."""

import json
import logging
import re
import time
from typing import Any, Dict, Optional

from google import genai
from google.genai import types
from pydantic import ValidationError

from src.agent.exceptions import InvalidAgentOutputError
from src.agent.prompts import (
    EMAIL_ANALYSIS_SYSTEM_PROMPT,
    EMAIL_ANALYSIS_USER_PROMPT,
    USER_PREFERENCE_CONTEXT,
)
from src.config.settings import Settings, get_settings
from src.memory.memory_service import MemoryService
from src.models.email_models import (
    CategoryEnum,
    EmailClassification,
    EmailMessage,
    PriorityEnum,
    TriageResult,
)

logger = logging.getLogger(__name__)


class InboxAgent:
    """AI Agent responsible for evaluating incoming emails using Google Gemini.

    Analyzes email text to classify emails into categories, assess urgency/priority,
    score spam likelihood, generate concise summaries and reasoning, and draft appropriate responses.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        memory_service: Optional[MemoryService] = None,
        client: Optional[Any] = None,
    ) -> None:
        """Initialize the InboxAgent with model configuration, memory service, and Gemini client.

        Args:
            settings: Global application settings instance.
            memory_service: Optional MemoryService component for sender preference queries.
            client: Optional injected Gemini client (useful for unit testing/mocking).
        """
        self.settings = settings or get_settings()
        self.memory_service = memory_service or MemoryService(settings=self.settings)
        self.client = client

        if self.client is None and self.settings.gemini_api_key:
            try:
                self.client = genai.Client(api_key=self.settings.gemini_api_key)
            except Exception as err:
                logger.warning("Failed to initialize Google GenAI client: %s", err)

    def analyze_email(self, email: EmailMessage) -> TriageResult:
        """Analyze an incoming email message using Gemini to produce structured triage results.

        Args:
            email: Structured EmailMessage object containing email metadata and body.

        Returns:
            TriageResult containing EmailClassification and optional draft reply.

        Raises:
            InvalidAgentOutputError: If Gemini returns malformed, missing, or schema-invalid output.
        """
        logger.info("Analyzing email ID: %s | Subject: '%s'", email.id, email.subject)

        if self.client is None:
            raise InvalidAgentOutputError(
                "Gemini API client is not initialized. Please configure GEMINI_API_KEY."
            )

        pref_context_str = ""
        preference_context_used = False

        if self.memory_service:
            try:
                stats = self.memory_service.get_sender_preferences(email.sender)
                if stats and stats.get("feedback_count", 0) > 0:
                    pref_context_str = "\n" + USER_PREFERENCE_CONTEXT.format(
                        preferred_priority=stats.get("preferred_priority", "N/A"),
                        confidence=stats.get("confidence", 0.0),
                        feedback_count=stats.get("feedback_count", 0),
                    )
                    preference_context_used = True
                    logger.info(
                        "Injecting preference context for sender '%s' (feedback_count: %d, preferred: %s)",
                        email.sender,
                        stats.get("feedback_count"),
                        stats.get("preferred_priority"),
                    )
            except Exception as err:
                logger.warning(
                    "Failed to query sender preferences for email ID %s: %s", email.id, err
                )

        prompt = EMAIL_ANALYSIS_USER_PROMPT.format(
            email_id=email.id,
            sender=email.sender,
            recipient=email.recipient,
            subject=email.subject,
            received_at=email.received_at.isoformat() if email.received_at else "",
            labels=", ".join(email.labels) if email.labels else "None",
            preference_context=pref_context_str,
            body=email.body,
        )

        config = types.GenerateContentConfig(
            system_instruction=EMAIL_ANALYSIS_SYSTEM_PROMPT,
            temperature=0.2,
            response_mime_type="application/json",
        )

        raw_text = ""
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.settings.gemini_model,
                    contents=prompt,
                    config=config,
                )
                raw_text = response.text if hasattr(response, "text") and response.text else ""
                break
            except Exception as err:
                err_str = str(err)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "Quota exceeded" in err_str:
                    logger.warning(
                        "Gemini API rate limit reached for email ID %s: %s. Using fallback classification.",
                        email.id,
                        err,
                    )
                    raw_text = json.dumps({
                        "category": "OTHER",
                        "priority": "MEDIUM",
                        "spam_score": 0.0,
                        "summary": email.snippet or email.subject,
                        "reasoning": "Fallback classification generated due to transient Gemini API rate limit.",
                        "reply_needed": False,
                        "draft_reply": None,
                    })
                    break

                if attempt == 2:
                    logger.error("Gemini API call failed for email ID %s: %s", email.id, err)
                    raise InvalidAgentOutputError(
                        f"Gemini API request execution failed: {err}"
                    ) from err
                logger.warning(
                    "Gemini API attempt %d failed for email ID %s: %s. Retrying in 2s...",
                    attempt + 1,
                    email.id,
                    err,
                )
                time.sleep(2.0)

        return self._parse_and_validate_response(
            email, raw_text, preference_context_used=preference_context_used
        )

    def _parse_and_validate_response(
        self, email: EmailMessage, raw_text: str, preference_context_used: bool = False
    ) -> TriageResult:
        """Parse raw text response from Gemini and validate against structured schema.

        Args:
            email: Original EmailMessage being processed.
            raw_text: Raw string output returned by Gemini.

        Returns:
            Validated TriageResult instance.

        Raises:
            InvalidAgentOutputError: On JSON parsing error or field schema validation failure.
        """
        if not raw_text or not raw_text.strip():
            logger.error("Received empty response from Gemini for email ID: %s", email.id)
            raise InvalidAgentOutputError(
                "Gemini returned empty or blank response", raw_output=raw_text
            )

        # Clean code fence markdown wrappers if present
        cleaned_text = raw_text.strip()
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text, flags=re.IGNORECASE)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)

        try:
            data = json.loads(cleaned_text)
        except json.JSONDecodeError as err:
            logger.error(
                "Failed to parse JSON output from Gemini for email ID %s: %s", email.id, err
            )
            raise InvalidAgentOutputError(
                f"Gemini output is not valid JSON: {err}", raw_output=raw_text
            ) from err

        if not isinstance(data, dict):
            logger.error("Gemini output is not a JSON object (dict) for email ID %s", email.id)
            raise InvalidAgentOutputError(
                "Gemini output must be a JSON object", raw_output=raw_text
            )

        # Verify required schema fields
        required_fields = [
            "category",
            "priority",
            "spam_score",
            "summary",
            "reasoning",
            "reply_needed",
            "draft_reply",
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.error(
                "Gemini output missing required schema fields %s for email ID %s",
                missing_fields,
                email.id,
            )
            raise InvalidAgentOutputError(
                f"Gemini JSON response missing required fields: {missing_fields}",
                raw_output=raw_text,
            )

        try:
            category = CategoryEnum(str(data["category"]).upper())
        except ValueError as err:
            logger.error(
                "Invalid category value '%s' in Gemini response for email ID %s",
                data.get("category"),
                email.id,
            )
            raise InvalidAgentOutputError(
                f"Invalid category value '{data.get('category')}': {err}",
                raw_output=raw_text,
            ) from err

        try:
            priority = PriorityEnum(str(data["priority"]).upper())
        except ValueError as err:
            logger.error(
                "Invalid priority value '%s' in Gemini response for email ID %s",
                data.get("priority"),
                email.id,
            )
            raise InvalidAgentOutputError(
                f"Invalid priority value '{data.get('priority')}': {err}",
                raw_output=raw_text,
            ) from err

        try:
            spam_score = float(data["spam_score"])
        except (ValueError, TypeError) as err:
            logger.error(
                "Invalid spam_score value '%s' in Gemini response for email ID %s",
                data.get("spam_score"),
                email.id,
            )
            raise InvalidAgentOutputError(
                f"Invalid spam_score value '{data.get('spam_score')}': {err}",
                raw_output=raw_text,
            ) from err

        summary = str(data["summary"]).strip()
        reasoning = str(data["reasoning"]).strip()
        reply_needed = bool(data["reply_needed"])
        raw_draft = data.get("draft_reply")
        draft_reply = (
            str(raw_draft).strip()
            if raw_draft and str(raw_draft).strip() and str(raw_draft).strip().lower() != "none"
            else None
        )

        try:
            classification = EmailClassification(
                priority=priority,
                category=category,
                summary=summary,
                spam_score=spam_score,
                reasoning=reasoning,
                reply_needed=reply_needed,
            )
        except ValidationError as err:
            logger.error(
                "EmailClassification validation failed for email ID %s: %s", email.id, err
            )
            raise InvalidAgentOutputError(
                f"EmailClassification schema validation failed: {err}",
                raw_output=raw_text,
            ) from err

        return TriageResult(
            email_id=email.id,
            classification=classification,
            draft_reply=draft_reply,
            synced_to_notion=False,
            preference_context_used=preference_context_used,
        )

    async def classify_email(
        self, email: EmailMessage, user_context: Optional[Dict[str, Any]] = None
    ) -> EmailClassification:
        """Asynchronous wrapper to analyze and return EmailClassification."""
        result = self.analyze_email(email)
        return result.classification

    async def draft_reply(
        self,
        email: EmailMessage,
        classification: EmailClassification,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Asynchronous wrapper to retrieve reply draft from triage result."""
        result = self.analyze_email(email)
        return result.draft_reply
