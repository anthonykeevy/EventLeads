# Architecture Map

Stack: Next.js (React + Tailwind + ShadCN CLI), FastAPI, SQL Server, Alembic.

Service boundaries
- Frontend: Next.js app for builder, auth, events, and render preview
- Backend: FastAPI APIs for auth, events, canvas, leads, invoices, billing
- DB: SQL Server via ODBC Driver 17; migrations via Alembic

Key routes (backend)
- /auth/*, /events/*, /canvas/*, /leads/*, /invoices/*, /billing/*

Links
- Docs shards: ./docs/shards
- PRD: ./docs/event-form-prd.md
- Tech: ./docs/tech-architecture.md



