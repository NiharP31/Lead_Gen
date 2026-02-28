import logging
import requests
from models.lead import RawLead
import config

logger = logging.getLogger(__name__)


class AturiyaClient:
    """Client for the Aturiya SDR Agent API."""

    def __init__(self, token: str | None = None):
        self.base_url = config.ATURIYA_BASE_URL
        self.token = token or config.ATURIYA_BEARER_TOKEN
        self.user_id = config.ATURIYA_USER_ID
        self.agent_id = config.ATURIYA_AGENT_ID
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
        })

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def verify_auth(self) -> dict:
        """Verify the bearer token and return user info."""
        resp = self.session.get(self._url("/users/auth/me"))
        resp.raise_for_status()
        return resp.json()

    def list_campaigns(self) -> list[dict]:
        """List all campaigns for the configured SDR agent."""
        url = self._url(
            f"/users/{self.user_id}/agents/sdr/{self.agent_id}/campaigns"
        )
        resp = self.session.get(url)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])

    def get_leads(
        self,
        campaign_id: str,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[RawLead], dict]:
        """Fetch leads for a campaign. Returns (leads, pagination_info)."""
        url = self._url(
            f"/users/{self.user_id}/agents/sdr/{self.agent_id}/leads"
        )
        params = {
            "campaign_id": campaign_id,
            "page": page,
            "per_page": per_page,
        }
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        leads = [RawLead(**lead) for lead in data.get("data", [])]
        pagination = data.get("pagination", {})

        logger.info(
            "Fetched %d leads (page %d/%d)",
            len(leads),
            pagination.get("page", 1),
            pagination.get("total_pages", 1),
        )
        return leads, pagination

    def get_all_leads(self, campaign_id: str) -> list[RawLead]:
        """Fetch all leads across all pages for a campaign."""
        all_leads = []
        page = 1
        while True:
            leads, pagination = self.get_leads(campaign_id, page=page)
            all_leads.extend(leads)
            if not pagination.get("has_next_page", False):
                break
            page += 1
        logger.info("Total leads fetched: %d", len(all_leads))
        return all_leads
