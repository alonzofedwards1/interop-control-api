from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.token_routes import router as auth_router
from app.health.routes import router as health_router
from app.pd.routes import router as pd_router
from app.patient.search_routes import router as patient_search_router

# CREATE APP FIRST
app = FastAPI(title="Interop Control API")

# ROOT PROBE
@app.get("/")
def root():
    return {
        "service": "interop-control-api",
        "status": "running"
    }

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(pd_router)
app.include_router(patient_search_router)
