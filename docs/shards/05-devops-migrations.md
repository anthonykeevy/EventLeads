# DevOps & Migrations

## Alembic Flow
- Define/modify models → autogenerate revision → review/adjust → upgrade

## Branch Policy
- feature/* → PR → main; require shard citations in PR description

## Rollback Steps
- `alembic downgrade -1`; if data migration needed, include reversible scripts

## Env Matrix
- dev/test/prod; CI uses SQLite for migrations; production uses SQL Server via ODBC Driver 17



