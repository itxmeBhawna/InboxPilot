# InboxPilot ✈️📧

An autonomous, production-ready AI email triage agent that monitors incoming emails, classifies priority and categories, detects spam and scam attempts, generates reply drafts, and synchronizes actionable inbox intelligence to a Notion dashboard.

---

## 🎯 Project Purpose

InboxPilot is designed to reduce inbox fatigue and automate personal or team email workflows. Powered by **Google ADK** and **Google Gemini**, InboxPilot acts as an intelligent executive assistant for your inbox by:

- **Classifying Emails**: Dynamically sorting messages across expanded categories (`ACTION_REQUIRED`, `MEETING`, `APPLICATION`, `FINANCE`, `NEWSLETTER`, `PROMOTION`, `SPAM_SCAM`, `PERSONAL`, `OTHER`).
- **Evaluating Urgency**: Assigning priority levels (`HIGH`, `MEDIUM`, `LOW`) based on context and urgency.
- **Drafting Intelligent Replies**: Generating contextually aware draft responses for action-item emails.
- **Notion Dashboard Syncing**: Logging triage decisions, metadata, and draft status directly to a Notion database.
- **Human-in-the-Loop Feedback**: Learning from user classification corrections (`UserFeedback`) to continuously personalize triage rules.

---

## 🔒 Privacy-First Memory Design

> **Core Principle**: InboxPilot intentionally avoids retaining full inbox contents or raw email bodies long-term.

To uphold privacy and data security:
- **No Indefinite Content Storage**: Raw email message bodies are processed ephemerally during triage and are discarded immediately after workflow execution.
- **Minimal Metadata Footprint**: The memory system only stores:
  1. **User Preferences**: Learned rules (e.g., sender whitelist/blacklist rules, category preferences).
  2. **User Feedback Corrections**: Misclassification corrections (`predicted_priority` vs `user_priority`, `predicted_category` vs `user_category`, and optional feedback reason) to personalize future AI predictions.
  3. **Lightweight Audit Logs**: Minimal operational metrics (event type, email ID, timestamp, priority score) without storing email body text.

---

## 📁 Folder Structure

```
InboxPilot/
│
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   └── inbox_agent.py          # Google ADK & Gemini agent interface
│   │
│   ├── gmail/
│   │   ├── __init__.py
│   │   └── gmail_service.py        # Gmail API authentication and message fetching
│   │
│   ├── notion/
│   │   ├── __init__.py
│   │   └── notion_service.py       # Notion SDK integration for database updates
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── memory_service.py       # Memory orchestrator (privacy-first)
│   │   ├── user_preferences.py     # Learned user preferences and rules storage
│   │   └── feedback_memory.py      # User feedback and correction memory storage
│   │
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── email_triage_workflow.py # End-to-end triage pipeline orchestrator
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── email_models.py         # Pydantic schemas (Priority, Category, Feedback, etc.)
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py             # Pydantic Settings configuration loader
│   │
│   └── main.py                     # FastAPI application entrypoint with GET /health
│
├── tests/
│   ├── __init__.py
│   └── test_main.py                # Pytest test suite
│
├── .env.example                    # Environment variable template
├── requirements.txt                # Python project dependencies
├── README.md                       # Project documentation
└── .gitignore                      # Git exclusion rules
```

---

## 🚀 Setup Instructions

### Prerequisites
- **Python 3.11+** installed.
- Access to a Google Cloud Project (for Gemini API & Gmail OAuth credentials).
- A Notion Integration Token & Database ID (for Notion sync).

### 1. Environment Setup

Clone or enter the project directory and create a Python virtual environment:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example configuration file and fill in your credential values:

```bash
cp .env.example .env
```

Edit `.env` to include your configuration:
- `GEMINI_API_KEY`: Google Gemini API key.
- `NOTION_API_KEY`: Notion Integration token.
- `NOTION_DATABASE_ID`: Target Notion database ID.

### 4. Run the FastAPI Server

Launch the development server with Uvicorn:

```bash
python -m src.main
# or
uvicorn src.main:app --reload
```

The service will start at `http://127.0.0.1:8000`.

### 5. Verify API Health

Verify the server is running by sending a request to the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "InboxPilot"
}
```

### 6. Run Unit Tests

Execute the test suite using `pytest`:

```bash
pytest
```

---

## 🗺️ Future Roadmap

- [ ] **Phase 1: Gmail OAuth & Webhook Integration**: Implement full OAuth 2.0 flow, token refresh, and real-time Gmail Push Notifications (Pub/Sub).
- [ ] **Phase 2: Google ADK & Gemini Prompting**: Integrate Google ADK structured agents with function calling and zero-shot/few-shot classification prompts.
- [ ] **Phase 3: Notion Database Synchronization**: Implement complete Notion SDK schema mapping to update status, properties, and draft previews.
- [ ] **Phase 4: Firestore Memory & Feedback Learning Loop**: Store user feedback and preferences in GCP Firestore, dynamically augmenting agent prompts with user corrections.
- [ ] **Phase 5: Automated Reply Approval UI**: Create a web/dashboard interface to review, approve, or refine AI-generated draft replies before sending.
