"""Rep notification control endpoints."""

from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId

from app.services.lead_workflow import apply_rep_decision, pipeline_counts

router = APIRouter()


@router.post("/approve/{lead_id}")
async def approve_lead(lead_id: str):
    lead, sent = await apply_rep_decision(PydanticObjectId(lead_id), "approved")
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {
        "lead_id": str(lead.id),
        "decision": "approved",
        "stage": str(lead.stage.value),
        "sent": sent,
    }


@router.post("/reject/{lead_id}")
async def reject_lead(lead_id: str):
    lead, sent = await apply_rep_decision(PydanticObjectId(lead_id), "rejected")
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {
        "lead_id": str(lead.id),
        "decision": "rejected",
        "stage": str(lead.stage.value),
        "sent": sent,
    }


@router.get("/pipeline-summary")
async def pipeline_summary():
    return await pipeline_counts()
