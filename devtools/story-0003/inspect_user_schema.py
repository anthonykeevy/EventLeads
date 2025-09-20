import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Ensure backend is importable
repo_root = Path(__file__).resolve().parents[2]
backend_dir = repo_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.settings import settings  # type: ignore


def main() -> None:
    eng = create_engine(settings.database_url)
    with eng.connect() as c:
        rows = list(
            c.execute(
                text(
                    """
                    SELECT c.name AS ColumnName, t.name AS TypeName, c.is_nullable
                    FROM sys.columns c
                    JOIN sys.types t ON c.user_type_id = t.user_type_id
                    WHERE c.object_id = OBJECT_ID('[dbo].[User]')
                    ORDER BY c.column_id
                    """
                )
            )
        )
        for r in rows:
            print(r)


if __name__ == "__main__":
    main()




