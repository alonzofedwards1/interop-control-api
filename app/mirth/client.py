import httpx
import os

DEFAULT_MIRTH_PD_ENDPOINT = os.getenv(
    "MIRTH_PD_ENDPOINT",
    "http://100.27.251.103:6662/pd/trigger/"
)


async def send_pd_request(
    *,
    endpoint_url: str | None = None,
    payload: dict | None = None,
) -> httpx.Response:
    """Forward a patient discovery trigger to Mirth.

    The endpoint is configurable via PD_ENDPOINT_URL/MIRTH_PD_ENDPOINT and
    the payload is expected to already match the Mirth contract
    (currently only patient_reference).
    """
    if payload is None:
        raise ValueError("payload is required for PD requests")

    url = endpoint_url or DEFAULT_MIRTH_PD_ENDPOINT

    print(f"📡 Posting PD trigger to Mirth: {url}")
    print(f"📦 Payload: {payload}")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )

    response.raise_for_status()

    print(f"✅ Mirth acknowledged request ({response.status_code})")

    return response
