# Test Environment Notes

This repository is currently on the `test` branch. Use these notes when exercising the Patient Discovery (PD) trigger flow in the test environment.

## Patient Discovery forwarding

- The PD trigger endpoint in FastAPI is `/api/pd/trigger/`.
- The PD endpoint URL is read from the `PD_ENDPOINT_URL` environment variable (fallback to `http://100.27.251.103:6662/pd/trigger/`).
- The payload forwarded to Mirth matches the working curl example: `{ "patient_reference": "<value>" }`.
- Logs will indicate the destination URL, payload, and whether the Mirth call succeeded.

## Environment setup

1. Copy `.env.example` to `.env` if you have not already.
2. Set `PD_ENDPOINT_URL` in `.env` if you need to override the default test endpoint.
3. Start the API locally with `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

These steps keep the test environment aligned with the known-working Mirth endpoint and payload expectations.
