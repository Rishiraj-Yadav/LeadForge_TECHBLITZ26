# API Overview

## Core endpoints

### Health
- GET /health

### Auth
- POST /api/v1/auth/signup
- POST /api/v1/auth/login

### Leads
- GET /api/v1/leads/
- POST /api/v1/leads/
- GET /api/v1/leads/{lead_id}
- PATCH /api/v1/leads/{lead_id}

### Webhooks
- GET /api/v1/webhooks/whatsapp
- POST /api/v1/webhooks/whatsapp
- POST /api/v1/webhooks/instagram
- POST /api/v1/webhooks/telegram
- POST /api/v1/webhooks/form
- POST /api/v1/webhooks/email

### Notifications
- POST /api/v1/notifications/approve/{lead_id}
- POST /api/v1/notifications/reject/{lead_id}
- GET /api/v1/notifications/pipeline-summary

### Voice
- POST /api/v1/voice/incoming
- POST /api/v1/voice/gather

## Example form webhook request

```json
{
  "business_id": "00000000-0000-0000-0000-000000000000",
  "name": "Asha",
  "phone": "+919999999999",
  "email": "asha@example.com",
  "message": "Need catering for 80 guests next Friday",
  "source_url": "https://example.com/contact"
}
```
