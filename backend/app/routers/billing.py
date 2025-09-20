from fastapi import APIRouter, Request, Header, HTTPException
from typing import Optional

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/webhooks/stripe")
async def stripe_webhook_stub(request: Request):
    _ = await request.body()
    return {"received": True}


@router.post("/charges", status_code=201)
async def create_billing_charges_stub(payload: dict, idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header required")
    # Stub: check dedupe store by idempotency_key to prevent duplicates
    # Stub: would validate duplicate protection and write ledger lines
    return {"charge_id": "ch_stub", "ledger_entry_ids": []}
