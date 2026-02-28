import logging
from clients.aturiya import AturiyaClient
from models.lead import RawLead

logger = logging.getLogger(__name__)


def fetch_leads(campaign_id: str | None = None) -> list[RawLead]:
    """Stage 1: Ingest leads from Aturiya API.

    If no campaign_id is provided, picks the first available campaign.
    """
    client = AturiyaClient()

    # Verify auth
    user_info = client.verify_auth()
    logger.info("Authenticated as %s (%s)", user_info.get("full_name"), user_info.get("email"))

    # Get campaign
    if not campaign_id:
        campaigns = client.list_campaigns()
        if not campaigns:
            raise RuntimeError("No campaigns found. Create a campaign in Aturiya first.")
        campaign_id = campaigns[0]["id"]
        logger.info("Using campaign: %s (%s)", campaigns[0].get("name"), campaign_id)

    # Fetch all leads
    leads = client.get_all_leads(campaign_id)
    logger.info("Ingested %d raw leads from campaign %s", len(leads), campaign_id)

    return leads
