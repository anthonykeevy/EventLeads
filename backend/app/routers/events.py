from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import text
import re

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


def _table_has_column(conn, table_name: str, column_name: str) -> bool:
    exists = conn.execute(
        text(
            "SELECT COUNT(1) FROM sys.columns "
            "WHERE Name = :col AND Object_ID = Object_ID(:tbl)"
        ),
        {"col": column_name, "tbl": table_name},
    ).scalar()
    try:
        return bool(int(exists or 0))
    except Exception:
        return False


def _slugify(value: str) -> str:
    value = (value or "event").lower().strip()
    value = re.sub(r"[^a-z0-9\-\s]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value or "event"


def _derive_org_id(conn, claims: dict) -> Optional[int]:
    # docs/shards: 04-auth-rbac.md — org scoping; 02-data-schema.md — Event schema
    org_id = claims.get("org_id")
    if org_id:
        return int(org_id)
    # Fallback: if [User].OrganizationID exists, read it
    user_id = claims.get("sub")
    if user_id and _table_has_column(conn, "[User]", "OrganizationID"):
        row = conn.execute(
            text("SELECT OrganizationID FROM [User] WHERE UserID = :uid"),
            {"uid": int(user_id)},
        ).first()
        if row and row[0] is not None:
            return int(row[0])
    # As a last resort, if a single Organization exists, use it
    try:
        row = conn.execute(text("SELECT TOP 1 OrganizationID FROM Organization ORDER BY OrganizationID"))
        first = row.first()
        if first and first[0] is not None:
            return int(first[0])
    except Exception:
        pass
    return None


@router.get("")
def list_events(claims: dict = Depends(_auth_dependency)):
    with engine.begin() as conn:
        org_id = _derive_org_id(conn, claims)
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization context missing")
        has_name = _table_has_column(conn, "[Event]", "Name")
        has_event_name = _table_has_column(conn, "[Event]", "EventName")
        has_status = _table_has_column(conn, "[Event]", "Status")
        has_event_status = _table_has_column(conn, "[Event]", "EventStatus")
        has_timezone = _table_has_column(conn, "[Event]", "Timezone")
        has_deleted = _table_has_column(conn, "[Event]", "IsDeleted")

        select_fields = ["EventID as id", "CreatedDate as created_date"]
        if has_name:
            select_fields.append("Name as name")
        if has_event_name:
            select_fields.append("EventName as name")
        if has_status:
            select_fields.append("Status as status")
        if has_event_status:
            select_fields.append("EventStatus as status")
        if has_timezone:
            select_fields.append("Timezone as timezone")

        where_clause = "OrganizationID = :org"
        if has_deleted:
            where_clause += " AND (IsDeleted = 0 OR IsDeleted IS NULL)"

        sql = f"SELECT {', '.join(select_fields)} FROM [Event] WHERE {where_clause} ORDER BY CreatedDate DESC"
        rows = conn.execute(text(sql), {"org": org_id}).mappings().all()
    return rows


@router.post("")
def create_event(payload: dict, claims: dict = Depends(_auth_dependency)):
    # docs/shards: 02-data-schema.md — Event required fields; 04-auth-rbac.md — org scoping
    now = datetime.utcnow()
    name = payload.get("name") or payload.get("event_name") or "Untitled Event"
    status = payload.get("status") or payload.get("event_status") or "Draft"
    ev_type = payload.get("type") or payload.get("event_type") or "General"
    tz = payload.get("timezone") or "UTC"
    start_iso = payload.get("start_date")
    end_iso = payload.get("end_date")
    try:
        start_dt = datetime.fromisoformat(start_iso) if start_iso else now
    except Exception:
        start_dt = now
    try:
        end_dt = datetime.fromisoformat(end_iso) if end_iso else (now + timedelta(hours=1))
    except Exception:
        end_dt = now + timedelta(hours=1)
    is_public = 1 if bool(payload.get("is_public", False)) else 0
    registration_enabled = 1 if bool(payload.get("registration_enabled", False)) else 0
    created_by = int(claims.get("sub")) if claims.get("sub") else None
    slug = payload.get("slug") or _slugify(name)

    with engine.begin() as conn:
        org_id = _derive_org_id(conn, claims)
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization context missing. Please ensure your user is linked to an organization or add one.")

        # Detect column names present in this DB
        has_name = _table_has_column(conn, "[Event]", "Name")
        has_status = _table_has_column(conn, "[Event]", "Status")
        has_timezone = _table_has_column(conn, "[Event]", "Timezone")
        has_deleted = _table_has_column(conn, "[Event]", "IsDeleted")
        has_event_name = _table_has_column(conn, "[Event]", "EventName")
        has_event_status = _table_has_column(conn, "[Event]", "EventStatus")
        has_event_type = _table_has_column(conn, "[Event]", "EventType")
        has_event_slug = _table_has_column(conn, "[Event]", "EventSlug")
        has_start = _table_has_column(conn, "[Event]", "StartDate")
        has_end = _table_has_column(conn, "[Event]", "EndDate")
        has_is_public = _table_has_column(conn, "[Event]", "IsPublic")
        has_reg_enabled = _table_has_column(conn, "[Event]", "RegistrationEnabled")
        has_created_by = _table_has_column(conn, "[Event]", "CreatedByUserID")

        columns = ["OrganizationID"]
        values = [":org"]
        params = {"org": org_id}

        # Created timestamp column can vary by database; include only if present
        created_columns_candidates = [
            "CreatedDate",
            "CreatedOn",
            "CreatedAt",
            "CreateDate",
            "DateCreated",
        ]
        created_col = None
        for col_name in created_columns_candidates:
            if _table_has_column(conn, "[Event]", col_name):
                created_col = col_name
                break
        if created_col:
            columns.append(created_col)
            values.append("GETUTCDATE()")

        if has_name:
            columns.append("Name")
            values.append(":name")
            params["name"] = name
        if has_event_name:
            columns.append("EventName")
            values.append(":event_name")
            params["event_name"] = name

        if has_status:
            columns.append("Status")
            values.append(":status")
            params["status"] = status
        if has_event_status:
            columns.append("EventStatus")
            values.append(":event_status")
            params["event_status"] = status

        if has_timezone:
            columns.append("Timezone")
            values.append(":tz")
            params["tz"] = tz

        if has_event_type:
            columns.append("EventType")
            values.append(":event_type")
            params["event_type"] = ev_type

        if has_event_slug:
            columns.append("EventSlug")
            values.append(":slug")
            params["slug"] = slug

        if has_start:
            columns.append("StartDate")
            values.append(":start_dt")
            params["start_dt"] = start_dt
        if has_end:
            columns.append("EndDate")
            values.append(":end_dt")
            params["end_dt"] = end_dt

        if has_is_public:
            columns.append("IsPublic")
            values.append(":is_public")
            params["is_public"] = is_public
        if has_reg_enabled:
            columns.append("RegistrationEnabled")
            values.append(":reg_enabled")
            params["reg_enabled"] = registration_enabled
        if has_deleted:
            columns.append("IsDeleted")
            values.append("0")
        if has_created_by and created_by:
            columns.append("CreatedByUserID")
            values.append(":created_by")
            params["created_by"] = created_by

        # Validate minimum set
        if ("Name" not in columns) and ("EventName" not in columns):
            raise HTTPException(status_code=500, detail="Event name column not found in schema.")
        if has_start and has_end and end_dt < start_dt:
            raise HTTPException(status_code=400, detail="EndDate must be after StartDate.")

        sql = f"INSERT INTO [Event] ({', '.join(columns)}) OUTPUT INSERTED.EventID VALUES ({', '.join(values)})"
        try:
            row = conn.execute(text(sql), params).first()
        except Exception as e:
            # Surface DB error for easier debugging in dev/UAT
            raise HTTPException(status_code=500, detail=f"Create failed: {str(e)}")
        new_id = int(row[0]) if row and row[0] is not None else None

    if not new_id:
        raise HTTPException(status_code=500, detail="Failed to create event")
    return {"id": new_id}


@router.get("/{event_id}")
def get_event(event_id: int, claims: dict = Depends(_auth_dependency)):
    with engine.begin() as conn:
        org_id = _derive_org_id(conn, claims)
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization context missing")
        has_name = _table_has_column(conn, "[Event]", "Name")
        has_event_name = _table_has_column(conn, "[Event]", "EventName")
        has_status = _table_has_column(conn, "[Event]", "Status")
        has_event_status = _table_has_column(conn, "[Event]", "EventStatus")
        has_timezone = _table_has_column(conn, "[Event]", "Timezone")

        select_fields = ["EventID as id", "CreatedDate as created_date"]
        if has_name:
            select_fields.append("Name as name")
        if has_event_name:
            select_fields.append("EventName as name")
        if has_status:
            select_fields.append("Status as status")
        if has_event_status:
            select_fields.append("EventStatus as status")
        if has_timezone:
            select_fields.append("Timezone as timezone")

        sql = f"SELECT TOP 1 {', '.join(select_fields)} FROM [Event] WHERE EventID = :id AND OrganizationID = :org"
        row = conn.execute(text(sql), {"id": event_id, "org": org_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return row


@router.put("/{event_id}")
def update_event(
    event_id: int, payload: dict, claims: dict = Depends(_auth_dependency)
):
    with engine.begin() as conn:
        org_id = _derive_org_id(conn, claims)
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization context missing")
        has_name = _table_has_column(conn, "[Event]", "Name")
        has_event_name = _table_has_column(conn, "[Event]", "EventName")
        has_status = _table_has_column(conn, "[Event]", "Status")
        has_event_status = _table_has_column(conn, "[Event]", "EventStatus")
        has_timezone = _table_has_column(conn, "[Event]", "Timezone")

        sets = []
        params = {"id": event_id, "org": org_id}
        if has_name and payload.get("name") is not None:
            sets.append("Name = :name")
            params["name"] = payload.get("name")
        if has_event_name and payload.get("name") is not None:
            sets.append("EventName = :event_name")
            params["event_name"] = payload.get("name")
        if has_status and payload.get("status") is not None:
            sets.append("Status = :status")
            params["status"] = payload.get("status")
        if has_event_status and payload.get("status") is not None:
            sets.append("EventStatus = :event_status")
            params["event_status"] = payload.get("status")
        if has_timezone and payload.get("timezone") is not None:
            sets.append("Timezone = :tz")
            params["tz"] = payload.get("timezone")
        if _table_has_column(conn, "[Event]", "LastUpdated"):
            sets.append("LastUpdated = GETUTCDATE()")

        if not sets:
            raise HTTPException(status_code=400, detail="No updatable fields provided")

        sql = f"UPDATE [Event] SET {', '.join(sets)} WHERE EventID = :id AND OrganizationID = :org"
        result = conn.execute(text(sql), params)
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

