# Lead Enrichment Pipeline

A programmatic lead enrichment layer that takes raw campaign leads from the Aturiya API (Apollo data) and enriches them with supplementary signals via pipe0 — company overview, tech stack, funding events, news triggers, and LinkedIn activity — producing structured, outreach-ready lead objects for an AI SDR agent.

## Architecture

```
                        CLI (main.py)
                             │
                    ┌────────┴────────┐
                    │                 │
              Aturiya API         pipe0 API
           (Apollo leads)      (enrichment)
                    │                 │
                    └────────┬────────┘
                             │
                      EnrichedLead
                     (Pydantic model)
                             │
                    ┌────────┴────────┐
                    │                 │
               JSON / CSV        FastAPI
                output         (runtime API)
                                     │
                              React Frontend
                            (leads table + UI)
```

### Design Rationale

- **Apollo provides the base** — contact info, company name, designation, LinkedIn URL. The pipeline does not duplicate any of this.
- **pipe0 fills the gaps** — signals Apollo doesn't cover: deeper company intel, tech stack (via BuiltWith), funding history (via LeadMagic), news summaries, and LinkedIn posts (via Crustdata).
- **Two access modes**: batch CLI for bulk enrichment, FastAPI for on-demand single-lead enrichment (what the SDR agent would call at runtime).
- **Pydantic models throughout** — `RawLead` → `EnrichedLead` with strict typing and validation at every stage.

## Enrichment Signals (pipe0 Layer)

| Signal | Pipe | What It Adds |
|--------|------|--------------|
| Company Overview | `company:overview@2` | Description, industry, headcount, founded year, region, estimated revenue |
| Tech Stack | `company:techstack:builtwith@1` | Technologies and platforms the company uses |
| Funding | `company:funding:leadmagic@1` | Total funding, funding rounds, history |
| News | `company:newssummary:website@1` | Recent news summary and trigger events |
| LinkedIn Posts | `people:posts:crustdata@1` | Recent LinkedIn activity for personalisation hooks |

Each signal can be independently toggled in `config.py` → `ENRICHMENT_PIPES` to control cost per lead.

## Project Structure

```
├── clients/
│   ├── aturiya.py          # Aturiya API client (auth, campaigns, leads)
│   └── pipe0.py            # pipe0 API client (sync/async enrichment, response parsing)
├── models/
│   └── lead.py             # Pydantic models: RawLead, EnrichedLead, CompanyOverview, etc.
├── pipeline/
│   ├── ingest.py           # Stage 1: Fetch raw leads from Aturiya
│   ├── enrich.py           # Stage 2: Enrich via pipe0 (batch + single-lead)
│   └── output.py           # Stage 3: Export to JSON/CSV + summary
├── api/
│   ├── app.py              # FastAPI app with CORS
│   ├── deps.py             # Singleton clients via lru_cache
│   └── routes/
│       ├── health.py       # GET /api/health
│       ├── campaigns.py    # GET /api/campaigns
│       └── leads.py        # GET /api/campaigns/{id}/leads, POST /api/leads/{id}/enrich
├── frontend/               # React + Vite + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/     # CampaignSelector, LeadsTable, LeadRow, LeadDetail, etc.
│   │   ├── hooks/          # useCampaigns, useLeads, useEnrich
│   │   └── types.ts        # TypeScript type definitions matching backend models
│   ├── Dockerfile          # Multi-stage: Node build → nginx serve
│   └── nginx.conf          # SPA routing + /api proxy to backend
├── config.py               # Centralised configuration (env vars + enrichment toggles)
├── main.py                 # CLI entry point
├── backend.Dockerfile      # Python 3.12-slim + uvicorn
├── docker-compose.yml      # Backend + frontend services
└── requirements.txt
```

## Setup

### Prerequisites

- Python 3.12+
- Node.js 20+ (for frontend development)
- Docker & Docker Compose (for containerised deployment)

### Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
# Aturiya API
ATURIYA_BEARER_TOKEN=your_token
ATURIYA_USER_ID=your_user_id
ATURIYA_AGENT_ID=your_agent_id

# pipe0 API
PIPE0_API_KEY=your_pipe0_key
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### CLI — Batch Enrichment

```bash
# Enrich all leads from the first campaign
python main.py

# Enrich leads from a specific campaign
python main.py --campaign-id <campaign_id>

# Limit to first 5 leads (useful for testing / controlling cost)
python main.py --limit 5

# Output format: json, csv, or both (default: both)
python main.py --format json
```

Output is written to `output/enriched_leads.json` and `output/enriched_leads.csv`.

### FastAPI — Runtime API

```bash
uvicorn api.app:app --reload
```

Open `http://localhost:8000/docs` for the interactive Swagger UI.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/campaigns` | List all campaigns |
| `GET` | `/api/campaigns/{id}/leads` | Get raw leads for a campaign |
| `POST` | `/api/leads/{id}/enrich` | Enrich a single lead on demand |

### Web UI

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Select a campaign, view leads in a table, and click "Enrich" on any row to trigger on-demand enrichment and view the results.

### Docker Compose

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

## Key Design Decisions

1. **Batch size of 9** — pipe0's sync endpoint has a limit of <10 records. The pipeline batches leads accordingly and processes them sequentially. For larger volumes, the async endpoint (`enrich_async` + `wait_for_run`) is available but not used by default to keep the pipeline simpler and more predictable.

2. **Graceful degradation per batch** — if a pipe0 batch call fails, that batch's leads are returned with empty enrichment rather than crashing the entire pipeline. Each lead's `enrichment_metadata.signals_missed` tracks exactly what was unavailable.

3. **Domain extraction from email** — when a lead has no `website` field, the pipeline extracts the company domain from the email address (filtering out generic providers like gmail.com, yahoo.com). This maximises company-level enrichment coverage.

4. **Signal toggles for cost control** — each enrichment pipe can be toggled on/off in `config.py` without code changes. This lets you balance coverage vs. cost per lead.

5. **Separate `enrich_one()` for runtime use** — the FastAPI endpoint calls `enrich_one()` which enriches a single lead synchronously, suitable for the SDR agent's real-time needs. The batch `enrich_leads()` remains for bulk processing.

6. **No duplication with Apollo** — the pipeline only adds signals Apollo doesn't provide: tech stack, funding history, news triggers, and LinkedIn posts. Apollo's contact and firmographic data flows through untouched.

## Tradeoffs

| Decision | Trade-off |
|----------|-----------|
| Sync over async enrichment | Simpler, more predictable, but slower for large batches. Async is implemented but not the default path. |
| All 5 pipes enabled by default | Maximum coverage but higher cost per lead. Toggle off less valuable signals for cost-sensitive campaigns. |
| No caching / deduplication | Each run re-enriches from scratch. With more time, I'd add a local cache keyed by `(lead_id, signal)` to avoid redundant API calls. |
| Single-threaded batching | Batches run sequentially. Concurrent batch processing would improve throughput but adds complexity and risk of rate limiting. |

## Known Limitations & Failure Modes

- **pipe0 rate limits / credits** — if the API key runs out of credits, enrichment returns successfully but with all signals missed. The pipeline doesn't fail — it degrades silently and reports the missed signals in metadata.
- **No retry logic** — if a pipe0 call fails (network error, 5xx), the batch is skipped. A production system would add exponential backoff retries.
- **No persistent storage** — enrichment results are written to flat files (JSON/CSV) or returned via API. A production deployment would write to a database to avoid re-enrichment and enable historical tracking.
- **No authentication on the API** — the FastAPI endpoints are open. A production deployment would add API key or JWT authentication.
- **Leads with no email and no website** — these leads get minimal enrichment since pipe0 can't identify the company. The pipeline still processes them but most signals will be missed.

## What I'd Add With More Time

- **Result caching** — store enriched leads in a database (PostgreSQL) to avoid paying for re-enrichment of the same lead.
- **Retry with backoff** — automatic retries on transient pipe0 failures.
- **Webhook / async enrichment mode** — for high-volume campaigns, kick off async pipe0 runs and poll for results.
- **Enrichment quality scoring** — score each enriched lead based on how many signals were found vs. missed, to prioritise outreach on the best-enriched leads.
- **Job postings signal** — add a pipe0 pipe for job postings data (hiring intent + budget signal), which the current implementation doesn't include.
