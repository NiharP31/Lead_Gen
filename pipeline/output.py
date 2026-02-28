import json
import csv
import logging
from pathlib import Path
from models.lead import EnrichedLead

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def save_json(leads: list[EnrichedLead], filename: str = "enriched_leads.json") -> Path:
    """Export enriched leads as JSON."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / filename
    data = [lead.model_dump() for lead in leads]
    path.write_text(json.dumps(data, indent=2, default=str))
    logger.info("Saved %d leads to %s", len(leads), path)
    return path


def save_csv(leads: list[EnrichedLead], filename: str = "enriched_leads.csv") -> Path:
    """Export enriched leads as a flat CSV (best-effort flattening)."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / filename

    rows = []
    for lead in leads:
        row = {
            "lead_id": lead.lead_id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "organization": lead.organization,
            "designation": lead.designation,
            "linkedin_url": lead.linkedin_url,
            "campaign_id": lead.campaign_id,
            "campaign_name": lead.campaign_name,
        }

        # Flatten company overview
        if lead.company_overview:
            row["company_description"] = lead.company_overview.description
            row["company_industry"] = lead.company_overview.industry
            row["company_headcount"] = lead.company_overview.headcount
            row["company_founded_year"] = lead.company_overview.founded_year
            row["company_region"] = lead.company_overview.region
            row["company_estimated_revenue"] = lead.company_overview.estimated_revenue

        # Tech stack as comma-separated
        if lead.tech_stack:
            row["tech_stack"] = ", ".join(str(t) for t in lead.tech_stack)

        # Funding
        if lead.funding:
            row["total_funding_usd"] = lead.funding.total_funding_usd
            row["funding_history"] = json.dumps(lead.funding.funding_history, default=str) if lead.funding.funding_history else None
            row["company_news_summary"] = lead.funding.news_summary

        # LinkedIn posts
        if lead.linkedin_posts:
            row["linkedin_posts"] = " | ".join(lead.linkedin_posts[:3])

        # Metadata
        row["signals_found"] = ", ".join(lead.enrichment_metadata.signals_found)
        row["signals_missed"] = ", ".join(lead.enrichment_metadata.signals_missed)
        row["enriched_at"] = lead.enrichment_metadata.enriched_at

        rows.append(row)

    if rows:
        # Collect all possible keys across all rows
        fieldnames = list(dict.fromkeys(k for row in rows for k in row.keys()))
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    logger.info("Saved %d leads to %s", len(leads), path)
    return path


def print_summary(leads: list[EnrichedLead]) -> None:
    """Print a quick summary of enrichment results."""
    total = len(leads)
    with_overview = sum(1 for l in leads if l.company_overview)
    with_tech = sum(1 for l in leads if l.tech_stack)
    with_funding = sum(1 for l in leads if l.funding)
    with_posts = sum(1 for l in leads if l.linkedin_posts)

    all_found = []
    all_missed = []
    for lead in leads:
        all_found.extend(lead.enrichment_metadata.signals_found)
        all_missed.extend(lead.enrichment_metadata.signals_missed)

    print("\n" + "=" * 60)
    print("ENRICHMENT SUMMARY")
    print("=" * 60)
    print(f"Total leads processed:    {total}")
    print(f"With company overview:    {with_overview}/{total}")
    print(f"With tech stack:          {with_tech}/{total}")
    print(f"With funding data:        {with_funding}/{total}")
    print(f"With LinkedIn posts:      {with_posts}/{total}")
    print(f"Total signals found:      {len(all_found)}")
    print(f"Total signals missed:     {len(all_missed)}")
    print("=" * 60 + "\n")
