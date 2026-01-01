from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import date
import uuid
import logging

router = APIRouter(prefix="/api/patient", tags=["patient-search"])

logger = logging.getLogger("patient-search")


# ============================
# Request / Response Models
# ============================

class PatientSearchRequest(BaseModel):
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Smith")
    dob: date = Field(..., example="1980-04-12")
    gender: str | None = Field(None, example="M")


class PatientSearchResponse(BaseModel):
    status: str
    execution_id: str
    criteria: dict


# ============================
# Route
# ============================

@router.post("/search", response_model=PatientSearchResponse)
async def patient_search(request: PatientSearchRequest):
    """
    Accepts patient demographics and triggers downstream Patient Discovery.
    This endpoint does NOT return PHI.
    """

    execution_id = str(uuid.uuid4())

    logger.info("Patient search received", extra={
        "execution_id": execution_id,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "dob": str(request.dob),
        "gender": request.gender,
    })

    # 🔒 Do NOT persist PHI
    # 🔄 Do NOT normalize
    # 📡 Just acknowledge orchestration

    return PatientSearchResponse(
        status="submitted",
        execution_id=execution_id,
        criteria=request.model_dump(),
    )
