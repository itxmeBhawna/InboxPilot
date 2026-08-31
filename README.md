# InboxPilot — Autonomous AI Email Triage Assistant ✈️📧

> **An autonomous, production-ready AI email triage assistant powered by Google Gemini 3.6 Flash, Gmail API, and Notion. InboxPilot continuously monitors incoming emails, evaluates urgency, generates reply drafts, synchronizes actionable workspace intelligence to Notion, and learns user preferences from feedback.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-3.6_Flash-8E75B2?style=for-the-badge&logo=googlecloud&logoColor=white)](https://ai.google.dev)
[![Gmail API](https://img.shields.io/badge/Gmail_API-OAuth_2.0-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](https://developers.google.com/gmail/api)
[![Notion API](https://img.shields.io/badge/Notion_API-Workspace_Sync-000000?style=for-the-badge&logo=notion&logoColor=white)](https://developers.notion.com)

---

## 📖 Overview

**InboxPilot** transforms email overload into an autonomous, self-improving workflow. Operating as a continuous background agent, InboxPilot:
- 📩 **Monitors unread emails** via official Gmail OAuth 2.0 integration.
- 🧠 **Classifies and prioritizes messages** across 9 categories and 3 priority levels using Google Gemini 3.6 Flash.
- ✍️ **Generates professional reply drafts** saved directly into Gmail Drafts for human review before sending.
- 📊 **Synchronizes structured email records** into a live Notion workspace dashboard.
- 🎓 **Learns user preferences** over time from manual feedback corrections without retraining models.
- 🛑 **Prevents duplicate processing** by automatically marking processed messages as read (`removeLabelIds: ["UNREAD"]`) upon workflow completion.
- 🎨 **Provides a modern React dashboard** with real-time autonomous monitoring indicators and a 15-second auto-poll toggle.

---

## 🚨 Problem Statement

Modern professionals suffer from severe **inbox fatigue**:
- 📥 **Email Deluge**: Hundreds of emails flood inboxes daily, mixing urgent requests with newsletters, promotions, and spam.
- 🔍 **Buried Priority**: Critical time-sensitive inquiries (e.g., job interview invitations, client requests, bank alerts) get lost in low-priority noise.
- ⏳ **Time Sink**: Manual email triage and repetitive draft composition consume hours of productive work every day.
- 🔄 **Fragmented Context**: Switching between email clients, task managers, and response drafts fragments focus and workflow continuity.

---

## 💡 The Solution

InboxPilot provides a **fully integrated, preference-aware autonomous agent**:

1. **AI-Powered Triage**: Evaluates each unread message using Google Gemini 3.6 Flash to compute urgency scores, primary category, spam risk, summary, and classification reasoning.
2. **Preference-Aware Context**: Injects historical user feedback statistics into Gemini reasoning prompts so the AI adapts to individual user preferences while keeping current content as primary truth.
3. **Safe Human-In-The-Loop Drafting**: Generates contextually relevant response drafts saved strictly to Gmail Drafts — emails are **never** automatically sent without human authorization.
4. **Unified Notion Workspace**: Automatically logs triaged emails, status badges, summaries, and draft indicators into a centralized Notion database.
5. **Real-time Glassmorphism Dashboard**: A dark-mode React web dashboard for reviewing analyzed messages, viewing integration status, and submitting feedback corrections with instant memory persistence.

---

## 🌐 Google Technologies Used

InboxPilot leverages Google's AI and Developer Ecosystem:

- 🧠 **Google Gemini 3.6 Flash**: The core AI reasoning engine powering multi-dimensional email classification, urgency scoring, spam detection, and reply draft composition using the latest `google-genai` Python SDK.
- 📧 **Gmail API**: Handles secure email retrieval (`is:unread`), read marking (`removeLabelIds: ["UNREAD"]`), and automated reply draft creation inside the user's Gmail account.
- 🔐 **Google Cloud OAuth 2.0**: Provides secure user authentication, token persistence (`token.json`), and automatic token refresh flows for production security.

---

## ✨ Features

- 🔐 **Real Gmail OAuth 2.0 Integration**: Token persistence, automatic refresh, and message metadata parsing.
- ⚡ **Gemini 3.6 Flash Reasoning Engine**: High-speed, structured JSON email classification and contextual reasoning output.
- 🏷️ **9-Category Classification**: `ACTION_REQUIRED`, `MEETING`, `APPLICATION`, `FINANCE`, `NEWSLETTER`, `PROMOTION`, `SPAM_SCAM`, `PERSONAL`, and `OTHER`.
- 🚥 **3-Tier Urgency Scoring**: `HIGH`, `MEDIUM`, and `LOW` priority tags.
- 🛡️ **Spam & Scam Risk Gauge**: 0%–100% risk scoring to isolate phishing attempts and fraudulent offers.
- 📝 **Automated Reply Drafting**: Generates professional draft responses saved directly into Gmail Drafts.
- 📓 **Notion Workspace Syncing**: Real-time property mapping to Notion database pages.
- 🧠 **User Feedback Memory**: Persistent JSON storage (`data/feedback_memory.json`) capturing priority/category corrections.
- 📊 **Preference-Aware Reasoner**: Injects sender preference statistics (`Preferred Priority`, `Confidence`, `Feedback Count`) as advisory context into Gemini prompts.
- 🔁 **Duplicate Processing Prevention**: Automatically marks processed Gmail messages as read to ensure idempotent execution.
- 📡 **Autonomous Live Monitoring**: Real-time waiting card with interactive 15-second auto-polling toggle for live hackathon demos.
- 🎨 **Glassmorphism React Dashboard**: Built with React 18, TypeScript, Vite, Tailwind CSS, and Lucide icons.

---

## 🏗️ Architecture

```mermaid
graph TD
    User([👤 User / Judge]) -->|Views Triage & Submits Feedback| ReactApp["🎨 React Frontend (Vite + TS + Tailwind)"]
    ReactApp -->|HTTP REST API (Port 5173 -> 8000)| FastAPI["⚡ FastAPI Backend (src/main.py)"]
    
    subgraph "Core Workflow Orchestrator"
        FastAPI -->|Invokes| Workflow["🔄 EmailTriageWorkflow"]
    end
    
    subgraph "Integrations & Reasoning Layer"
        Workflow -->|1. Fetch Unread Email| GmailAPI["📧 Gmail API (OAuth 2.0)"]
        Workflow -->|2. Query Preference Stats| MemoryStore["🧠 Feedback Memory (data/feedback_memory.json)"]
        Workflow -->|3. Analyze & Classify| Gemini["🧠 Google Gemini 3.6 Flash"]
        Workflow -->|4. Create Database Record| NotionAPI["📓 Notion API"]
        Workflow -->|5. Save Reply Draft| GmailAPI
        Workflow -->|6. Mark Message Read| GmailAPI
    end

    MemoryStore -->|Advisory History Context| Gemini
    ReactApp -->|POST /feedback| FastAPI
    FastAPI -->|Record User Correction| MemoryStore
```

---

## 🔄 Autonomous Agent Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 User
    participant App as 🎨 React Dashboard
    participant API as ⚡ FastAPI Backend
    participant WF as 🔄 EmailTriageWorkflow
    participant Gmail as 📧 Gmail API
    participant Mem as 🧠 Memory Service
    participant Gemini as 🤖 Gemini 3.6 Flash
    participant Notion as 📓 Notion API

    App->>API: GET /emails/latest
    API->>WF: process_latest_unread_email()
    WF->>Gmail: get_latest_unread_email(q="is:unread")
    
    alt Unread Email Found
        Gmail-->>WF: Return EmailMessage
        WF->>Mem: get_sender_preferences(sender)
        Mem-->>WF: Return Preference Stats
        WF->>Gemini: analyze_email(email + advisory_context)
        Gemini-->>WF: Return TriageResult JSON
        
        WF->>Notion: create_email_record(triage_result)
        Notion-->>WF: Return Page ID
        
        opt reply_needed == True AND draft_reply present
            WF->>Gmail: create_draft_reply(original_email, draft_text)
            Gmail-->>WF: Return Draft ID
        end
        
        WF->>Gmail: mark_as_read(email_id)
        Gmail-->>WF: Confirm Label Modified (UNREAD removed)
        WF-->>API: Return (EmailMessage, TriageResult, page_id)
        API-->>App: JSON Response (unread=True, triage payload)
    else No Unread Email
        Gmail-->>WF: Return None
        WF-->>API: Return None
        API-->>App: JSON Response (unread=False, message="No new unread emails found")
        App->>User: Render Autonomous Monitoring Active Card
    end

    opt User Submits Feedback Correction
        User->>App: Select priority/category & submit
        App->>API: POST /feedback (user_priority, user_category, rationale)
        API->>Mem: record_feedback(...)
        Mem-->>API: Saved to data/feedback_memory.json
        API-->>App: 200 OK (✓ Feedback saved toast)
    end
```

### Why InboxPilot Qualifies as an Autonomous Agent

- 👁️ **Perceives Environment**: Continuously polls and inspects inbox state via Gmail API.
- 🧠 **Reasons Contextually**: Synthesizes email text alongside historical sender preferences using Gemini 3.6 Flash.
- 🎯 **Determines Goals**: Autonomously decides whether an email requires urgent attention, a reply draft, or silent filing.
- ⚡ **Executes Multi-Step Actions**: Writes triaged records to Notion, creates Gmail drafts, and marks processed emails as read.
- 🎓 **Adapts & Learns**: Remembers human corrections to personalize future predictions per sender.
- 🛡️ **Operates Safely**: Never sends emails automatically — human review remains mandatory before dispatch.

---

## 🎨 Frontend Web Dashboard

The frontend application (`frontend/`) is a single-page dashboard built with **React 18**, **TypeScript**, **Vite**, and **Tailwind CSS**.

### Key UI Components
- **Glassmorphic Navigation Bar**: Brand identity, active AI status pill, and manual refresh trigger.
- **Email Details Card**: Subject line, sender/recipient badges, and received date timestamp.
- **Triage Badges**: Color-coded category badge, 3-tier priority badge, and spam risk percentage meter.
- **Integration Status Cards**: Live indicators for Notion Sync (`Synced`), Gmail Draft (`Draft Saved`), and Memory Preference (`Memory Context Used` vs `No Preference History`).
- **AI Summary & Reasoning Accordion**: Concise summary block and expandable Gemini classification reasoning block.
- **Draft Reply Box**: Interactive reply draft preview with a 1-click clipboard copy button.
- **Feedback Correction Panel**: Priority & category dropdowns, rationale text area, and submit button displaying an instant `✓ Feedback saved to memory repository!` notification.
- **Autonomous Monitoring Active Card**: Rendered when all unread emails have been processed, featuring a glowing pulse animation, last checked timestamp, and an interactive **Auto-Poll (15s): ON/OFF** toggle.

---

## 💻 Tech Stack

- **Backend Framework**: [Python 3.11+](https://python.org) | [FastAPI](https://fastapi.tiangolo.com) | [Pydantic v2](https://docs.pydantic.dev)
- **Frontend Framework**: [React 18](https://react.dev) | [TypeScript](https://www.typescriptlang.org) | [Vite](https://vitejs.dev) | [Tailwind CSS](https://tailwindcss.com)
- **AI Engine**: [Google Gemini 3.6 Flash](https://ai.google.dev) (`google-genai` SDK)
- **Integrations**: [Google Gmail API](https://developers.google.com/gmail/api) | [Notion API](https://developers.notion.com) (`notion-client`)
- **Memory & Storage**: Persistent local JSON (`data/feedback_memory.json`)
- **Testing**: [Pytest](https://docs.pytest.org)

---

## 📂 Project Structure

```text
InboxPilot/
├── src/
│   ├── agent/
│   │   ├── exceptions.py             # Custom agent exception classes
│   │   ├── inbox_agent.py            # Gemini 3.6 Flash agent with retry & fallback
│   │   └── prompts.py                # Structured system, user & preference prompts
│   ├── config/
│   │   └── settings.py               # Pydantic Settings configuration loader
│   ├── gmail/
│   │   └── gmail_service.py          # Gmail OAuth 2.0 auth, read-marking & draft creation
│   ├── memory/
│   │   ├── feedback_memory.py        # Local JSON feedback storage
│   │   ├── memory_service.py         # Memory orchestrator module
│   │   └── user_preferences.py       # Sender preference statistics compiler
│   ├── models/
│   │   └── email_models.py           # Pydantic data schemas (Email, TriageResult, Feedback)
│   ├── notion/
│   │   └── notion_service.py         # Notion database SDK integration
│   ├── workflows/
│   │   └── email_triage_workflow.py  # End-to-end triage workflow orchestrator
│   └── main.py                       # FastAPI application entrypoint
│
├── frontend/                         # React + Vite + TypeScript web dashboard
│   ├── src/
│   │   ├── App.tsx                   # Main glassmorphism UI component
│   │   ├── index.css                 # Tailwind imports & glow animations
│   │   ├── types.ts                  # TypeScript interface definitions
│   │   └── main.tsx                  # React entrypoint
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts                # Vite config with backend proxy (/api)
│
├── scripts/                          # Standalone verification & test scripts
│   ├── test_gmail_connection.py      # Gmail OAuth connection test
│   ├── test_email_triage.py          # Gemini email triage test
│   ├── test_notion_integration.py    # Notion page creation test
│   ├── test_gmail_draft_creation.py  # Gmail draft reply creation test
│   ├── test_feedback_memory.py       # Memory storage test
│   ├── test_preference_aware_analysis.py # Preference-aware classification test
│   └── test_bugfix_validation.py     # Duplicate prevention & read-marking test
│
├── tests/                            # Pytest test suite
│   ├── test_inbox_agent.py
│   └── test_main.py
│
├── data/                             # Persistent memory store
│   └── feedback_memory.json
│
├── .env.example                      # Configuration template
├── credentials.json                  # Google OAuth credentials (User configured)
├── token.json                        # Gmail OAuth token cache (Generated)
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**
- Google Cloud Project with Gmail API enabled
- Notion Integration Secret & Database ID

---

### 2. Clone & Virtual Environment Setup

```powershell
# Clone repository
git clone https://github.com/itxmeBhawna/InboxPilot.git
cd InboxPilot

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate
```

---

### 3. Install Dependencies

#### Backend Dependencies
```powershell
pip install -r requirements.txt
```

#### Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

---

### 4. Environment Variables Configuration

Copy `.env.example` to `.env`:

```powershell
cp .env.example .env
```

Configure your `.env` variables:

```env
APP_NAME=InboxPilot
ENVIRONMENT=development
LOG_LEVEL=INFO

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash

# Gmail OAuth Settings
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_USER_ID=me

# Notion Integration Settings
NOTION_API_KEY=your_notion_integration_secret_here
NOTION_DATABASE_ID=your_notion_database_id_here
```

---

### 5. Gmail OAuth 2.0 Credentials Setup

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable the **Gmail API**.
3. Configure the **OAuth Consent Screen** (Desktop App).
4. Create **OAuth 2.0 Client IDs** credentials.
5. Download the credentials JSON file and save it as `credentials.json` in the project root directory.
6. Upon initial run, a browser authentication window will launch. Authorize access, and `token.json` will be saved for automatic token re-use.

---

### 6. Notion Database Integration Setup

1. Visit [Notion Integrations](https://www.notion.so/my-integrations) and create a new integration. Copy the key to `NOTION_API_KEY`.
2. Create a database in Notion with the following schema:
   - **Subject** (Title)
   - **Sender** (Rich Text)
   - **Category** (Select)
   - **Priority** (Select)
   - **Spam Score** (Number)
   - **Reply Needed** (Checkbox)
   - **Summary** (Rich Text)
   - **Received At** (Date)
3. Share the Notion database page with your integration.
4. Copy the 32-character database ID into `NOTION_DATABASE_ID`.

---

## 🚀 Running the Application

### Start FastAPI Backend Server

```powershell
# From project root directory
.venv\Scripts\python.exe -m uvicorn src.main:app --port 8000 --reload
```
- **Backend API Server**: `http://localhost:8000`
- **Interactive Swagger Docs**: [`http://localhost:8000/docs`](http://localhost:8000/docs)

---

### Start React Frontend Development Server

```powershell
# Open a second terminal window
cd frontend
npm run dev
```
- **React Web Dashboard**: [`http://localhost:5173`](http://localhost:5173)

---

## 🚢 Deployment

### Backend Deployment (Docker / Cloud Run / Railway)

1. Build the production Docker image using the included Python 3.11 slim base:
   ```bash
   docker build -t inboxpilot-backend .
   ```
2. Run container exposing port 8000:
   ```bash
   docker run -p 8000:8000 --env-file .env inboxpilot-backend
   ```
3. Deploy to **GCP Cloud Run**, **Render**, or **Railway** by setting environment variables (`GEMINI_API_KEY`, `NOTION_API_KEY`, `NOTION_DATABASE_ID`, `GMAIL_CREDENTIALS_FILE`).

---

### Frontend Deployment (Vercel / Netlify)

1. Build the optimized production static bundle:
   ```bash
   cd frontend
   npm run build
   ```
2. Deploy the generated `frontend/dist` directory to **Vercel**, **Netlify**, or **Cloudflare Pages**.
3. Configure environment proxy / API route pointing `/emails` and `/feedback` requests to your deployed backend URL.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
