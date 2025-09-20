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
        res = c.execute(
            text(
                "SELECT COALESCE(SettingKey, [Key]) as K, COALESCE(SettingValue, [Value]) as V "
                "FROM GlobalSetting WHERE COALESCE(SettingKey, [Key]) = 'invite_token_ttl_hours'"
            )
        )
        rows = [tuple(r) for r in res]
        print({"database_url": settings.database_url, "rows": rows})


if __name__ == "__main__":
    main()
