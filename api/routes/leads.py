from fastapi import APIRouter, Depends
from clients.aturiya import AturiyaClient
from clients.pipe0 import Pipe0Client
from models.lead import RawLead
from api.deps import get_aturiya_client, get_pipe0_client
from pipeline.enrich import enrich_one

router = APIRouter()


@router.get("/api/campaigns/{campaign_id}/leads")
def get_leads(
    campaign_id: str,
    client: AturiyaClient = Depends(get_aturiya_client),
):
    leads = client.get_all_leads(campaign_id)
    return [lead.model_dump() for lead in leads]


@router.post("/api/leads/{lead_id}/enrich")
def enrich_lead(
    lead_id: str,
    raw: RawLead,
    pipe0: Pipe0Client = Depends(get_pipe0_client),
):
    enriched = enrich_one(raw, client=pipe0)
    return enriched.model_dump()
