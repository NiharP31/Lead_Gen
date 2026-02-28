import logging
from models.lead import (
    RawLead,
    EnrichedLead,
    CompanyOverview,
    FundingInfo,
    EnrichmentMetadata,
)
from clients.pipe0 import Pipe0Client
import config

logger = logging.getLogger(__name__)


def _batch(items: list, size: int):
    """Yield successive chunks of `size` from `items`."""
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _merge_lead(raw: RawLead, enrichment: dict) -> EnrichedLead:
    """Merge raw Apollo data with pipe0 enrichment into an EnrichedLead."""

    # Company overview
    company_overview = None
    if any(
        k in enrichment
        for k in (
            "company_description",
            "company_industry",
            "headcount",
            "founded_year",
            "company_region",
            "estimated_revenue",
        )
    ):
        company_overview = CompanyOverview(
            description=enrichment.get("company_description"),
            industry=enrichment.get("company_industry"),
            headcount=enrichment.get("headcount"),
            founded_year=enrichment.get("founded_year"),
            region=enrichment.get("company_region"),
            estimated_revenue=enrichment.get("estimated_revenue"),
        )

    # Tech stack
    tech_stack = enrichment.get("technology_list")

    # Funding
    funding = None
    if "funding_history" in enrichment or "funding_total_usd" in enrichment:
        funding = FundingInfo(
            total_funding_usd=enrichment.get("funding_total_usd"),
            funding_history=enrichment.get("funding_history"),
            news_summary=enrichment.get("company_news_summary"),
        )

    # LinkedIn posts
    linkedin_posts = None
    post_data = enrichment.get("crustdata_post_list")
    if post_data and isinstance(post_data, list):
        # Extract post text from crustdata format
        linkedin_posts = []
        for post in post_data[:5]:  # Limit to 5 most recent
            if isinstance(post, dict):
                linkedin_posts.append(post.get("text", str(post)))
            else:
                linkedin_posts.append(str(post))
    elif enrichment.get("post_list_string"):
        linkedin_posts = [enrichment["post_list_string"]]

    # Metadata
    metadata = EnrichmentMetadata(
        signals_found=enrichment.get("_signals_found", []),
        signals_missed=enrichment.get("_signals_missed", []),
        pipe0_run_id=enrichment.get("_run_id"),
    )

    return EnrichedLead(
        lead_id=raw.lead_id,
        name=raw.name,
        email=raw.email,
        phone=raw.phone,
        organization=raw.organization,
        designation=raw.designation,
        linkedin_url=raw.linkedin_url,
        campaign_id=raw.campaign_id,
        campaign_name=raw.campaign_name,
        company_overview=company_overview,
        tech_stack=tech_stack,
        funding=funding,
        linkedin_posts=linkedin_posts,
        enrichment_metadata=metadata,
    )


def enrich_one(raw: RawLead, client: Pipe0Client | None = None) -> EnrichedLead:
    """Enrich a single lead via pipe0 and return an EnrichedLead."""
    client = client or Pipe0Client()
    index_map = {1: raw.lead_id}
    batch_dicts = [raw.model_dump()]

    try:
        response = client.enrich_sync(batch_dicts)
        enrichments = Pipe0Client.parse_enrichment(response, index_map)
    except Exception as e:
        logger.error("Enrichment failed for %s: %s", raw.name, e)
        enrichments = {}

    enrichment = enrichments.get(raw.lead_id, {})
    return _merge_lead(raw, enrichment)


def enrich_leads(raw_leads: list[RawLead]) -> list[EnrichedLead]:
    """Stage 2: Enrich leads via pipe0 in batches.

    Processes leads in batches of PIPE0_BATCH_SIZE (default 9) using
    the synchronous endpoint, with graceful fallback on errors.
    """
    client = Pipe0Client()
    enriched_leads = []
    batch_size = config.PIPE0_BATCH_SIZE
    total_batches = (len(raw_leads) + batch_size - 1) // batch_size

    for batch_num, batch in enumerate(_batch(raw_leads, batch_size), start=1):
        logger.info("Enriching batch %d/%d (%d leads)", batch_num, total_batches, len(batch))

        # Build index map: pipe0 1-based id -> lead_id
        index_map = {i + 1: lead.lead_id for i, lead in enumerate(batch)}

        # Convert to dicts for pipe0 input
        batch_dicts = [lead.model_dump() for lead in batch]

        try:
            response = client.enrich_sync(batch_dicts)
            enrichments = Pipe0Client.parse_enrichment(response, index_map)
        except Exception as e:
            logger.error("Batch %d failed: %s. Returning leads without enrichment.", batch_num, e)
            enrichments = {}

        # Merge each lead
        for lead in batch:
            enrichment = enrichments.get(lead.lead_id, {})
            enriched = _merge_lead(lead, enrichment)
            enriched_leads.append(enriched)

            found = len(enrichment.get("_signals_found", []))
            missed = len(enrichment.get("_signals_missed", []))
            logger.debug(
                "  %s @ %s — %d signals found, %d missed",
                lead.name,
                lead.organization,
                found,
                missed,
            )

    logger.info("Enrichment complete: %d leads processed", len(enriched_leads))
    return enriched_leads
