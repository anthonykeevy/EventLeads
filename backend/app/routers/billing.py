from fastapi import APIRouter, Request

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/webhooks/stripe")
async def stripe_webhook_stub(request: Request):
    _ = await request.body()
    return {"received": True}

