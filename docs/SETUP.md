# Setup Guide

## 1. What works today

This repository is set up to run locally on Windows with:

- FastAPI backend on port 8000
- Next.js frontend on port 3000
- Redis on port 6379
- Supabase Postgres as the database
- Telegram webhook for customer messages and rep commands

Use the local workflow first. There is a docker-compose.yml file in the repo root, but the backend and frontend Dockerfiles are not present, so Docker Compose is not the reliable path right now.

## 2. Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- Docker Desktop or a local Redis installation
- A Supabase project
- A Telegram bot created with BotFather
- API keys for Gemini, Pinecone, Serper, SendGrid, Twilio, Deepgram, and ElevenLabs if you want those integrations active

## 3. Project structure you will run

- Backend API: backend
- Frontend dashboard: frontend
- Main backend entrypoint: backend/app/main.py
- Main setup guide: docs/SETUP.md

## 4. Environment files

The backend reads variables from backend/.env. The frontend reads variables from frontend/.env.local.

Required backend variables:

- DATABASE_URL
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY
- REDIS_URL
- GOOGLE_API_KEY
- GEMINI_MODEL
- TELEGRAM_BOT_TOKEN
- TELEGRAM_WEBHOOK_SECRET
- REP_TELEGRAM_CHAT_ID

Recommended optional backend variables:

- INSTAGRAM_ACCESS_TOKEN
- INSTAGRAM_BUSINESS_ACCOUNT_ID
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_PHONE_NUMBER
- DEEPGRAM_API_KEY
- ELEVENLABS_API_KEY
- ELEVENLABS_VOICE_ID
- SENDGRID_API_KEY
- SENDGRID_FROM_EMAIL
- SERPER_API_KEY
- PINECONE_API_KEY
- PINECONE_INDEX_NAME
- PINECONE_ENVIRONMENT

Required frontend variables:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SOCKET_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 5. Supabase setup

1. Create a Supabase project.
2. Copy the project URL into SUPABASE_URL.
3. Copy the anon key into SUPABASE_ANON_KEY and NEXT_PUBLIC_SUPABASE_ANON_KEY.
4. Copy the service role key into SUPABASE_SERVICE_ROLE_KEY.
5. Copy the Postgres connection string into DATABASE_URL.

Notes:

- The backend creates tables on startup in development through SQLAlchemy.
- You do not need Alembic to do the first local boot for this repo.

## 6. Redis setup

If you have Docker Desktop running, start Redis with:

```powershell
docker run --name leadforge-redis -p 6379:6379 redis:7-alpine
```

Set:

```env
REDIS_URL=redis://localhost:6379/0
```

If that container already exists, start it again with:

```powershell
docker start leadforge-redis
```

## 7. Backend setup

From the repo root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload
```

Why socket_app and not app.main:app:

- The file mounts Socket.IO through socket_app.
- Using socket_app gives you both the HTTP API and the Socket.IO server together.

Backend checks:

- Health endpoint: http://localhost:8000/health
- Swagger docs: http://localhost:8000/docs

If startup fails immediately, check these first:

- DATABASE_URL is valid
- Redis is running
- backend/.env exists

## 8. Frontend setup

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL:

- http://localhost:3000

## 9. Telegram bot setup

### Create the bot

1. Open Telegram.
2. Talk to BotFather.
3. Run /newbot.
4. Copy the bot token into TELEGRAM_BOT_TOKEN.

### Get your rep chat id

1. Send any message to your bot from your own Telegram account.
2. In a browser, open:

```text
https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
```

3. Find message.chat.id in the JSON.
4. Put that value into REP_TELEGRAM_CHAT_ID.

That chat id is where rep notifications and rep commands will work.

## 10. Expose your local backend to Telegram

Telegram webhooks need a public HTTPS URL. For local development, use ngrok.

Start ngrok in a third terminal:

```powershell
ngrok http 8000
```

Copy the HTTPS forwarding URL from ngrok, for example:

```text
https://abc123.ngrok-free.app
```

## 11. Register the Telegram webhook

Use PowerShell to register the webhook:

```powershell
$body = @{
  url = "https://YOUR_NGROK_URL/api/v1/webhooks/telegram"
  secret_token = "YOUR_TELEGRAM_WEBHOOK_SECRET"
} | ConvertTo-Json

Invoke-RestMethod \
  -Method Post \
  -Uri "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
  -ContentType "application/json" \
  -Body $body
```

Expected success response:

```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

To verify the webhook later:

```powershell
Invoke-RestMethod -Method Get -Uri "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

## 12. End-to-end local run order

Start things in this order:

1. Redis
2. Backend
3. Frontend
4. ngrok
5. Telegram webhook registration
6. Telegram chat test

## 13. How to test Telegram end to end

### Customer message flow

1. Send a normal message to your bot from any Telegram account.
2. Telegram sends the webhook to:

```text
POST /api/v1/webhooks/telegram
```

3. The backend creates or updates a lead in the database.
4. The lead workflow runs through intake, research, scoring, and notification.
5. A rep notification should arrive in the REP_TELEGRAM_CHAT_ID chat.

### Rep command flow

From the same rep Telegram chat, test these commands:

- today
- leads
- approve LEAD_ID
- reject LEAD_ID
- won LEAD_ID 5000

You can get a lead id from the rep notification text or from the backend API.

### Approval button flow

If a notification arrives with inline buttons:

- Approve should mark the lead approved and trigger outreach
- Reject should mark the lead lost

This repo now accepts both approve and approved, and both reject and rejected, so the Telegram callback buttons and typed commands use the same backend decision path.

## 14. How to verify it is actually working

Check these URLs while the app is running:

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- Backend health: http://localhost:8000/health

Useful API checks from Swagger or another client:

- POST /api/v1/webhooks/form
- GET /api/v1/leads/
- GET /api/v1/leads/{lead_id}/conversations

Signs the Telegram integration is working:

- getWebhookInfo shows your ngrok URL
- Sending a Telegram message returns no Telegram-side error
- The backend logs show the webhook request
- A lead appears in the leads API
- The rep receives a Telegram notification

## 15. Troubleshooting

### Telegram bot does not respond

Check:

- TELEGRAM_BOT_TOKEN is correct
- ngrok is still running
- getWebhookInfo points to the current ngrok URL
- TELEGRAM_WEBHOOK_SECRET matches the registered secret
- backend is running on port 8000

### Frontend loads but shows no data

Check:

- frontend/.env.local exists
- NEXT_PUBLIC_API_URL is http://localhost:8000
- backend /health works
- Supabase keys are valid

### Backend crashes on startup

Check:

- DATABASE_URL format
- Redis availability
- Missing Python packages from requirements.txt

### Rep commands do not work

Check:

- You are sending commands from the same chat id stored in REP_TELEGRAM_CHAT_ID
- The webhook is reaching the backend
- The command format includes a real UUID lead id

## 16. Optional services

You can run the basic Telegram flow first with just:

- Supabase
- Redis
- Gemini
- Telegram

These can be added later without blocking the first end-to-end test:

- Instagram Graph API
- Twilio voice and SMS
- Deepgram
- ElevenLabs
- SendGrid
- Pinecone
- Serper

## 17. Production direction

Recommended deployment split:

- Frontend: Vercel
- Backend: Railway or another HTTPS host
- Redis: Railway Redis or Upstash
- Database: Supabase

For production, replace ngrok with a permanent HTTPS domain and register that domain as the Telegram webhook target.
