import httpx
import logging
from app.config.settings import get_settings

logger = logging.getLogger("pd.mirth")


async def send_pd_request(payload: dict) -> tuple[int, str]:
    settings = get_settings()

    logger.info("📡 Preparing HTTP POST to Mirth")
    logger.info("📍 Mirth endpoint: %s", settings.PD_ENDPOINT_URL)
    logger.info("📦 Payload: %s", payload)

    async def send_pd_request(
            endpoint_url: str,
            payload: dict,
    ) -> None:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                endpoint_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                },
            )

            response.raise_for_status()


