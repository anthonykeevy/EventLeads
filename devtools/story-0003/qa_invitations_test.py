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
    """Return (org_id, admin_user_id)."""
    with engine.begin() as conn:
        # Ensure Organization
        row = conn.execute(text("SELECT TOP 1 OrganizationID FROM Organization ORDER BY OrganizationID")).first()
        org_id = int((row or [0])[0]) if row else 0
        if not org_id:
            conn.execute(text("INSERT INTO Organization (Name, CreatedDate) VALUES ('QA Org', GETUTCDATE())"))
            row2 = conn.execute(text("SELECT TOP 1 OrganizationID FROM Organization ORDER BY OrganizationID DESC")).first()
            org_id = int((row2 or [0])[0]) if row2 else 0
        # Ensure Admin role id
        rrow = conn.execute(text("SELECT TOP 1 RoleID FROM Role WHERE RoleName='Admin'")).first()
        if not rrow or rrow[0] is None:
            raise RuntimeError("Admin role not found in Role table")
        rid = int(rrow[0])
        # Ensure Admin user
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
    claims = {"sub": str(uid), "org_id": org_id, "role": "Admin"}
    from app.core.settings import settings  # type: ignore

    token = create_jwt_token(claims, settings.jwt_secret)
    headers = {"Authorization": f"Bearer {token}"}
    client = TestClient(app)

    invitee = f"qa_user_{int(datetime.now(tz=timezone.utc).timestamp())}@example.com"

    # Create invitation
    resp = client.post("/invitations/", json={"email": invitee, "role": "User"}, headers=headers)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["email"].lower() == invitee.lower()

    # Fetch token directly from DB for acceptance
    with engine.begin() as conn:
        trow = conn.execute(
            text("SELECT TOP 1 Token FROM Invitation WHERE Email=:e ORDER BY InvitationID DESC"),
            {"e": invitee},
        ).first()
        token_val = (trow or [None])[0]
        assert token_val, "Invitation token not found"

    # Accept invitation
    resp2 = client.post(f"/invitations/{token_val}/accept", json={"password": "StrongPassw0rd!"})
    assert resp2.status_code == 200, resp2.text

    print({"create_status": resp.status_code, "accept_status": resp2.status_code, "email": invitee})


if __name__ == "__main__":
    main()
