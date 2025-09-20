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
    if len(sys.argv) < 3:
        print({"error": "usage: set_setting.py key value"})
        sys.exit(1)
    key = sys.argv[1]
    value = sys.argv[2]
    eng = create_engine(settings.database_url)
    with eng.begin() as c:
        # Try preferred columns first, fallback to legacy
        updated = c.execute(
            text(
                "UPDATE GlobalSetting SET SettingValue=:v WHERE COALESCE(SettingKey, [Key]) = :k"
            ),
            {"v": value, "k": key},
        ).rowcount
        if updated == 0:
            # Insert if missing (idempotent)
            try:
                c.execute(
                    text(
                        "INSERT INTO GlobalSetting (SettingKey, SettingValue, ValueType, Scope) VALUES (:k, :v, 'int', 'global')"
                    ),
                    {"k": key, "v": value},
                )
            except Exception:
                c.execute(
                    text(
                        "INSERT INTO GlobalSetting ([Key], [Value], ValueType, Scope) VALUES (:k, :v, 'int', 'global')"
                    ),
                    {"k": key, "v": value},
                )
    print({"updated": True, "key": key, "value": value})


if __name__ == "__main__":
    main()




