# PR Title

## Summary
- What changed and why?

## Shard Citations (required)
- Link to relevant shard sections used to implement this change:
  - docs/shards/02-data-schema.md#... (tables/fields/indexes)
  - docs/shards/04-auth-rbac.md#... (RBAC enforcement)
  - docs/shards/05-devops-migrations.md#... (alembic flow)
  - docs/shards/03-billing-go-live.md#... (if billing-related)

## Migrations
- [ ] Alembic migration included
- [ ] Downgrade path implemented
- [ ] Tested on SQLite (CI) and SQL Server (local/docker)

## Security & RBAC
- [ ] Routes protected appropriately (Admin/User)
- [ ] Org isolation enforced

## Observability
- [ ] Structured logs and request_id present
- [ ] Health/readiness unaffected

## Screenshots / API Examples
- Optional but helpful

## Checklist
- [ ] Lints/tests pass
- [ ] Docs updated (story, roadmap, architecture/PRD if applicable)
