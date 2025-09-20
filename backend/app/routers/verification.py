from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/verify", tags=["verify"]) 


class EmailSubmitRequest(BaseModel):
    token: str
    from_domain: str
    dkim_pass: bool
    spf_pass: bool
    dmarc_aligned: bool


@router.post("/email-submit")
async def verify_email_submit(payload: EmailSubmitRequest):
    # Stub: accept payload and return a status; real implementation integrates DMARC checks and updates domain_claim
    status = "verified" if payload.dmarc_aligned and payload.dkim_pass and payload.spf_pass else "pending"
    return {"status": status}
