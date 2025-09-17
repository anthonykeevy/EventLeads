# DevOps & Migrations

## Alembic Flow
- Define/modify models → autogenerate revision → review/adjust → upgrade

Policy
- Any model change requires an Alembic migration with a rollback path.
- Never apply direct DDL in production; use Alembic scripts only.

## Branch Policy
- feature/* → PR → main; require shard citations in PR description

PR Requirements
- Include migration script(s) for schema changes.
- CI must run `alembic upgrade head` on ephemeral DBs before merge.

## Rollback Steps
- `alembic downgrade -1`; if data migration needed, include reversible scripts

## Env Matrix
- dev/test/prod; CI uses SQLite for migrations; production uses SQL Server via ODBC Driver 17

CI Migration Matrix
- Run migration previews on SQLite and SQL Server (container) to ensure compatibility.



