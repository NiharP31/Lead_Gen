from fastapi import APIRouter, Depends
from clients.aturiya import AturiyaClient
from api.deps import get_aturiya_client

router = APIRouter()


@router.get("/api/campaigns")
def list_campaigns(client: AturiyaClient = Depends(get_aturiya_client)):
    return client.list_campaigns()
