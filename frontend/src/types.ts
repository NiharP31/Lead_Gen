export interface Campaign {
  id: string;
  name: string;
  [key: string]: unknown;
}

export interface RawLead {
  lead_id: string;
  agent_id: string;
  campaign_id: string;
  task_id?: string;
  task_status?: string;
  campaign_name?: string;
  name: string;
  email?: string;
  phone?: string;
  organization?: string;
  designation?: string;
  linkedin_url?: string;
  website?: string;
  status?: string;
  type?: string;
  created_at?: string;
}

export interface CompanyOverview {
  description?: string;
  industry?: string;
  headcount?: string;
  founded_year?: string;
  region?: string;
  estimated_revenue?: string;
}

export interface FundingInfo {
  total_funding_usd?: number;
  funding_history?: unknown[];
  news_summary?: string;
}

export interface EnrichmentMetadata {
  enriched_at: string;
  signals_found: string[];
  signals_missed: string[];
  pipe0_run_id?: string;
}

export interface EnrichedLead {
  lead_id: string;
  name: string;
  email?: string;
  phone?: string;
  organization?: string;
  designation?: string;
  linkedin_url?: string;
  campaign_id: string;
  campaign_name?: string;
  company_overview?: CompanyOverview;
  tech_stack?: string[];
  funding?: FundingInfo;
  linkedin_posts?: string[];
  enrichment_metadata: EnrichmentMetadata;
}

export type LeadStatus = 'raw' | 'enriching' | 'enriched' | 'failed';
