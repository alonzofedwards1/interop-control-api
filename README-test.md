# Test Environment Notes

This repository is currently on the `test` branch. Use these notes when exercising the Patient Discovery (PD) trigger flow in the test environment against the EC2 control plane.

## Patient Discovery forwarding

- The PD trigger endpoint in FastAPI is `/api/pd/trigger/`.
- The PD endpoint URL is read from the `PD_ENDPOINT_URL` environment variable (fallback to `http://100.27.251.103:6662/pd/trigger/`).
- The PD callback URL (used by Mirth's HTTP Sender) is read from `PD_CALLBACK_URL` (fallback to `${CONTROL_PLANE_BASE_URL}/api/pd/callback`).
- The payload forwarded to Mirth includes the patient reference, callback URL, and correlation ID to avoid Mirth defaulting to `localhost:8000`.
- Logs will indicate the destination URL, payload, and whether the Mirth call succeeded.

## Environment setup

1. Copy `.env.example` to `.env` if you have not already.
2. Set `CONTROL_PLANE_BASE_URL` to the EC2 control plane host (defaults to `http://100.27.251.103:8000`).
3. Set `PD_ENDPOINT_URL` and `PD_CALLBACK_URL` in `.env` if you need to override the default test endpoints.
4. Start the API locally with `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

These steps keep the test environment aligned with the known-working Mirth endpoint and payload expectations.

## Callback sanity checks

- Health: `curl -i ${CONTROL_PLANE_BASE_URL:-http://100.27.251.103:8000}/api/health/ping`
- Callback echo (expects HTTP 200):

```bash
curl -i \
  -H "Content-Type: application/json" \
  -H "x-correlation-id: test-corr-id" \
  -d '{"patient_reference":"demo","correlation_id":"test-corr-id"}' \
  ${CONTROL_PLANE_BASE_URL:-http://100.27.251.103:8000}/api/pd/callback
```

The callback logs the payload and correlation ID and responds with `{ "status": "received", "correlation_id": "test-corr-id" }`.
