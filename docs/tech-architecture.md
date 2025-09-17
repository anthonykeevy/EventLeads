# 📐 Technical Architecture: Event Form Builder Platform

## 1. 🧱 Core Stack

| Layer       | Tech                                      |
| ----------- | ----------------------------------------- |
| Frontend    | React + Tailwind + ShadCN + Framer Motion |
| Backend     | FastAPI (Python)                          |
| ORM         | SQLAlchemy                                |
| Migrations  | Alembic                                   |
| Database    | SQL Server                                |
| Auth        | JWT + Role middleware                     |
| Payments    | Stripe SDK (Server + Client)              |
| DevOps      | Docker, GitHub Actions                    |
| Env Configs | `.env.dev`, `.env.test`, `.env.prod`      |

---

## 2. 🔁 Development & Environment Strategy

### Local (Dev)

* Host-installed SQL Server
* Alembic runs manually or on startup
* Migration history tracked in `/migrations`

### Test & Production

* Fully Dockerized (`docker-compose`)
* SQL Server container with mounted volume
* Alembic auto-applied at container startup
* GitHub Actions run migrations pre-deploy

### CI/CD Tooling

* Git pre-commit: `black`, `flake8`, `mypy`
* GitHub Actions: lint, test, migrate, build
* Docker images versioned & pushed

---

## 3. 🧪 Migrations & Versioning

* Schema changes must use **Alembic**
* No direct DDL in production
* Each feature branch includes migration script
* PRs check Alembic consistency
* **Database Standards**: Follow `docs/shards/02-data-schema.md` for data types and field standards

**Alembic Folders:**

```
/migrations
  /versions
    2023_10_15_initial.py
  env.py
  script.py.mako
```

**Commands:**

```bash
alembic revision --autogenerate -m "add CanvasObject"
alembic upgrade head
```

---

## 4. 🔐 Auth & Roles

* JWT-based auth
* Role-based RBAC middleware (`Admin`, `User`)
* Token expiration & refresh flows

---

## 5. 📦 Directory Structure

```
/backend
  /app
    /models
    /schemas
    /routers
    /services
    /auth
    /core
  /tests
  /migrations
  Dockerfile
  alembic.ini
/frontend
  /components
  /pages
  /lib
  tailwind.config.js
  .env
```

---

## 6. 🛠️ Deployment Workflow

1. Push to main → build/test/migration preview
2. Merge to `release/` → build frontend/backend → run Alembic migrations → deploy container to staging/prod

---

## 7. 👩‍🎨 UX Alignment Notes

1. Snapping/grid alignment must be implemented in UI; DB only enforces coordinates
2. Device previews: UI must guide creation of CanvasLayouts per device type
3. Accessibility: enforce defaults for contrast, tab order, visible labels
4. Undo/redo: expose RevisionNumber as user-facing version history
5. Preview URLs: must match CanvasObject data exactly for trust

---

✅ Architecture enables database evolution, testability, and production stability.


---

## 8. 🔌 API Base, Health, and Middleware (Consolidated v0.2)

- Base path: `/api/v1`
- Health: `GET /healthz` (liveness), `GET /readyz` (readiness)
- Middleware:
  - Request ID + structured logging
  - Error envelope with trace ID (Problem Details)
  - CORS for app and public form origins
  - Rate limiting for auth-sensitive endpoints

Shard refs: `docs/shards/02-data-schema.md`, `docs/shards/04-auth-rbac.md`

---

## 9. ✉️ Auth Flows: Email Verification & Password Reset (Consolidated v0.2)

- Email Verification
  - Table: `EmailVerificationToken(user_id, token, expires_at, consumed_at)`
  - Flow: signup → send token link → verify → activate account → redirect dashboard
  - Resend: cooldown (e.g., 60s) and daily cap
- Password Reset
  - Table: `PasswordResetToken(user_id, token, expires_at, consumed_at)`
  - Flow: request → email link → set new password → invalidate sessions
- Security
  - Tokens random 32+ bytes, one-time, expire in 30–60 min
  - Audit issuance and consumption; rate limit endpoints

Shard refs: `docs/shards/04-auth-rbac.md`

---

## 10. 🔧 Environment Variables (Consolidated v0.2)

Provide `.env.dev`, `.env.test`, `.env.prod`. Example keys are in `.env.example`:

```
APP_BASE_URL=
JWT_SECRET=
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASS=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
DB_DSN=
DEFAULT_TIMEZONE=UTC
```

---

## 11. 💳 Billing Enforcement (Consolidated v0.2)

- Event-day guard: compute "today" in `Event.timezone`; block submissions outside `[start_date, end_date]`
- Usage charges: on first production submission per day, insert `UsageCharge(event_id, charge_date, amount)` per schedule
- Invoicing: sum usage into invoices; handle via Stripe and webhooks

Shard refs: `docs/shards/03-billing-go-live.md`

---

## 12. 🗃️ Schema Updates Summary (v0.2)

- Event: add `timezone`, `end_date`, soft deletes
- New: `Form(id, event_id, name, status, public_slug, soft-delete)`
- CanvasLayout: add `form_id` (deprecate `event_id`)
- Lead: add `is_test`, `form_id`, soft-delete metadata
- New: `UsageCharge(org_id, event_id, charge_date, amount, source)` unique per day

Shard refs: `docs/shards/02-data-schema.md`

---

## 13. 🚀 Bootstrap & Seeding (v0.2)

- Seed `ObjectType`: TextField, DropdownField, Checkbox (see `docs/event-form-database.sql` v0.2 section)
- Admin bootstrap: create first Organization and Admin user on first run if none exist
- Provide `scripts/bootstrap_dev.py` (future) to initialize dev environment

---

## 14. 🔭 Observability & Monitoring (v0.2)

### Metrics & Tracing
* Expose Prometheus `/metrics`; instrument HTTP, DB, webhooks, entitlements
* Emit OpenTelemetry traces; propagate `X-Request-ID`

### Dashboards & Alerts
* Dashboards: Ops, Billing, Public Form, Auth/Email, Builder Perf
* Alerts: webhook error spikes, entitlement lag, public form latency, email bounce rate

### Logging & Audit
* Structured JSON with `request_id`, `org_id`, `event_id`, `form_id`; redact PII
* Audit actions: publish, archive/delete/restore, role changes, CSV exports, billing

### Product Analytics
* Track privacy-aware events (publish, extend days, submissions) with minimal metadata
