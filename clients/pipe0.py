import logging
import time
import requests
import config

logger = logging.getLogger(__name__)

# Pipe IDs for each enrichment signal
PIPES = {
    "company_overview": "company:overview@2",
    "tech_stack": "company:techstack:builtwith@1",
    "funding": "company:funding:leadmagic@1",
    "news": "company:newssummary:website@1",
    "linkedin_posts": "people:posts:crustdata@1",
}


class Pipe0Client:
    """Client for the pipe0 enrichment API."""

    def __init__(self, api_key: str | None = None):
        self.base_url = config.PIPE0_BASE_URL
        self.api_key = api_key or config.PIPE0_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    def _build_pipes_list(self) -> list[dict]:
        """Build the pipes array based on enabled enrichment signals."""
        pipes = []
        for signal, pipe_id in PIPES.items():
            if config.ENRICHMENT_PIPES.get(signal, False):
                pipes.append({"pipe_id": pipe_id})
        return pipes

    def _build_input(self, leads_batch: list[dict]) -> list[dict]:
        """Convert leads into pipe0 input format.

        pipe0 expects fields like:
        - company_website_url (or company_name) for company pipes
        - profile_url for people pipes (LinkedIn URL)
        """
        inputs = []
        for i, lead in enumerate(leads_batch):
            entry = {"id": i + 1}

            # Company identification — derive domain from email if no website
            org = lead.get("organization", "")
            email = lead.get("email", "")
            website = lead.get("website")

            if website:
                entry["company_website_url"] = website
            elif email and "@" in email:
                domain = email.split("@")[1]
                # Skip generic email providers
                generic = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}
                if domain not in generic:
                    entry["company_website_url"] = domain
            if org:
                entry["company_name"] = org

            # LinkedIn URL for people pipes
            linkedin = lead.get("linkedin_url")
            if linkedin:
                entry["profile_url"] = linkedin

            inputs.append(entry)
        return inputs

    def enrich_sync(self, leads_batch: list[dict]) -> dict:
        """Run enrichment synchronously for a batch of <=9 leads.

        Returns the raw pipe0 response.
        """
        pipes = self._build_pipes_list()
        if not pipes:
            logger.warning("No enrichment pipes enabled")
            return {}

        payload = {
            "pipes": pipes,
            "input": self._build_input(leads_batch),
            "config": {"environment": config.PIPE0_ENVIRONMENT},
        }

        resp = self.session.post(
            f"{self.base_url}/v1/pipes/run/sync",
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("errors"):
            logger.warning("pipe0 returned errors: %s", data["errors"])

        logger.info(
            "pipe0 sync run %s — status: %s",
            data.get("id", "?"),
            data.get("status", "?"),
        )
        return data

    def enrich_async(self, leads_batch: list[dict]) -> str:
        """Start an async enrichment run. Returns the run_id for polling."""
        pipes = self._build_pipes_list()
        if not pipes:
            return ""

        payload = {
            "pipes": pipes,
            "input": self._build_input(leads_batch),
            "config": {"environment": config.PIPE0_ENVIRONMENT},
        }

        resp = self.session.post(
            f"{self.base_url}/v1/pipes/run",
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        run_id = data.get("id", "")
        logger.info("pipe0 async run started: %s", run_id)
        return run_id

    def check_run(self, run_id: str) -> dict:
        """Poll the status of an async run."""
        resp = self.session.get(f"{self.base_url}/v1/pipes/check/{run_id}")
        resp.raise_for_status()
        return resp.json()

    def wait_for_run(self, run_id: str, timeout: int = 120, interval: int = 3) -> dict:
        """Poll an async run until it completes or times out."""
        start = time.time()
        while time.time() - start < timeout:
            result = self.check_run(run_id)
            status = result.get("status", "")
            if status in ("completed", "failed"):
                return result
            logger.debug("Run %s still %s, waiting...", run_id, status)
            time.sleep(interval)
        raise TimeoutError(f"pipe0 run {run_id} did not complete within {timeout}s")

    @staticmethod
    def parse_enrichment(pipe0_response: dict, batch_index_map: dict[int, str]) -> dict[str, dict]:
        """Parse pipe0 response into a dict keyed by lead_id.

        Args:
            pipe0_response: Raw pipe0 API response.
            batch_index_map: Maps pipe0 input id (1-based) to lead_id.

        Returns:
            {lead_id: {field_name: value, ...}} for each lead.
        """
        records = pipe0_response.get("records", {})
        results = {}

        for rec_id_str, record in records.items():
            rec_id = int(rec_id_str) if rec_id_str.isdigit() else record.get("id")
            lead_id = batch_index_map.get(rec_id)
            if not lead_id:
                continue

            fields = record.get("fields", {})
            enriched = {}
            signals_found = []
            signals_missed = []

            for field_name, field_data in fields.items():
                # Skip input echo fields
                resolved_by = field_data.get("resolved_by") or {}
                if resolved_by.get("ref") == "input":
                    continue

                status = field_data.get("status", "")
                value = field_data.get("value")

                if status == "completed" and value is not None:
                    enriched[field_name] = value
                    signals_found.append(field_name)
                else:
                    signals_missed.append(field_name)

            enriched["_signals_found"] = signals_found
            enriched["_signals_missed"] = signals_missed
            enriched["_run_id"] = pipe0_response.get("id")
            results[lead_id] = enriched

        return results
