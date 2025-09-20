import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure backend is importable
repo_root = Path(__file__).resolve().parents[2]
backend_dir = repo_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient  # type: ignore
from sqlalchemy import text

from app.main import app  # type: ignore
from app.core.db import engine  # type: ignore
from app.utils.security import create_jwt_token  # type: ignore


def ensure_org_and_admin() -> tuple[int, int]:
    with engine.begin() as conn:
        row = conn.execute(text("SELECT TOP 1 OrganizationID FROM Organization ORDER BY OrganizationID")).first()
        org_id = int((row or [0])[0]) if row else 0
        if not org_id:
            conn.execute(text("INSERT INTO Organization (Name, CreatedDate) VALUES ('QA Org', GETUTCDATE())"))
            row2 = conn.execute(text("SELECT TOP 1 OrganizationID FROM Organization ORDER BY OrganizationID DESC")).first()
            org_id = int((row2 or [0])[0]) if row2 else 0
        rrow = conn.execute(text("SELECT TOP 1 RoleID FROM Role WHERE RoleName='Admin'")).first()
        if not rrow or rrow[0] is None:
            raise RuntimeError("Admin role not found")
        rid = int(rrow[0])
        urow = conn.execute(text("SELECT TOP 1 UserID FROM [User] WHERE Email='qa_invite_admin@example.com' ORDER BY UserID DESC")).first()
        uid = int((urow or [0])[0]) if urow else 0
        if not uid:
            conn.execute(
                text(
                    "INSERT INTO [User] (RoleID, OrganizationID, Username, FirstName, LastName, Email, PasswordHash, PasswordSalt, IsActive, EmailVerified, TwoFactorEnabled, CreatedDate, CreatedBy) "
                    "VALUES (:rid, :oid, :uname, :fn, :ln, :email, '', '', 1, 1, 0, GETUTCDATE(), :created_by)"
                ),
                {
                    "rid": rid,
                    "oid": org_id,
                    "uname": "qa_invite_admin",
                    "fn": "QA",
                    "ln": "Admin",
                    "email": "qa_invite_admin@example.com",
                    "created_by": "system",
                },
            )
            urow2 = conn.execute(text("SELECT TOP 1 UserID FROM [User] WHERE Email='qa_invite_admin@example.com' ORDER BY UserID DESC")).first()
            uid = int((urow2 or [0])[0]) if urow2 else 0
    return org_id, uid


def main() -> None:
    org_id, uid = ensure_org_and_admin()
    from app.core.settings import settings  # type: ignore

    token = create_jwt_token({"sub": str(uid), "org_id": org_id, "role": "Admin"}, settings.jwt_secret)
    headers = {"Authorization": f"Bearer {token}"}
    client = TestClient(app)

    nowts = int(datetime.now(tz=timezone.utc).timestamp())
    payload = {
        "email": f"invite_{nowts}@example.com",
        "role": "User",
        "first_name": "Sam",
        "last_name": "Tester",
    }
    resp = client.post("/invitations/", json=payload, headers=headers)
    print(resp.status_code, resp.json())


if __name__ == "__main__":
    main()




