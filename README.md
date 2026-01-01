# Interop Control API

FastAPI-based control plane for interoperability demos. This service manages OAuth2 tokens for external systems and orchestrates patient discovery triggers without persisting PHI.

## Features

- OAuth2 password grant manager with manual credential submission and automatic refresh.
- Token health metadata and JWT decoding (no signature verification).
- Patient discovery trigger forwarding with immediate correlation IDs and no data persistence.
- Simple health endpoint for infrastructure checks.

## Getting Started

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and update values for your OAuth2 provider and downstream patient discovery endpoint and callback target.

3. Run the API locally (default port `8000`):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Key Endpoints

- `GET /api/health/` - basic service health.
- `GET /api/health/ping` - lightweight uptime check.
- `POST /api/auth/token/manual` - submit OAuth2 password grant credentials and fetch a token.
- `GET /api/auth/token` - fetch current token (refreshing if close to expiry).
- `GET /api/auth/token/health` - token presence and expiry info.
- `POST /api/auth/token/decode` - decode JWT header and claims without verification.
- `POST /api/pd/trigger/` - forward demo patient discovery payload to configured downstream endpoint.
- `POST /api/pd/callback` - callback endpoint for PD responses from Mirth.

OpenAPI documentation is available at `/docs` and `/openapi.json` when the server is running.
