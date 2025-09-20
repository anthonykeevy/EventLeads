from fastapi import APIRouter, Path, Header, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..utils.security import decode_jwt_token
from ..core.settings import settings

router = APIRouter(prefix="/admin", tags=["admin"]) 


class ModelAssignmentRequest(BaseModel):
    model_id: str
    plan_id: str
    effective_at: str
    overrides: dict | None = None


def _get_claims(authorization: Optional[str]) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    payload = decode_jwt_token(token, settings.jwt_secret)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


@router.post("/orgs/{org_id}/model-assignment")
async def assign_model_plan(org_id: str = Path(...), payload: ModelAssignmentRequest | None = None, authorization: Optional[str] = Header(None)):
    claims = _get_claims(authorization)
    role = claims.get("role")
    if role != "SystemAdmin":
        raise HTTPException(status_code=403, detail="SystemAdmin required")
    # Stub: would validate roles and persist org_business_model + entitlements overrides
    return {"org_id": org_id, "model_id": payload.model_id, "plan_id": payload.plan_id, "effective_at": payload.effective_at}
