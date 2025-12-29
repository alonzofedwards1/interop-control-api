"""Interop Control API entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.token_routes import router as auth_router
from app.health.routes import router as health_router
from app.pd.routes import router as pd_router

app = FastAPI(title="Interop Control API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(pd_router)
