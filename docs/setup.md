# Developer Setup

This guide describes how to run the Event Leads project locally for development.

## Prerequisites
- Python 3.11
- Node.js 18+
- SQL Server (local or container)
- ODBC Driver 17 for SQL Server
- Git, Docker (optional for DB)

## Environment
1) Copy `.env.example` to the desired env file (e.g., `.env.dev`) and set values:
```
cp .env.example .env.dev
```
Key fields:
- `DB_DSN` — SQL Server DSN using ODBC Driver 17
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` — Stripe test keys
- `SMTP_*` or email provider token
- `DEFAULT_TIMEZONE` — default fallback (UTC)

2) Billing config
- Use `docs/billing-config.example.yaml` (dev defaults). Reference path via `BILLING_CONFIG_PATH`.

## Database
1) Create database/schema in SQL Server
2) Apply migrations (to be created with Alembic):
```
# placeholder commands
alembic upgrade head
```
3) Optional: Seed base data (ObjectTypes). If using Alembic, seeds will be included; otherwise run the SQL tail section in `docs/event-form-database.sql` v0.2.

## Backend (FastAPI)
- Install deps and run dev server:
```
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
- Health endpoints: `/healthz`, `/readyz`
- API base: `/api/v1`

## Frontend (React + Tailwind)
- Install deps and run:
```
cd frontend
npm install
npm run dev
```
- The public form and builder routes are described in `docs/front-end-spec.md`.

## Webhooks (Stripe)
- Expose local URL (stripe CLI or ngrok) and register webhook secret
- See `docs/webhooks-stripe.md` for event handling and idempotency

## Test Accounts
- Use Stripe test cards (4242 4242 4242 4242)
- Use MailHog/Mailpit for local SMTP and email verification

## Troubleshooting
- ODBC Driver issues: ensure Driver 17 installed; verify DSN string encoding
- Migrations: confirm `alembic.ini` points to your DSN; run `alembic current`
- Webhooks: confirm signature verification using the configured secret
