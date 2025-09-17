from fastapi import APIRouter

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("")
def create_lead_stub():
    return {"id": 1}

