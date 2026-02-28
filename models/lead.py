from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RawLead(BaseModel):
    """Lead as returned by the Aturiya API (Apollo data)."""
    lead_id: str
    agent_id: str
    campaign_id: str
    task_id: Optional[str] = None
    task_status: Optional[str] = None
    campaign_name: Optional[str] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    designation: Optional[str] = None
    linkedin_url: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    created_at: Optional[str] = None


class CompanyOverview(BaseModel):
    description: Optional[str] = None
    industry: Optional[str] = None
    headcount: Optional[str] = None
    founded_year: Optional[str] = None
    region: Optional[str] = None
    estimated_revenue: Optional[str] = None


class FundingInfo(BaseModel):
    total_funding_usd: Optional[int] = None
    funding_history: Optional[list] = None
    news_summary: Optional[str] = None


class EnrichmentMetadata(BaseModel):
    enriched_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    signals_found: list[str] = Field(default_factory=list)
    signals_missed: list[str] = Field(default_factory=list)
    pipe0_run_id: Optional[str] = None


class EnrichedLead(BaseModel):
    """Fully enriched lead — Apollo data + pipe0 enrichments."""
    # Apollo data (from Aturiya)
    lead_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    designation: Optional[str] = None
    linkedin_url: Optional[str] = None
    campaign_id: str
    campaign_name: Optional[str] = None

    # pipe0 enrichments
    company_overview: Optional[CompanyOverview] = None
    tech_stack: Optional[list] = None
    funding: Optional[FundingInfo] = None
    linkedin_posts: Optional[list[str]] = None

    # Metadata
    enrichment_metadata: EnrichmentMetadata = Field(default_factory=EnrichmentMetadata)
