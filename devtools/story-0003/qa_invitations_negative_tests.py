import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

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

    token_jwt = create_jwt_token({"sub": str(uid), "org_id": org_id, "role": "Admin"}, settings.jwt_secret)
    headers = {"Authorization": f"Bearer {token_jwt}"}
    client = TestClient(app)

    # Create a fresh invite to manipulate
    invitee = f"qa_user_neg_{int(datetime.now(tz=timezone.utc).timestamp())}@example.com"
    r = client.post("/invitations/", json={"email": invitee, "role": "User"}, headers=headers)
    assert r.status_code == 201, r.text
    with engine.begin() as conn:
        trow = conn.execute(text("SELECT TOP 1 InvitationID, Token FROM Invitation WHERE Email=:e ORDER BY InvitationID DESC"), {"e": invitee}).first()
        inv_id = int((trow or [0, None])[0]) if trow else 0
        inv_token = (trow or [None, None])[1]
        assert inv_id and inv_token

    results = {}

    # Expired token -> 410
    with engine.begin() as conn:
        conn.execute(text("UPDATE Invitation SET ExpiresAt = DATEADD(day, -1, GETUTCDATE()) WHERE InvitationID = :id"), {"id": inv_id})
    r_exp = client.post(f"/invitations/{inv_token}/accept", json={"password": "StrongPassw0rd!"})
    results["expired_status"] = r_exp.status_code

    # Consumed token -> 410
    with engine.begin() as conn:
        conn.execute(text("UPDATE Invitation SET ConsumedAt = GETUTCDATE(), ExpiresAt = DATEADD(day, 1, GETUTCDATE()) WHERE InvitationID = :id"), {"id": inv_id})
    r_cons = client.post(f"/invitations/{inv_token}/accept", json={"password": "StrongPassw0rd!"})
    results["consumed_status"] = r_cons.status_code

    # Invalid token -> 404
    r_inv = client.post("/invitations/invalid_token_value/accept", json={"password": "StrongPassw0rd!"})
    results["invalid_status"] = r_inv.status_code

    # Rate limit: attempt many creates to trigger 429
    last_status = None
    retry_after = None
    for i in range(12):
        rr = client.post("/invitations/", json={"email": f"rate_{i}_{invitee}", "role": "User"}, headers=headers)
        last_status = rr.status_code
        if last_status == 429:
            retry_after = rr.headers.get("retry-after") or rr.headers.get("Retry-After")
            break
    results["rate_limit_status"] = last_status
    results["retry_after"] = retry_after

    print(results)


if __name__ == "__main__":
    main()




