# VoiceAI Follow-up Service

Minimal Flask service to send follow-up emails when calls fail or are declined.

## Endpoints

- `GET /health` → returns `{ "status": "ok" }`
- `POST /followup` → sends an email

### POST /followup payload
```json
{
  "email": "lead@example.com",
  "reason": "no-answer",
  "phoneNumber": "+15551234567",
  "leadId": "abc123"
}
```

## Environment Variables

Required:
- `EMAIL_SENDER`
- `EMAIL_PASSWORD`

Optional:
- `EMAIL_SUBJECT` (default: "We tried to reach you")
- `EMAIL_HTML` (custom HTML body)
- `SMTP_SERVER` (default: smtp.gmail.com)
- `SMTP_PORT` (default: 587)
- `FOLLOWUP_WEBHOOK_SECRET` (if set, must send header `x-webhook-secret`)

## Render Commands

Build:
```
pip install -r requirements.txt
```

Start:
```
gunicorn app:app
```
