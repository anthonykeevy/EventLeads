from fastapi import APIRouter

router = APIRouter(prefix="/canvas", tags=["canvas"])


@router.get("/{event_id}")
def get_canvas_stub(event_id: int):
    return {"event_id": event_id, "objects": []}

