from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any

router = APIRouter(prefix="/metering", tags=["metering"]) 


class MeteringEvent(BaseModel):
    request_id: str
    sku: str
    quantity: float
    org_id: str
    project_id: str
    time: str


@router.post("/events", status_code=202)
async def create_events(events: List[MeteringEvent]):
    if not events:
        raise HTTPException(status_code=400, detail="No events provided")
    # Stub: enqueue events and enforce idempotency on request_id (to be implemented)
    return {"accepted": len(events)}
