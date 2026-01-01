from __future__ import annotations

import httpx


async def send_pd_request(endpoint_url: str, payload: dict) -> httpx.Response:
    print(f"📡 Posting PD trigger to Mirth: {endpoint_url}")
    print(f"📦 Payload: {payload}")

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            endpoint_url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )

    response.raise_for_status()

    print(f"✅ Mirth acknowledged request ({response.status_code})")

    return response
