"""FastAPI application entrypoint for InboxPilot service."""

import logging
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config.settings import get_settings
from src.memory.memory_service import MemoryService
from src.workflows.email_triage_workflow import EmailTriageWorkflow

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Autonomous AI agent for email triage, classification, drafting, and Notion synchronization.",
    version="0.1.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
workflow_service = EmailTriageWorkflow(settings=settings)
memory_service = MemoryService(settings=settings)


class FeedbackRequest(BaseModel):
    """Pydantic schema for user feedback submission endpoint."""

    email_id: str = Field(..., description="Target email message ID")
    sender: str = Field(..., description="Sender email address")
    subject: str = Field(default="", description="Email subject line")
    predicted_priority: str = Field(..., description="Agent predicted priority")
    user_priority: str = Field(..., description="User corrected priority")
    predicted_category: str = Field(..., description="Agent predicted category")
    user_category: str = Field(..., description="User corrected category")
    feedback_reason: Optional[str] = Field(
        default=None, description="Optional explanation for correction"
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Service health check endpoint."""
    logger.info("Health check endpoint invoked")
    return {
        "status": "ok",
        "service": settings.app_name,
    }


@app.get("/emails/latest", tags=["Triage"])
@app.get("/api/emails/latest", tags=["Triage"])
async def get_latest_email(response: Response):
    """Fetch and process the latest unread email via EmailTriageWorkflow."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    logger.info("Fetching latest unread email via API endpoint...")
    try:
        res = workflow_service.process_latest_unread_email()
        if not res:
            return {"unread": False, "message": "No new unread emails found", "email": None}

        email, triage_result, page_id = res
        classification = triage_result.classification

        return {
            "unread": True,
            "email_id": email.id,
            "subject": email.subject,
            "sender": email.sender,
            "recipient": email.recipient,
            "received_at": email.received_at.isoformat() if email.received_at else None,
            "category": classification.category.value,
            "priority": classification.priority.value,
            "spam_score": classification.spam_score,
            "summary": classification.summary,
            "reasoning": classification.reasoning,
            "reply_needed": classification.reply_needed,
            "draft_reply": triage_result.draft_reply,
            "synced_to_notion": triage_result.synced_to_notion,
            "notion_page_id": page_id,
            "draft_created": triage_result.draft_created,
            "draft_id": triage_result.draft_id,
            "preference_context_used": triage_result.preference_context_used,
        }
    except Exception as e:
        logger.exception("Error processing latest unread email: %s", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to process latest email: {str(e)}"
        )


@app.post("/feedback", tags=["Feedback"])
@app.post("/api/feedback", tags=["Feedback"])
async def submit_feedback(req: FeedbackRequest):
    """Submit user classification correction feedback."""
    logger.info(
        "Received feedback submission for email %s: Priority (%s -> %s), Category (%s -> %s)",
        req.email_id,
        req.predicted_priority,
        req.user_priority,
        req.predicted_category,
        req.user_category,
    )
    try:
        record = memory_service.record_feedback(
            email_id=req.email_id,
            sender=req.sender,
            subject=req.subject,
            predicted_priority=req.predicted_priority,
            user_priority=req.user_priority,
            predicted_category=req.predicted_category,
            user_category=req.user_category,
            feedback_reason=req.feedback_reason,
        )
        return {
            "status": "success",
            "message": "Feedback saved successfully",
            "record": record,
        }
    except Exception as e:
        logger.exception("Failed to save user feedback: %s", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to record feedback: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=(settings.app_env == "development"),
    )
