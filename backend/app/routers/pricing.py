from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict

router = APIRouter(prefix="/pricing", tags=["pricing"]) 


class PricingEstimateRequest(BaseModel):
    org_id: str
    project_id: str
    leads: int
    skus: Dict[str, float]


@router.post("/estimate")
async def create_pricing_estimate(payload: PricingEstimateRequest):
    # Stub: compute a trivial estimate structure
    base = 0.0
    lines = []
    total = 0.0
    for sku, qty in payload.skus.items():
        line_total = float(qty)  # placeholder
        lines.append({"sku": sku, "included": 0, "overage": line_total, "total": line_total})
        total += line_total
    return {"base": base, "lines": lines, "grand_total": total}
