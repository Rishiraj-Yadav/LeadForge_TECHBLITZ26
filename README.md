# LeadForge - Intelligent Sales Agent System

An AI-powered multi-agent system that captures leads from multiple sources, automatically researches and scores them, notifies sales reps via WhatsApp/Telegram for approval, and handles complete outreach and follow-up autonomously.

## Features

- **Multi-Source Lead Capture**: Website forms, Instagram DMs, WhatsApp, Email, Voice calls
- **AI Lead Research & Scoring**: Automated web research with 0-10 scoring
- **Rep Notifications**: WhatsApp/Telegram alerts with approve/reject buttons
- **Smart Outreach**: Personalized multi-channel first contact within 60 seconds
- **Intelligent Follow-Up**: Auto follow-ups with timing optimization
- **Voice Calls**: AI-powered inbound/outbound calls via Twilio
- **Pipeline Management**: Full CRM with phone-first control

## Architecture

Built with 9 specialized AI agents orchestrated via LangGraph:

1. **Intake Agent** - Normalizes leads from all channels
2. **Research Agent** - Gathers intelligence on leads
3. **Scoring Agent** - Evaluates lead quality (0-10)
4. **Notification Agent** - Alerts reps with context
5. **Outreach Agent** - Personalized first contact
6. **Conversation Agent** - Handles ongoing dialogue
7. **Follow-Up Agent** - Re-engages silent leads
8. **Voice Agent** - Phone call handling
9. **Pipeline Agent** - CRM updates and analytics

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python 3.11+) |
| Agent Framework | LangGraph + LangChain |
| LLM | Google Gemini Pro 2.5 |
| Database | Supabase (PostgreSQL) |
| Vector DB | Pinecone |
| Cache/Queue | Redis |
| Frontend | Next.js 14 + Tailwind + shadcn/ui |
| Voice | Twilio + Deepgram + ElevenLabs |

## Quick Start

See [docs/SETUP.md](docs/SETUP.md) for complete setup instructions.

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis server
- Supabase account
- API keys (see `.env.example`)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## License
MIT
