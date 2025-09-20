from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy import text

from ..core.db import engine
from ..utils.security import decode_jwt_token
from ..core.settings import settings

router = APIRouter(prefix="/audit", tags=["audit"]) 


def get_claims(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    payload = decode_jwt_token(token, settings.jwt_secret)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


@router.get("/auth")
def list_auth_events(
    email: Optional[str] = Query(None),
    event: Optional[str] = Query(None, alias="event_type"),
    status: Optional[str] = Query(None),
    reason: Optional[str] = Query(None, alias="reason_code"),
    user_id: Optional[int] = Query(None),
    org_id: Optional[int] = Query(None),
    from_: Optional[datetime] = Query(None, alias="from"),
    to: Optional[datetime] = Query(None),
    page: int = 1,
    page_size: int = 50,
    claims: dict = Depends(get_claims),
):
    role = claims.get("role")
    if role not in ("Admin", "SystemAdmin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    offset = max(page - 1, 0) * page_size
    filters = ["1=1"]
    params = {}
    if email:
        filters.append("Email = :email")
        params["email"] = email
    if event:
        filters.append("EventType = :event")
        params["event"] = event
    if status:
        filters.append("Status = :status")
        params["status"] = status
    if reason:
        filters.append("ReasonCode = :reason")
        params["reason"] = reason
    if user_id:
        filters.append("UserID = :user_id")
        params["user_id"] = user_id
    # Org scoping: Admin limited to their org_id; SystemAdmin can override via query
    effective_org = org_id if (role == "SystemAdmin" and org_id) else claims.get("org_id")
    if effective_org:
        filters.append("OrganizationID = :org")
        params["org"] = effective_org
    if from_:
        filters.append("CreatedDate >= :from")
        params["from"] = from_
    if to:
        filters.append("CreatedDate <= :to")
        params["to"] = to

    where = " AND ".join(filters)
    with engine.begin() as conn:
        total = conn.execute(text(f"SELECT COUNT(1) FROM AuthEvent WHERE {where}"), params).scalar() or 0
        rows = conn.execute(
            text(
                f"SELECT TOP (:page_size) * FROM (SELECT ROW_NUMBER() OVER (ORDER BY CreatedDate DESC) AS rn, * FROM AuthEvent WHERE {where}) q WHERE rn > :offset ORDER BY rn"
            ),
            {**params, "page_size": page_size, "offset": offset},
        ).mappings().all()
    items = [dict(r) for r in rows]
    return {"items": items, "page": page, "page_size": page_size, "total": int(total)}


@router.get("/provider-errors")
def list_provider_errors(
    provider: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    org_id: Optional[int] = Query(None),
    from_: Optional[datetime] = Query(None, alias="from"),
    to: Optional[datetime] = Query(None),
    page: int = 1,
    page_size: int = 50,
    claims: dict = Depends(get_claims),
):
    role = claims.get("role")
    if role not in ("Admin", "SystemAdmin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    # Stub: replace with real provider error table
    return {"items": [], "page": page, "page_size": page_size, "total": 0}


@router.get("/dlq")
def list_dead_letter_queue(
    queue: Optional[str] = Query(None),
    org_id: Optional[int] = Query(None),
    from_: Optional[datetime] = Query(None, alias="from"),
    to: Optional[datetime] = Query(None),
    page: int = 1,
    page_size: int = 50,
    claims: dict = Depends(get_claims),
):
    role = claims.get("role")
    if role not in ("Admin", "SystemAdmin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    # Stub: replace with real DLQ table
    return {"items": [], "page": page, "page_size": page_size, "total": 0}
