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

