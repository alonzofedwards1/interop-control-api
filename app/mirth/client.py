import httpx
import os

MIRTH_PD_ENDPOINT = os.getenv(
    "MIRTH_PD_ENDPOINT",
    "http://mirth:8080/api/channels/PD_Request_In"
)

async def send_pd_request(payload: dict):
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            MIRTH_PD_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        response.raise_for_status()
