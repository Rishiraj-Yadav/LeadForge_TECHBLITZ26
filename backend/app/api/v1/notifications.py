"""Rep notification control endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/approve/{lead_id}")
async def approve_lead(lead_id: str):
    return {"lead_id": lead_id, "decision": "approved"}


@router.post("/reject/{lead_id}")
async def reject_lead(lead_id: str):
    return {"lead_id": lead_id, "decision": "rejected"}


@router.get("/pipeline-summary")
async def pipeline_summary():
    return {
        "new": 0,
        "contacted": 0,
        "qualified": 0,
        "proposal": 0,
        "won": 0,
        "lost": 0,
    }
