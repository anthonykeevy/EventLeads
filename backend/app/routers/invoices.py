from fastapi import APIRouter

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("")
def list_invoices_stub():
    return []

