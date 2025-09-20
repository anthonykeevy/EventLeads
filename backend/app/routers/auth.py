# NOTE FOR DEVS:
# The database schema for this project uses PascalCase for all table and column names
# (e.g., `TableName`, `ColumnName`). However, the SQLAlchemy models and Python code
# often use snake_case. When writing raw SQL queries, you MUST use the correct
# PascalCase names for columns to avoid errors.
from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import text

from ..core.db import engine
from ..core.settings import settings
from ..utils.security import (
    create_jwt_token,
    hash_password,
    verify_password,
    decode_jwt_token,
)
from ..services.emailer import send_email
from ..schemas.auth import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    ResendRequest,
    ResetRequest,
    ResetConfirmRequest,
    MeResponse,
)


router = APIRouter(prefix="/auth", tags=["auth"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


def write_auth_event(
    engine,
    *,
    event_type: str,
    status: str,
    email: Optional[str] = None,
    org_id: Optional[int] = None,
    user_id: Optional[int] = None,
    reason: Optional[str] = None,
    request: Optional[Request] = None,
):
    try:
        with engine.begin() as conn:
            req_id = request.headers.get("X-Request-ID") if request else None
            ip = request.client.host if request and request.client else None
            ua = request.headers.get("User-Agent") if request else None
            conn.execute(
                text(
                    "INSERT INTO AuthEvent (OrganizationID, UserID, Email, "
                    "EventType, Status, ReasonCode, RequestID, IP, UserAgent) "
                    "VALUES (:org_id, :user_id, :email, :event_type, :status, "
                    ":reason, :req_id, :ip, :ua)"
                ),
                {
                    "org_id": org_id,
                    "user_id": user_id,
                    "email": email,
                    "event_type": event_type,
                    "status": status,
                    "reason": reason,
                    "req_id": req_id,
                    "ip": ip,
                    "ua": ua,
                },
            )
    except Exception:
        pass


def get_user_by_email(email: str):
    with engine.begin() as conn:
        row = conn.execute(
            text(
                "SELECT TOP 1 * FROM [User] WHERE Email = :email "
                "ORDER BY UserID DESC"
            ),
            {"email": email},
        ).mappings().first()
        return row


def get_role_id(role_name: str) -> Optional[int]:
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT TOP 1 RoleID FROM Role WHERE RoleName = :n"),
            {"n": role_name},
        ).first()
        return int(row[0]) if row else None


def get_default_org_id() -> Optional[int]:
    with engine.begin() as conn:
        row = conn.execute(
            text(
                "SELECT TOP 1 OrganizationID FROM Organization "
                "ORDER BY OrganizationID"
            )
        ).first()
        return int(row[0]) if row else None


def _user_has_org_column(conn) -> bool:
    exists = conn.execute(
        text(
            "SELECT COUNT(1) FROM sys.columns "
            "WHERE Name = 'OrganizationID' AND Object_ID = Object_ID('[User]')"
        )
    ).scalar()
    try:
        return bool(int(exists or 0))
    except Exception:
        return False


def ensure_user_organization(user_id: int, email: str) -> Optional[int]:
    """Ensure the user has an OrganizationID. Create a default org if missing.
    Returns the org id if linked, otherwise None when column is not present.
    """
    local_name = email.split("@")[0] if email and "@" in email else "Org"
    with engine.begin() as conn:
        if not _user_has_org_column(conn):
            return None
        row = conn.execute(
            text("SELECT OrganizationID FROM [User] WHERE UserID = :uid"),
            {"uid": user_id},
        ).first()
        current = int(row[0]) if row and row[0] is not None else None
        if current:
            return current
        conn.execute(
            text(
                "INSERT INTO Organization (Name, CreatedDate) "
                "VALUES (:name, GETDATE())"
            ),
            {"name": f"{local_name}'s Organization"},
        )
        org_row = conn.execute(text("SELECT SCOPE_IDENTITY()"))
        new_org_id = int(list(org_row.fetchone() or [0])[0])
        conn.execute(
            text("UPDATE [User] SET OrganizationID = :org WHERE UserID = :uid"),
            {"org": new_org_id, "uid": user_id},
        )
        return new_org_id


@router.post("/signup", response_model=dict)
def signup(payload: SignupRequest, request: Request):
    write_auth_event(
        engine,
        event_type="signup_attempt",
        status="attempt",
        email=payload.email,
        request=request,
    )
    existing = get_user_by_email(payload.email)
    if existing and (existing.get("EmailVerified") and existing.get("EmailVerified") != 0):
        write_auth_event(
            engine,
            event_type="signup_failure",
            status="failure",
            email=payload.email,
            reason="already_verified",
            request=request,
        )
        raise HTTPException(status_code=400, detail="Account already exists")
    role_id = get_role_id("User")
    # using bcrypt for new passwords; salt kept for legacy compatibility
    salt = ""
    pwd_hash = hash_password(salt, payload.password)
    # Derive username if needed (not used yet; kept for future)
    # username = payload.email.split("@")[0]
    with engine.begin() as conn:
        # Get the "Default Organization" ID
        default_org = conn.execute(
            text("SELECT TOP 1 OrganizationID FROM Organization WHERE OrganizationCode = 'DEFAULT'")
        ).first()
        
        if not default_org:
            raise HTTPException(status_code=500, detail="Default organization not found")
        
        org_id = default_org[0]

        if existing is None:
            conn.execute(
                text(
                    "INSERT INTO [User] (RoleID, OrganizationID, Email, Username, FirstName, LastName, CreatedBy, PasswordHash, PasswordSalt, EmailVerified, CreatedDate) "
                    "VALUES (:RoleID, :OrganizationID, :Email, :Username, 'New', 'User', :CreatedBy, :PasswordHash, :PasswordSalt, 0, GETUTCDATE())"
                ),
                {
                    "RoleID": role_id,
                    "OrganizationID": org_id,
                    "Email": payload.email,
                    "Username": payload.email,
                    "CreatedBy": payload.email,
                    "PasswordHash": pwd_hash,
                    "PasswordSalt": salt,
                },
            )
        else:
            # Existing unverified user, update password and link to org
            conn.execute(
                text(
                    "UPDATE [User] SET OrganizationID = :org_id, PasswordHash = :pwd_hash, PasswordSalt = :salt WHERE Email = :email"
                ),
                {
                    "org_id": org_id,
                    "pwd_hash": pwd_hash,
                    "salt": salt,
                    "email": payload.email
                }
            )
    token = secrets.token_urlsafe(32)
    expires = _now() + timedelta(minutes=60)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO emailverificationtoken (UserID, Token, "
                "ExpiresAt, ConsumedAt, CreatedAt) SELECT TOP 1 UserID, "
                ":token, :exp, NULL, GETDATE() FROM [User] WHERE "
                "Email = :email ORDER BY UserID DESC"
            ),
            {"token": token, "exp": expires, "email": payload.email},
        )
    verify_url = f"http://localhost:3000/verify?token={token}"
    send_email(
        to=payload.email,
        subject="Verify your account",
        body=f"Click to verify your account: {verify_url}",
    )
    write_auth_event(
        engine,
        event_type="signup_success",
        status="success",
        email=payload.email,
        request=request,
    )
    return {"status": "verification_required"}


@router.get("/verify", response_class=RedirectResponse)
def verify(token: str, request: Request):
    write_auth_event(
        engine,
        event_type="verification_attempt",
        status="attempt",
        request=request,
    )
    with engine.begin() as conn:
        row = conn.execute(
            text(
                "SELECT TOP 1 evt.UserID, evt.ExpiresAt, evt.ConsumedAt, "
                "u.Email FROM emailverificationtoken evt JOIN [User] u ON "
                "u.UserID = evt.UserID WHERE evt.Token = :token "
                "ORDER BY evt.ID DESC"
            ),
            {"token": token},
        ).mappings().first()
        if not row:
            write_auth_event(
                engine,
                event_type="verification_failure",
                status="failure",
                reason="invalid",
                request=request,
            )
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=Invalid verification link.")

        if row["ConsumedAt"] is not None:
            time_since_consumed = datetime.now(timezone.utc).replace(tzinfo=None) - row["ConsumedAt"]
            if time_since_consumed < timedelta(seconds=2):
                # Harmless double-click, redirect to login as if successful
                return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?verified=true")
            else:
                # Attempt to reuse a token
                return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=This verification link has already been used. Please try logging in.")

        if row["ExpiresAt"] and row["ExpiresAt"] < _now().replace(tzinfo=None):
            write_auth_event(
                engine,
                event_type="verification_failure",
                status="failure",
                reason="expired",
                email=row["Email"],
                user_id=row["UserID"],
                request=request,
            )
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=This verification link has expired. Please request a new one.")

        conn.execute(
            text("UPDATE [User] SET EmailVerified = 1 WHERE UserID = :uid"),
            {"uid": row["UserID"]},
        )
        conn.execute(
            text(
                "UPDATE emailverificationtoken SET ConsumedAt = GETDATE() "
                "WHERE Token = :tkn"
            ),
            {"tkn": token},
        )
    write_auth_event(
        engine,
        event_type="verification_success",
        status="success",
        user_id=row["UserID"],
        email=row["Email"],
        request=request,
    )
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?verified=true")


@router.post("/resend", response_model=dict)
def resend(payload: ResendRequest, request: Request):
    write_auth_event(
        engine,
        event_type="resend_attempt",
        status="attempt",
        email=payload.email,
        request=request,
    )
    with engine.begin() as conn:
        user = conn.execute(
            text("SELECT TOP 1 * FROM [User] WHERE Email = :email"),
            {"email": payload.email},
        ).mappings().first()
        if not user or (user.get("EmailVerified") and user.get("EmailVerified") != 0):
            write_auth_event(
                engine,
                event_type="resend_success",
                status="success",
                email=payload.email,
                request=request,
            )
            return {"status": "sent"}
        recent = conn.execute(
            text(
                "SELECT TOP 1 CreatedAt FROM EmailVerificationToken "
                "WHERE UserID = :uid ORDER BY CreatedAt DESC"
            ),
            {"uid": user["UserID"]},
        ).first()
    if recent and recent[0] and (_now() - recent[0]).total_seconds() < 60:
        write_auth_event(
            engine,
            event_type="resend_limited",
            status="failure",
            reason="cooldown",
            email=payload.email,
            user_id=user["UserID"],
            request=request,
        )
        raise HTTPException(
            status_code=429, detail="Please wait before resending"
        )
    # Enforce daily max (5)
    with engine.begin() as conn:
        count_today = conn.execute(
            text(
                "SELECT COUNT(1) FROM EmailVerificationToken WHERE "
                "UserID = :uid AND CreatedAt > DATEADD(day, -1, GETUTCDATE())"
            ),
            {"uid": user["UserID"]},
        ).scalar()
        if count_today and int(count_today) >= 5:
            write_auth_event(
                engine,
                event_type="resend_limited",
                status="failure",
                reason="daily_limit",
                email=payload.email,
                user_id=user["UserID"],
                request=request,
            )
            raise HTTPException(
                status_code=429, detail="Daily resend limit reached"
            )
    token = secrets.token_urlsafe(32)
    expires = _now() + timedelta(minutes=60)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO EmailVerificationToken (UserID, Token, "
                "ExpiresAt, ConsumedAt, CreatedAt) VALUES "
                "(:uid, :token, :exp, NULL, GETUTCDATE())"
            ),
            {"uid": user["UserID"], "token": token, "exp": expires},
        )
    verify_url = f"/verify?token={token}"
    send_email(
        to=payload.email,
        subject="Verify your account",
        body=f"Click to verify: {verify_url}",
    )
    write_auth_event(
        engine,
        event_type="resend_success",
        status="success",
        email=payload.email,
        user_id=user["UserID"],
        request=request,
    )
    return {"status": "sent"}


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request):
    write_auth_event(
        engine,
        event_type="login_attempt",
        status="attempt",
        email=payload.email,
        request=request,
    )
    user = get_user_by_email(payload.email)
    if not user:
        write_auth_event(
            engine,
            event_type="login_failure",
            status="failure",
            email=payload.email,
            reason="invalid_credentials",
            request=request,
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.get("EmailVerified") or user.get("EmailVerified") == 0:
        write_auth_event(
            engine,
            event_type="login_failure",
            status="failure",
            email=payload.email,
            user_id=user["UserID"],
            reason="unverified",
            request=request,
        )
        raise HTTPException(status_code=403, detail="Email not verified")
    if not verify_password(
        user.get("PasswordSalt"), user.get("PasswordHash"), payload.password
    ):
        write_auth_event(
            engine,
            event_type="login_failure",
            status="failure",
            email=payload.email,
            user_id=user["UserID"],
            reason="invalid_credentials",
            request=request,
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Ensure org exists and is linked when the column exists
    org_id = user.get("OrganizationID")
    if not org_id:
        try:
            org_id = ensure_user_organization(int(user["UserID"]), payload.email)
        except Exception:
            org_id = None
    # docs/shards: 04-auth-rbac.md — org scoping; 02-data-schema.md — Organization
    # Fallback: if user column missing or linking failed, ensure a default org exists
    if not org_id:
        try:
            oid = get_default_org_id()
            if not oid:
                with engine.begin() as conn:
                    conn.execute(
                        text(
                            "INSERT INTO Organization (Name, CreatedDate) VALUES (:n, GETDATE())"
                        ),
                        {"n": "Default Organization"},
                    )
                oid = get_default_org_id()
            org_id = oid
        except Exception:
            org_id = None
    # Get role name from database
    role_name = "User"
    with engine.begin() as conn:
        role_row = conn.execute(
            text("SELECT RoleName FROM Role WHERE RoleID = :role_id"),
            {"role_id": user.get("RoleID")}
        ).first()
        if role_row:
            role_name = role_row[0]

    claims = {
        "sub": str(user["UserID"]),
        "org_id": org_id,
        "role": role_name,
        "exp": int((_now() + timedelta(hours=8)).timestamp()),
    }
    token = create_jwt_token(claims, settings.jwt_secret)
    write_auth_event(
        engine,
        event_type="login_success",
        status="success",
        email=payload.email,
        user_id=user["UserID"],
        request=request,
    )
    return LoginResponse(access_token=token)


def auth_dependency(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    payload = decode_jwt_token(token, settings.jwt_secret)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


@router.get("/me", response_model=MeResponse)
def me(claims: dict = Depends(auth_dependency)):
    needs_onboarding = False
    org_id = claims.get("org_id")
    if org_id:
        with engine.begin() as conn:
            org_code = conn.execute(
                text("SELECT OrganizationCode FROM Organization WHERE OrganizationID = :org_id"),
                {"org_id": org_id}
            ).scalar()
            if org_code == 'DEFAULT':
                needs_onboarding = True

    return MeResponse(
        user_id=int(claims.get("sub")),
        org_id=org_id,
        role=claims.get("role"),
        verified=True,
        needs_onboarding=needs_onboarding,
    )


@router.post("/reset/request", response_model=dict)
def reset_request(payload: ResetRequest, request: Request):
    write_auth_event(
        engine,
        event_type="reset_request_attempt",
        status="attempt",
        email=payload.email,
        request=request,
    )
    user = get_user_by_email(payload.email)
    if user:
        # Check for recent reset requests (5 minute cooldown)
        with engine.begin() as conn:
            recent = conn.execute(
                text(
                    "SELECT TOP 1 CreatedAt FROM passwordresettoken "
                    "WHERE UserID = :uid ORDER BY CreatedAt DESC"
                ),
                {"uid": user["UserID"]},
            ).first()
        if recent and recent[0] and (_now().replace(tzinfo=None) - recent[0]).total_seconds() < 300:  # 5 minutes
            write_auth_event(
                engine,
                event_type="reset_request_limited",
                status="failure",
                reason="cooldown",
                email=payload.email,
                user_id=user["UserID"],
                request=request,
            )
            raise HTTPException(
                status_code=429, detail="Please wait 5 minutes before requesting another reset"
            )

        # Check daily limit (3 resets per day)
        with engine.begin() as conn:
            count_today = conn.execute(
                text(
                    "SELECT COUNT(1) FROM passwordresettoken WHERE "
                    "UserID = :uid AND CreatedAt > DATEADD(day, -1, GETDATE())"
                ),
                {"uid": user["UserID"]},
            ).scalar()
        if count_today and int(count_today) >= 3:
            write_auth_event(
                engine,
                event_type="reset_request_limited",
                status="failure",
                reason="daily_limit",
                email=payload.email,
                user_id=user["UserID"],
                request=request,
            )
            raise HTTPException(
                status_code=429, detail="We have already sent 3 password reset emails. If you are not receiving the emails, you are not registered on the platform with this email address."
            )
        token = secrets.token_urlsafe(32)
        expires = _now().replace(tzinfo=None) + timedelta(minutes=60)
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO passwordresettoken (UserID, Token, "
                    "ExpiresAt, ConsumedAt, CreatedAt) VALUES "
                    "(:uid, :token, :exp, NULL, GETDATE())"
                ),
                {"uid": user["UserID"], "token": token, "exp": expires},
            )
        reset_url = f"http://localhost:3000/reset/confirm?token={token}"
        send_email(
            to=payload.email,
            subject="Reset your password",
            body=f"Click to reset your password: {reset_url}",
        )
    write_auth_event(
        engine,
        event_type="reset_request_success",
        status="success",
        email=payload.email,
        user_id=(user or {}).get("UserID"),
        request=request,
    )
    return {"status": "sent"}


@router.post("/reset/confirm", response_model=dict)
def reset_confirm(payload: ResetConfirmRequest, request: Request):
    write_auth_event(
        engine,
        event_type="reset_confirm_attempt",
        status="attempt",
        request=request,
    )
    with engine.begin() as conn:
        row = conn.execute(
            text(
                "SELECT TOP 1 prt.UserID, prt.ExpiresAt, prt.ConsumedAt, "
                "u.Email FROM passwordresettoken prt JOIN [User] u ON "
                "u.UserID = prt.UserID WHERE prt.Token = :token "
                "ORDER BY prt.ID DESC"
            ),
            {"token": payload.token},
        ).mappings().first()
        if not row:
            write_auth_event(
                engine,
                event_type="reset_confirm_failure",
                status="failure",
                reason="invalid",
                request=request,
            )
            raise HTTPException(status_code=400, detail="Invalid token")
        if row["ConsumedAt"] is not None or (
            row["ExpiresAt"] and row["ExpiresAt"] < _now().replace(tzinfo=None)
        ):
            write_auth_event(
                engine,
                event_type="reset_confirm_failure",
                status="failure",
                reason="expired",
                email=row["Email"],
                user_id=row["UserID"],
                request=request,
            )
            raise HTTPException(status_code=400, detail="Token expired")
        salt = ""
        pwd_hash = hash_password(salt, payload.new_password)
        conn.execute(
            text(
                "UPDATE [User] SET PasswordHash = :h, PasswordSalt = :s "
                "WHERE UserID = :uid"
            ),
            {"h": pwd_hash, "s": salt, "uid": row["UserID"]},
        )
        conn.execute(
            text(
                "UPDATE passwordresettoken SET ConsumedAt = GETDATE() "
                "WHERE Token = :tkn"
            ),
            {"tkn": payload.token},
        )
    write_auth_event(
        engine,
        event_type="reset_confirm_success",
        status="success",
        email=row["Email"],
        user_id=row["UserID"],
        request=request,
    )
    return {"status": "updated"}


@router.post("/logout", response_model=dict)
def logout(request: Request):
    # Stateless JWT; client should discard token. Record audit only.
    write_auth_event(
        engine, event_type="logout", status="success", request=request
    )
    return {"status": "ok"}