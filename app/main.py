"""Interop Control API entrypoint."""
from fastapi import FastAPI

from app.auth.token_routes import router as auth_router
from app.health.routes import router as health_router
from app.pd.routes import router as pd_router

app = FastAPI(title="Interop Control API", version="0.1.0")

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(pd_router)
