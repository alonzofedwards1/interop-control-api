from fastapi import APIRouter

from app.pd.callback_routes import router as callback_router
from app.pd.trigger_routes import router as trigger_router

router = APIRouter(prefix="/api/pd", tags=["patient-discovery"])

router.include_router(callback_router)
router.include_router(trigger_router)
