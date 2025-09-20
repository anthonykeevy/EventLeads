import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Ensure backend app is importable
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
                    "SELECT COALESCE(SettingKey, [Key]) as K, COALESCE(SettingValue, [Value]) as V "
                    "FROM GlobalSetting WHERE COALESCE(SettingKey, [Key]) in ('invite_token_ttl_hours','invite_daily_limit') "
                    "ORDER BY 1"
                )
            )
        )
        print(rows)


if __name__ == "__main__":
    main()




