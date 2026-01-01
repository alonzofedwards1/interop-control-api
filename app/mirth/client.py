import httpx
import os

MIRTH_PD_ENDPOINT = os.getenv(
    "MIRTH_PD_ENDPOINT",
    "http://100.27.251.103:6662/pd/trigger/"
)

async def send_pd_request(
    correlation_id: str,
    patient_reference: str,
) -> None:
    payload = {
        "correlation_id": correlation_id,
        "patient_reference": patient_reference,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            MIRTH_PD_ENDPOINT,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Correlation-ID": correlation_id,
            },
        )

        response.raise_for_status()
