"""
Generate T-SQL to normalize legacy column names to v2 conventions:
- BIT columns should be prefixed with Is/Has
- Renames default constraints bound to those columns to DF_[Table]_[Column]

Output: prints T-SQL; use to create db/maintenance/legacy_fix_columns.sql
"""
from __future__ import annotations

from sqlalchemy import create_engine, text
from app.core.settings import settings


def rows(engine, sql: str):
    with engine.begin() as conn:
        return conn.execute(text(sql)).mappings().all()


def main() -> int:
    engine = create_engine(settings.database_url)
    plan: list[str] = []
    # Find BIT columns not starting with Is/Has
    cols = rows(
        engine,
        """
        SELECT t.name AS TableName, c.name AS ColumnName
        FROM sys.columns c
        JOIN sys.tables t ON t.object_id = c.object_id
        JOIN sys.types ty ON ty.user_type_id = c.user_type_id
        WHERE t.is_ms_shipped = 0 AND ty.name = 'bit' AND c.name NOT LIKE 'Is%' AND c.name NOT LIKE 'Has%'
        ORDER BY t.name, c.name
        """,
    )
    for r in cols:
        table = r["TableName"]
        old = r["ColumnName"]
        # Simple rule: prefix Is if not already Has; keep original casing after prefix
        new = f"Is{old[0].upper() + old[1:]}" if not old.startswith("Has") else old
        plan.append(f"-- Column rename: {table}.{old} -> {new}")
        plan.append(f"EXEC sp_rename '[dbo].[{table}].[{old}]', '{new}', 'COLUMN';")
        # Rename default constraint if exists
        plan.append(
            f"DECLARE @dc NVARCHAR(128); SELECT @dc = dc.name FROM sys.default_constraints dc JOIN sys.columns c ON c.object_id=dc.parent_object_id AND c.column_id=dc.parent_column_id JOIN sys.tables t ON t.object_id=c.object_id WHERE t.name='{table}' AND c.name='{new}'; IF @dc IS NOT NULL EXEC sp_rename @dc, 'DF_{table}_{new}', 'OBJECT';"
        )

    print("-- BEGIN LEGACY COLUMN FIX PLAN")
    for line in plan:
        print(line)
    print("-- END LEGACY COLUMN FIX PLAN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


