from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import text

from ..core.db import engine
from ..core.settings import settings
from ..utils.security import decode_jwt_token


router = APIRouter(prefix="/canvas", tags=["canvas"])


def _auth_dependency(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    payload = decode_jwt_token(token, settings.jwt_secret)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


@router.post("/forms/{form_id}/layouts")
def create_layout(
    form_id: int,
    payload: dict,
    claims: dict = Depends(_auth_dependency),
):
    # Ensure form belongs to user's org via event
    with engine.begin() as conn:

        row = conn.execute(
            text(
                "SELECT TOP 1 f.FormID FROM Form f JOIN Event e ON e.EventID = f.EventID "
                "WHERE f.FormID = :fid AND e.OrganizationID = :org AND "
                "(f.IsDeleted = 0 OR f.IsDeleted IS NULL)"
            ),
            {"fid": form_id, "org": claims.get("org_id")},
        ).first()
        if not row:
            raise HTTPException(status_code=404, detail="Form not found")
        conn.execute(
            text(
                "INSERT INTO CanvasLayout (FormID, DeviceType, AspectRatio, "
                "ResolutionX, ResolutionY, RevisionNumber, IsDeleted) "
                "VALUES (:fid, :dt, :ar, :rx, :ry, 1, 0)"
            ),
            {
                "fid": form_id,
                "dt": payload.get("device_type"),
                "ar": payload.get("aspect_ratio"),
                "rx": payload.get("resolution_x"),
                "ry": payload.get("resolution_y"),
            },
        )
        new_id = conn.execute(text("SELECT SCOPE_IDENTITY() as id")).first()
    return {"id": int(new_id[0]) if new_id and new_id[0] else None}

