# Contributing

Workflow (BMAD): PRD → Story → Migration → Code → Tests → Review → Deploy

Requirements
- Cite shard sections in PR description (e.g., 02-data-schema: Constraints)
- Any model change requires Alembic migration + rollback

Setup
- Backend: see backend/README or ARCHITECTURE.md
- Frontend: Next.js app in ./frontend

Testing
- Run unit tests and Alembic `upgrade head` in CI



