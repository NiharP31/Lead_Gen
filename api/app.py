from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import health, campaigns, leads

app = FastAPI(title="Lead Enrichment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(campaigns.router)
app.include_router(leads.router)
