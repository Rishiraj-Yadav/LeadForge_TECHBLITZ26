"""Lead CRUD and conversation query endpoints."""

from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId

from app.models.lead import Lead
from app.models.conversation import Conversation
from app.schemas.lead import LeadCreate, LeadResponse, LeadSummary, LeadUpdate
from app.schemas.conversation import ConversationResponse

router = APIRouter()


@router.get("/", response_model=list[LeadSummary])
async def list_leads():
    leads = await Lead.find_all().sort(-Lead.created_at).to_list()
    return leads


@router.post("/", response_model=LeadResponse)
async def create_lead(payload: LeadCreate):
    lead = Lead(**payload.model_dump())
    await lead.insert()
    return lead


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str):
    lead = await Lead.get(PydanticObjectId(lead_id))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: str, payload: LeadUpdate):
    lead = await Lead.get(PydanticObjectId(lead_id))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)

    await lead.save()
    return lead


@router.get("/{lead_id}/conversations", response_model=list[ConversationResponse])
async def get_lead_conversations(lead_id: str):
    conversations = await Conversation.find(
        Conversation.lead_id == PydanticObjectId(lead_id)
    ).sort(-Conversation.created_at).to_list()
    return conversations
