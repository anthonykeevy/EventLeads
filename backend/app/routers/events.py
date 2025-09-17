from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import text

from ..core.db import engine
from ..core.settings import settings
from ..utils.security import decode_jwt_token


router = APIRouter(prefix="/events", tags=["events"])


def _auth_dependency(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    payload = decode_jwt_token(token, settings.jwt_secret)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


@router.get("")
def list_events(claims: dict = Depends(_auth_dependency)):
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                "SELECT EventID as id, Name as name, Status as status, "
                "Timezone as timezone, CreatedDate as created_date "
                "FROM [Event] WHERE OrganizationID = :org AND "
                "(IsDeleted = 0 OR IsDeleted IS NULL) "
                "ORDER BY CreatedDate DESC"
            ),
            {"org": org_id},
        ).mappings().all()
    return rows


@router.post("")
def create_event(payload: dict, claims: dict = Depends(_auth_dependency)):
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO [Event] (OrganizationID, Name, Status, Timezone, CreatedDate, IsDeleted) "
                "VALUES (:org, :name, :status, :tz, :cd, 0)"
            ),
            {
                "org": org_id,
                "name": payload.get("name"),
                "status": payload.get("status", "Draft"),
                "tz": payload.get("timezone", "UTC"),
                "cd": datetime.utcnow(),
            },
        )
        row = conn.execute(text("SELECT SCOPE_IDENTITY() as id")).first()
        new_id = int(row[0]) if row and row[0] else None
    if not new_id:
        raise HTTPException(status_code=500, detail="Failed to create event")
    return {"id": new_id}


@router.get("/{event_id}")
def get_event(event_id: int, claims: dict = Depends(_auth_dependency)):
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        row = conn.execute(
            text(
                "SELECT TOP 1 EventID as id, Name as name, Status as status, "
                "Timezone as timezone, CreatedDate as created_date "
                "FROM [Event] WHERE EventID = :id "
                "AND OrganizationID = :org"
            ),
            {"id": event_id, "org": org_id},
        ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return row


@router.put("/{event_id}")
def update_event(
    event_id: int, payload: dict, claims: dict = Depends(_auth_dependency)
):
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE [Event] SET Name = :name, Status = :status, Timezone = :tz, "
                "LastUpdated = GETUTCDATE() WHERE EventID = :id AND OrganizationID = :org"
            ),
            {
                "id": event_id,
                "org": org_id,
                "name": payload.get("name"),
                "status": payload.get("status", "Draft"),
                "tz": payload.get("timezone", "UTC"),
            },
        )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "ok"}

@router.delete("/{event_id}")
def soft_delete_event(
    event_id: int, claims: dict = Depends(_auth_dependency)
):
    if claims.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admin required")
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE [Event] SET IsDeleted = 1, DeletedAt = GETUTCDATE(), "
                "DeletedBy = :by WHERE EventID = :id AND OrganizationID = :org"
            ),
            {"id": event_id, "org": org_id, "by": f"user:{claims.get('sub')}"},
        )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "deleted"}


@router.post("/{event_id}/restore")
def restore_event(
    event_id: int, claims: dict = Depends(_auth_dependency)
):
    if claims.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admin required")
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE [Event] SET IsDeleted = 0, DeletedAt = NULL, "
                "DeletedBy = NULL WHERE EventID = :id AND OrganizationID = :org"
            ),
            {"id": event_id, "org": org_id},
        )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "restored"}

