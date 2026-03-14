# 🚀 LeadForge — AI-Powered Sales Agent on Telegram

LeadForge is a fully autonomous, Telegram-native lead capture and sales pipeline system. Customers chat with your AI agent on Telegram, which qualifies them, scores them, and notifies you instantly. You approve or reject leads with one tap.

> **Telegram Bot:** [`@leadforge12_bot`](https://t.me/leadforge12_bot) — start a conversation or test the flow directly.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Conversational Capture** | Gemini-powered agent asks your custom questions naturally |
| 🌐 **Multi-language Support** | Customers choose **English, Hindi, or Marathi** at the start |
| 🆕 **New Enquiry (`/new`)** | Customers can start a fresh enquiry at any time |
| 📊 **Lead Scoring** | Automatic 0–10 scoring via a 9-agent LangGraph pipeline |
| 📲 **Instant Notifications** | Owner gets Telegram alert with Approve / Reject buttons |
| 🔁 **Smart Outreach** | Approved leads get personalized follow-up automatically |
| 📋 **CRM Commands** | Full pipeline management directly from Telegram |
| 🔊 **Voice Calls** *(optional)* | AI inbound/outbound calls via Twilio + Deepgram + ElevenLabs |

---

## 🏗️ Architecture

### 9-Agent AI Pipeline (LangGraph)

```
Customer Message
      │
      ▼
[1] Intake Agent       → Normalise lead from Telegram/Form/Email/Instagram
[2] Research Agent     → Web research on customer/company (Serper)
[3] Scoring Agent      → 0-10 lead quality score (Gemini)
[4] Notification Agent → Telegram alert to owner with Approve/Reject buttons
[5] Outreach Agent     → Personalised first contact (on approval)
[6] Conversation Agent → Ongoing dialogue handling
[7] Follow-Up Agent    → Re-engage silent leads
[8] Voice Agent        → Phone call handling (Twilio)
[9] Pipeline Agent     → CRM updates & analytics
```

### Tech Stack

| Component | Technology |
|---|---|
| Backend | FastAPI (Python 3.11+) |
| Agent Framework | LangGraph + LangChain |
| LLM | Google Gemini 2.5 Pro |
| Database | MongoDB (via Beanie ODM) |
| Vector DB | Pinecone |
| Cache | Redis *(optional)* |
| Translation | lingo.dev API |
| Voice | Twilio + Deepgram + ElevenLabs *(optional)* |
| Frontend | Next.js 14 + Tailwind *(optional — not required to run)* |

> **Note:** The **frontend is optional**. The entire product works through the Telegram bot. You do not need to start the frontend to use LeadForge.

---

## 🛠️ Quick Start

### Prerequisites

- Python 3.11+
- MongoDB Atlas account (free tier works)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Google Gemini API key
- ngrok (for local webhook exposure) or a deployed server
- lingo.dev API key (for Hindi/Marathi translation)

Optional (for email/voice features):
- SendGrid · Serper · Pinecone · Twilio · Deepgram · ElevenLabs

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/your-org/LeadForge.git
cd LeadForge/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Open .env and fill in your values (see comments in the file)
```

**Minimum required variables to run:**

```dotenv
MONGODB_URL=mongodb+srv://...
GOOGLE_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_BOT_USERNAME=leadforge12_bot
API_BASE_URL=https://your-ngrok-url.ngrok-free.app
```

### 3. Start the Backend

```bash
cd backend
uvicorn app.main:socket_app --host 0.0.0.0 --port 8005 --reload
```

### 4. Expose Locally with ngrok

```bash
ngrok http 8005
```

Copy the `https://xxxx.ngrok-free.app` URL into your `.env` as `API_BASE_URL`, then restart the backend.

### 5. Register the Telegram Webhook

```bash
# Replace YOUR_BOT_TOKEN and YOUR_NGROK_URL
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
  -d "url=https://YOUR_NGROK_URL/api/v1/webhooks/telegram" \
  -d "secret_token=YOUR_WEBHOOK_SECRET"
```

### 6. (Optional) Start the Frontend

```bash
cd frontend
npm install
npm run dev
# Available at http://localhost:3000
```

---

## 📲 Telegram User Flows

### Owner Setup

1. Open [`@leadforge12_bot`](https://t.me/leadforge12_bot) and send `/register`
2. The bot walks you through 8 steps:
   - Business name, industry, phone, email
   - Business hours, services offered
   - **5 custom AI questions** (the AI will ask these to customers)
   - Welcome message
3. You receive a **QR code** and a **customer deep link** to share
4. You are auto-connected to receive lead notifications

### Customer Enquiry Flow

1. Customer scans the QR code or clicks the link → bot opens
2. Bot asks: **"Choose your language"** → English / हिन्दी / मराठी
3. AI has a natural conversation, asking the owner's 5 questions
4. Once complete → lead is scored (0–10) → **owner gets notified on Telegram**
5. Owner taps **Approve** or **Reject**
6. Approved → outreach / follow-up pipeline starts automatically

### `/new` — Start a Fresh Enquiry

If a customer wants to enquire about something different:

```
Customer sends: /new
```

- The previous enquiry is **archived** (marked closed)
- The bot shows the language picker again
- A completely **new lead** is created in the system

---

## 🤖 Owner Commands (Telegram)

Send these directly to the bot after connecting:

| Command | Description |
|---|---|
| `/help` | Show all commands |
| `/stats` | Full business analytics |
| `/today` | Today's pipeline summary |
| `/leads` | Recent 10 leads with scores |
| `/customers` | All customers sorted by score |
| `/approved` | Approved enquiries |
| `/rejected` | Rejected enquiries |
| `/detail <lead_id>` | Full details of a specific lead |
| `approve <lead_id>` | Approve a lead |
| `reject <lead_id>` | Reject a lead |
| `won <lead_id> <amount>` | Mark a deal as won |
| `/register` | Register (or re-register) your business |

---

## 🚀 Deployment

### Deploy on Railway / Render

1. Connect your GitHub repo
2. Set all environment variables from `.env.example`
3. Set start command: `uvicorn app.main:socket_app --host 0.0.0.0 --port 8005`
4. Deploy → copy your public URL
5. Update `API_BASE_URL` to your deployed URL
6. Re-run the webhook registration `curl` command above

### Docker

```bash
docker-compose up --build
```

> The `docker-compose.yml` starts the backend. MongoDB and Redis can be external services.

---

## 📁 Project Structure

```
LeadForge/
├── backend/
│   ├── app/
│   │   ├── agents/           # 9 LangGraph AI agents
│   │   ├── api/v1/
│   │   │   └── webhooks.py   # Telegram, Instagram, Form, Email handlers
│   │   ├── models/           # MongoDB / Beanie ODM models
│   │   ├── services/
│   │   │   ├── telegram/     # Bot, onboarding wizard, templates
│   │   │   ├── translation.py # lingo.dev multi-language (EN/HI/MR)
│   │   │   ├── gemini_capture.py # AI conversation service
│   │   │   └── lead_workflow.py  # Two-phase pipeline orchestrator
│   │   ├── config.py         # All settings (pydantic-settings)
│   │   └── main.py           # FastAPI app + startup
│   ├── .env.example          # ← Copy this to .env
│   └── requirements.txt
├── frontend/                 # Next.js UI (optional)
├── docker-compose.yml
└── README.md
```

---

## 🌐 Language Support

LeadForge uses [lingo.dev](https://lingo.dev) for real-time translation.

| Language | Code |
|---|---|
| English | `en` |
| Hindi (हिन्दी) | `hi` |
| Marathi (मराठी) | `mr` |

- Customer messages are translated **to English** for AI processing
- AI replies are translated **back to the customer's language** before sending
- If `LINGODOTDEV_API_KEY` is not set, the app works in English only

---

## 📄 License

MIT
