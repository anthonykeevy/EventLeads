from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field, constr
from sqlalchemy import text

from ..core.db import engine
from ..core.settings import settings
from ..services.emailer import send_email
from ..services.settings_service import settings_service
from .auth import auth_dependency, get_role_id, write_auth_event


router = APIRouter(prefix="/invitations", tags=["invitations"])


class CreateInvitationRequest(BaseModel):
    email: EmailStr
    role: str = Field(min_length=3, max_length=50)
    first_name: constr(min_length=1, max_length=100)  # required
    last_name: constr(min_length=1, max_length=100)   # required


class CreateInvitationResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    expires_at: datetime


class AcceptInvitationRequest(BaseModel):
    password: str = Field(min_length=8, max_length=200)


class InvitationPreviewResponse(BaseModel):
    email: EmailStr
    inviter_name: str


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _get_rate_limit_remaining_for_org(org_id: int) -> tuple[int, int]:
    """Return (count_last_day, limit_per_day)."""
    limit_per_day = settings_service.get_invite_daily_limit()
    with engine.begin() as conn:
        count_today = conn.execute(
            text(
                "SELECT COUNT(1) FROM Invitation WHERE OrganizationID = :oid "
                "AND CreatedAt > DATEADD(day, -1, GETUTCDATE())"
            ),
            {"oid": org_id},
        ).scalar()
    count = int(count_today or 0)
    return count, limit_per_day


def _require_admin(claims: dict) -> None:
    role = (claims or {}).get("role")
    if role not in {"Admin", "SystemAdmin"}:
        raise HTTPException(status_code=403, detail="Admin required")


@router.post("/", response_model=CreateInvitationResponse, status_code=201)
def create_invitation(
    payload: CreateInvitationRequest,
    request: Request,
    claims: dict = Depends(auth_dependency),
):
    _require_admin(claims)
    org_id = claims.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="Missing org context")

    # Rate limit per org per day
    used, limit = _get_rate_limit_remaining_for_org(int(org_id))
    if used >= limit:
        headers = {"Retry-After": "3600"}
        raise HTTPException(status_code=429, detail="Invite rate limit reached", headers=headers)

    # TTL
    ttl_hours = settings_service.get_invite_token_ttl_hours()
    expires = _now().replace(tzinfo=None) + timedelta(hours=ttl_hours)
    token = secrets.token_urlsafe(32)

    role_id = get_role_id(payload.role) or get_role_id("User")
    if role_id is None:
        raise HTTPException(status_code=400, detail="Invalid role")

    with engine.begin() as conn:
        # Pre-create or update the user record so invited users belong to the organisation immediately
        existing = conn.execute(
            text("SELECT TOP 1 UserID, OrganizationID FROM [User] WHERE Email = :email ORDER BY UserID DESC"),
            {"email": str(payload.email)},
        ).first()
        username = str(payload.email).split("@")[0]
        first_name = payload.first_name.strip()
        last_name = payload.last_name.strip()
        if not existing:
            conn.execute(
                text(
                    "INSERT INTO [User] (RoleID, OrganizationID, Username, FirstName, LastName, Email, PasswordHash, PasswordSalt, IsActive, EmailVerified, TwoFactorEnabled, CreatedDate, CreatedBy) "
                    "VALUES (:rid, :oid, :uname, :fn, :ln, :email, '', '', 1, 0, 0, GETUTCDATE(), :created_by)"
                ),
                {
                    "rid": role_id,
                    "oid": int(org_id),
                    "uname": username,
                    "fn": first_name,
                    "ln": last_name,
                    "email": str(payload.email),
                    "created_by": str(int(claims.get("sub"))),
                },
            )
        else:
            # Ensure org and role are set (do not overwrite names for existing accounts)
            conn.execute(
                text(
                    "UPDATE [User] SET OrganizationID = COALESCE(OrganizationID, :oid), RoleID = :rid WHERE Email = :email"
                ),
                {"oid": int(org_id), "rid": role_id, "email": str(payload.email)},
            )

        conn.execute(
            text(
                "INSERT INTO Invitation (OrganizationID, Email, Role, Token, ExpiresAt, ConsumedAt, CreatedBy, CreatedAt) "
                "VALUES (:oid, :email, :role, :token, :exp, NULL, :uid, GETUTCDATE())"
            ),
            {
                "oid": int(org_id),
                "email": str(payload.email),
                "role": payload.role,
                "token": token,
                "exp": expires,
                "uid": int(claims.get("sub")),
            },
        )
        row = conn.execute(
            text(
                "SELECT TOP 1 InvitationID FROM Invitation WHERE OrganizationID=:oid AND Email=:email ORDER BY InvitationID DESC"
            ),
            {"oid": int(org_id), "email": str(payload.email)},
        ).first()
        inv_id = int(row[0]) if row and row[0] else 0

    # Send invitation email (plain + HTML)
    accept_url = f"http://localhost:3000/invite/accept?token={token}"
    inviter_name = ""  # best-effort fetch of inviter's display name
    try:
        with engine.begin() as conn:
            row_un = conn.execute(
                text("SELECT TOP 1 COALESCE(FirstName+' '+LastName, Username, Email) FROM [User] WHERE UserID = :uid"),
                {"uid": int(claims.get("sub"))},
            ).first()
            inviter_name = (row_un or [""])[0] or ""
    except Exception:
        inviter_name = ""
    ttl_hours = ttl_hours  # already computed
    plain = (
        f"{inviter_name or 'An Admin'} invited you to join Event Leads.\n\n"
        f"Click the invitation link below to set your password and join: \n{accept_url}\n\n"
        f"This invitation is valid for {ttl_hours} hours. If it expires, please ask {inviter_name or 'your admin'} to resend it."
    )
    html = f"""
    <html>
      <body style=\"font-family:Segoe UI, Arial, sans-serif; color:#1f2937;\">
        <h2 style=\"color:#111827;\">You're invited to Event Leads</h2>
        <p>
          <strong>{inviter_name or 'An Admin'}</strong> has invited you to join
          <strong>Event Leads</strong> for their organisation.
        </p>
        <p>
          When you click the button below, you'll be prompted to set your password before entering the site.
        </p>
        <p>
          <a href=\"{accept_url}\" style=\"background:#2563eb;color:#fff;padding:10px 16px;text-decoration:none;border-radius:6px;display:inline-block;\">Accept Invitation</a>
        </p>
        <p style=\"margin-top:16px;\">
          This invitation is valid for <strong>{ttl_hours} hours</strong>. If the link has expired, please reach out to {inviter_name or 'your admin'} to send a new invitation.
        </p>
        <hr style=\"margin:20px 0;border:none;border-top:1px solid #e5e7eb;\" />
        <p style=\"font-size:12px;color:#6b7280;\">
          If the button doesn't work, paste this link in your browser:<br/>
          <span style=\"word-break:break-all;\">{accept_url}</span>
        </p>
      </body>
    </html>
    """
    send_email(to=str(payload.email), subject="You're invited to Event Leads", body=plain, html_body=html)

    write_auth_event(
        engine,
        event_type="invite_create",
        status="success",
        email=str(payload.email),
        org_id=int(org_id),
        user_id=int(claims.get("sub")),
        request=request,
    )

    return CreateInvitationResponse(
        id=inv_id, email=payload.email, role=payload.role, expires_at=expires
    )


@router.get("/{token}/preview", response_model=InvitationPreviewResponse)
def preview_invitation(token: str):
    with engine.begin() as conn:
        inv = conn.execute(
            text(
                "SELECT TOP 1 OrganizationID, Email, CreatedBy FROM Invitation WHERE Token = :t ORDER BY InvitationID DESC"
            ),
            {"t": token},
        ).mappings().first()
        if not inv:
            raise HTTPException(status_code=404, detail="Invalid token")
        inviter_name = ""
        try:
            # CreatedBy may be user id or string; handle both
            created_by = inv.get("CreatedBy")
            if created_by is not None and str(created_by).isdigit():
                row = conn.execute(
                    text(
                        "SELECT TOP 1 COALESCE(FirstName+' '+LastName, Username, Email) FROM [User] WHERE UserID = :uid"
                    ),
                    {"uid": int(created_by)},
                ).first()
                inviter_name = (row or [""])[0] or ""
        except Exception:
            inviter_name = ""
    return InvitationPreviewResponse(email=inv["Email"], inviter_name=inviter_name or "Admin")


@router.post("/{token}/accept", response_model=dict)
def accept_invitation(token: str, payload: AcceptInvitationRequest, request: Request):
    # Look up invitation
    with engine.begin() as conn:
        inv = conn.execute(
            text(
                "SELECT TOP 1 InvitationID, OrganizationID, Email, Role, ExpiresAt, ConsumedAt, CreatedBy "
                "FROM Invitation WHERE Token = :t ORDER BY InvitationID DESC"
            ),
            {"t": token},
        ).mappings().first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invalid token")
    if inv["ConsumedAt"] is not None or (
        inv["ExpiresAt"] and inv["ExpiresAt"] < _now().replace(tzinfo=None)
    ):
        raise HTTPException(status_code=410, detail="Token expired")

    # Create user if not exists, assign role, attach to org
    from .auth import get_user_by_email, hash_password  # lazy import

    user = get_user_by_email(inv["Email"]) or {}
    role_id = get_role_id(inv["Role"]) or get_role_id("User")
    if role_id is None:
        raise HTTPException(status_code=400, detail="Invalid invite role")

    salt = ""
    pwd_hash = hash_password(salt, payload.password)
    username = inv["Email"].split("@")[0]
    created_by = str(inv.get("CreatedBy") or "system")

    with engine.begin() as conn:
        if not user:
            conn.execute(
                text(
                    "INSERT INTO [User] (RoleID, OrganizationID, Username, FirstName, LastName, Email, PasswordHash, PasswordSalt, IsActive, EmailVerified, TwoFactorEnabled, CreatedDate, CreatedBy) "
                    "VALUES (:role_id, :oid, :username, :fn, :ln, :email, :pwd, :salt, 1, 1, 0, GETUTCDATE(), :created_by)"
                ),
                {
                    "role_id": role_id,
                    "oid": int(inv["OrganizationID"]),
                    "username": username,
                    "fn": username[:50] or "Invited",
                    "ln": "User",
                    "email": inv["Email"],
                    "pwd": pwd_hash,
                    "salt": salt,
                    "created_by": created_by,
                },
            )
        else:
            # Update existing user: set org and role; set password; mark verified & active
            conn.execute(
                text(
                    "UPDATE [User] SET OrganizationID=:oid, RoleID=:rid, PasswordHash=:pwd, PasswordSalt=:salt, EmailVerified=1, IsActive=1 WHERE Email=:email"
                ),
                {
                    "oid": int(inv["OrganizationID"]),
                    "rid": role_id,
                    "pwd": pwd_hash,
                    "salt": salt,
                    "email": inv["Email"],
                },
            )
        # Consume invitation
        conn.execute(
            text("UPDATE Invitation SET ConsumedAt = GETUTCDATE() WHERE InvitationID = :id"),
            {"id": int(inv["InvitationID"])},
        )

    write_auth_event(
        engine,
        event_type="invite_accept",
        status="success",
        email=inv["Email"],
        org_id=int(inv["OrganizationID"]),
        request=request,
    )

    return {"status": "accepted"}
