from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import text

from ..core.db import engine
from ..core.settings import settings
from ..utils.security import decode_jwt_token


router = APIRouter(prefix="/events/{event_id}/forms", tags=["forms"])


def _auth_dependency(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    payload = decode_jwt_token(token, settings.jwt_secret)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


@router.get("")
def list_forms(event_id: int, claims: dict = Depends(_auth_dependency)):
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                "SELECT f.FormID as id, f.Name as name, f.Status as status, "
                "f.PublicSlug as public_slug, f.CreatedDate as created_date "
                "FROM Form f JOIN Event e ON e.EventID = f.EventID "
                "WHERE f.EventID = :eid AND e.OrganizationID = :org AND "
                "(f.IsDeleted = 0 OR f.IsDeleted IS NULL) "
                "ORDER BY f.CreatedDate DESC"
            ),
            {"eid": event_id, "org": org_id},
        ).mappings().all()
    return rows


def _slugify(name: str) -> str:
    base = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    return "-".join(filter(None, base.split("-")))[:80]


@router.post("")
def create_form(
    event_id: int, payload: dict, claims: dict = Depends(_auth_dependency)
):
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        # Validate event ownership
        evt = conn.execute(
            text(
                "SELECT TOP 1 EventID FROM [Event] WHERE EventID = :id AND "
                "OrganizationID = :org AND (IsDeleted = 0 OR IsDeleted IS NULL)"
            ),
            {"id": event_id, "org": org_id},
        ).first()
        if not evt:
            raise HTTPException(status_code=404, detail="Event not found")
        # Generate unique slug if none provided
        desired = payload.get("public_slug") or _slugify(payload.get("name", "form"))
        slug = desired
        attempt = 1
        while True:
            exists = conn.execute(
                text("SELECT 1 FROM Form WHERE PublicSlug = :s"), {"s": slug}
            ).first()
            if not exists:
                break
            attempt += 1
            suffix = f"-{attempt}"
            if len(desired) + len(suffix) > 80:
                slug = desired[: (80 - len(suffix))] + suffix
            else:
                slug = desired + suffix
        conn.execute(
            text(
                "INSERT INTO Form (EventID, Name, Status, PublicSlug, IsDeleted, CreatedDate) "
                "VALUES (:eid, :name, :status, :slug, 0, GETUTCDATE())"
            ),
            {
                "eid": event_id,
                "name": payload.get("name"),
                "status": payload.get("status", "Draft"),
                "slug": slug,
            },
        )
        row = conn.execute(text("SELECT SCOPE_IDENTITY() as id")).first()
    return {"id": int(row[0]) if row and row[0] else None}


@router.get("/{form_id}")
def get_form(event_id: int, form_id: int, claims: dict = Depends(_auth_dependency)):
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        row = conn.execute(
            text(
                "SELECT TOP 1 f.FormID as id, f.Name as name, f.Status as status, "
                "f.PublicSlug as public_slug, f.CreatedDate as created_date "
                "FROM Form f JOIN Event e ON e.EventID = f.EventID "
                "WHERE f.FormID = :fid AND f.EventID = :eid AND e.OrganizationID = :org"
            ),
            {"fid": form_id, "eid": event_id, "org": org_id},
        ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return row


@router.put("/{form_id}")
def update_form(
    event_id: int, form_id: int, payload: dict, claims: dict = Depends(_auth_dependency)
):
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE f SET f.Name = :name, f.Status = :status, "
                "f.LastUpdated = GETUTCDATE() FROM Form f JOIN Event e ON e.EventID = f.EventID "
                "WHERE f.FormID = :fid AND f.EventID = :eid AND e.OrganizationID = :org"
            ),
            {
                "fid": form_id,
                "eid": event_id,
                "org": org_id,
                "name": payload.get("name"),
                "status": payload.get("status", "Draft"),
            },
        )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "ok"}


@router.delete("/{form_id}")
def soft_delete_form(
    event_id: int, form_id: int, claims: dict = Depends(_auth_dependency)
):
    if claims.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admin required")
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE f SET f.IsDeleted = 1, f.DeletedAt = GETUTCDATE(), "
                "f.DeletedBy = :by FROM Form f JOIN Event e ON e.EventID = f.EventID "
                "WHERE f.FormID = :fid AND f.EventID = :eid AND e.OrganizationID = :org"
            ),
            {
                "fid": form_id,
                "eid": event_id,
                "org": org_id,
                "by": f"user:{claims.get('sub')}",
            },
        )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "deleted"}


@router.post("/{form_id}/restore")
def restore_form(
    event_id: int, form_id: int, claims: dict = Depends(_auth_dependency)
):
    if claims.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admin required")
    org_id = claims.get("org_id")
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE f SET f.IsDeleted = 0, f.DeletedAt = NULL, f.DeletedBy = NULL "
                "FROM Form f JOIN Event e ON e.EventID = f.EventID "
                "WHERE f.FormID = :fid AND f.EventID = :eid AND e.OrganizationID = :org"
            ),
            {"fid": form_id, "eid": event_id, "org": org_id},
        )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "restored"}


