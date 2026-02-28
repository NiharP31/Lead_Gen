import os
from dotenv import load_dotenv

load_dotenv()

# Aturiya API
ATURIYA_BASE_URL = "https://api.aturiya.ai"
ATURIYA_BEARER_TOKEN = os.getenv("ATURIYA_BEARER_TOKEN")
ATURIYA_USER_ID = os.getenv("ATURIYA_USER_ID")
ATURIYA_AGENT_ID = os.getenv("ATURIYA_AGENT_ID")

# pipe0 API
PIPE0_BASE_URL = "https://api.pipe0.com"
PIPE0_API_KEY = os.getenv("PIPE0_API_KEY")

# Enrichment settings
PIPE0_BATCH_SIZE = 9  # sync endpoint limit is <10 records
PIPE0_ENVIRONMENT = os.getenv("PIPE0_ENVIRONMENT", "production")

# Which enrichment pipes to run (toggle to control cost)
ENRICHMENT_PIPES = {
    "company_overview": True,
    "tech_stack": True,
    "funding": True,
    "news": True,
    "linkedin_posts": True,
}
