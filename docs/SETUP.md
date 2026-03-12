# Setup Guide

## 1. Prerequisites

- Python 3.11+
- Node.js 18+
- Redis
- Supabase project
- Meta developer account for WhatsApp and Instagram
- Telegram account for bot creation
- Twilio account for voice
- Deepgram, ElevenLabs, Serper, and Pinecone accounts

## 2. Clone and install

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## 3. Environment files

- Copy root .env.example into your working notes and fill every required value.
- Update backend/.env for backend runtime.
- Update frontend/.env.local for browser-side variables.

## 4. Supabase setup

1. Create a new project at https://supabase.com.
2. Open Project Settings -> API.
3. Copy SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_SERVICE_ROLE_KEY.
4. Open Project Settings -> Database and copy the connection string into DATABASE_URL.
5. Create tables with your migration strategy. For this scaffold, initial tables are created by SQLAlchemy on startup in development.

## 5. Redis setup

### Local Redis

```bash
docker run -p 6379:6379 redis:7-alpine
```

Set REDIS_URL=redis://localhost:6379/0.

## 6. Gemini setup

1. Open https://aistudio.google.com/apikey.
2. Create an API key.
3. Put it in GOOGLE_API_KEY.
4. Keep GEMINI_MODEL=gemini-2.5-pro unless you deliberately switch models.

## 7. WhatsApp Cloud API setup

1. Go to https://developers.facebook.com and create an app.
2. Add the WhatsApp product.
3. Open WhatsApp -> API Setup.
4. Copy the temporary access token, phone number ID, and business account ID.
5. Put them in WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_BUSINESS_ACCOUNT_ID.
6. Choose a custom verify token and set WHATSAPP_VERIFY_TOKEN.
7. Expose your backend over HTTPS using Railway or ngrok.
8. In Meta webhook configuration, use:
   https://YOUR_DOMAIN/api/v1/webhooks/whatsapp
9. Use the same verify token when Meta asks for verification.
10. Subscribe to messages field updates.

## 8. Instagram Graph API setup

1. Use the same Meta app.
2. Add Instagram permissions and connect an Instagram Business account.
3. Configure the messaging webhook endpoint:
   https://YOUR_DOMAIN/api/v1/webhooks/instagram
4. Save access token and account ID into INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID.

## 9. Telegram Bot setup

1. In Telegram, message BotFather.
2. Run /newbot.
3. Copy the generated token into TELEGRAM_BOT_TOKEN.
4. Send a message to your bot from your own Telegram account.
5. Visit:
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
6. Find your chat id and place it into REP_TELEGRAM_CHAT_ID.
7. Register webhook:
   https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://YOUR_DOMAIN/api/v1/webhooks/telegram

## 10. Twilio voice setup

1. Create a Twilio account.
2. Buy or provision a phone number with voice enabled.
3. Copy account SID, auth token, and phone number into env values.
4. In Twilio console, configure voice webhook for the number:
   https://YOUR_DOMAIN/api/v1/voice/incoming
5. If you want real-time audio streaming, add your own public WebSocket endpoint and update the placeholder URL in the voice route.

## 11. Deepgram and ElevenLabs

1. Create accounts.
2. Generate API keys.
3. Put them in DEEPGRAM_API_KEY and ELEVENLABS_API_KEY.
4. Choose a voice ID in ElevenLabs and set ELEVENLABS_VOICE_ID.

## 12. SendGrid

1. Create API key.
2. Verify sender email.
3. Set SENDGRID_API_KEY and SENDGRID_FROM_EMAIL.

## 13. Serper and Pinecone

1. Create API keys.
2. Put the Serper key into SERPER_API_KEY.
3. Create a Pinecone index named leadforge-conversations and set PINECONE_API_KEY and PINECONE_INDEX_NAME.

## 14. Run the project

### Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm run dev
```

## 15. Test the flow

1. Open http://localhost:3000.
2. Open backend docs at http://localhost:8000/docs.
3. Post a sample lead to POST /api/v1/webhooks/form.
4. Check the resulting state and dashboard scaffold.

## 16. Production deployment

- Frontend: Vercel
- Backend + Redis: Railway
- Database: Supabase
- Add Sentry, PostHog, and Better Stack before going live
