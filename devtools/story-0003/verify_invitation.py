import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Ensure backend app is on sys.path regardless of where this script is run from
repo_root = Path(__file__).resolve().parents[2]
backend_dir = repo_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.settings import settings  # type: ignore


def main() -> None:
    eng = create_engine(settings.database_url)
    with eng.connect() as c:
        exists = c.execute(
            text("SELECT COUNT(1) FROM sys.objects WHERE type='U' AND name='Invitation'")
        ).scalar()
        rows = []
        if exists:
            rows = [tuple(r) for r in c.execute(text("SELECT TOP 1 * FROM Invitation"))]
        print({"database_url": settings.database_url, "exists": bool(exists), "sample": rows})


if __name__ == "__main__":
    main()
