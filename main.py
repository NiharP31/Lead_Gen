"""
Lead Enrichment Pipeline
========================
Takes raw campaign leads from Aturiya (Apollo data) and enriches them
with additional signals via pipe0 — tech stack, funding, news, LinkedIn
activity — producing outreach-ready lead objects for the SDR agent.

Usage:
    python main.py                          # Enrich all leads from first campaign
    python main.py --campaign-id <id>       # Enrich leads from a specific campaign
    python main.py --limit 5                # Only process first N leads
    python main.py --format json            # Output format: json (default), csv, both
"""

import argparse
import logging
import sys

from pipeline.ingest import fetch_leads
from pipeline.enrich import enrich_leads
from pipeline.output import save_json, save_csv, print_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("pipeline")


def main():
    parser = argparse.ArgumentParser(description="Lead Enrichment Pipeline")
    parser.add_argument("--campaign-id", help="Aturiya campaign ID (default: first campaign)")
    parser.add_argument("--limit", type=int, help="Max leads to process")
    parser.add_argument("--format", choices=["json", "csv", "both"], default="both", help="Output format")
    args = parser.parse_args()

    # Stage 1: Ingest
    logger.info("=== STAGE 1: INGEST ===")
    raw_leads = fetch_leads(campaign_id=args.campaign_id)

    if not raw_leads:
        logger.error("No leads found. Exiting.")
        sys.exit(1)

    if args.limit:
        raw_leads = raw_leads[: args.limit]
        logger.info("Limited to %d leads", args.limit)

    # Stage 2: Enrich
    logger.info("=== STAGE 2: ENRICH ===")
    enriched_leads = enrich_leads(raw_leads)

    # Stage 3: Output
    logger.info("=== STAGE 3: OUTPUT ===")
    if args.format in ("json", "both"):
        save_json(enriched_leads)
    if args.format in ("csv", "both"):
        save_csv(enriched_leads)

    print_summary(enriched_leads)

    logger.info("Pipeline complete.")


if __name__ == "__main__":
    main()
