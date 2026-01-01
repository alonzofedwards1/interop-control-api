from pydantic import BaseModel
from typing import Optional


class PatientDiscoveryRequest(BaseModel):
    patient_reference: str


class PatientDiscoveryResponse(BaseModel):
    correlation_id: str
    forwarded: bool
    downstream_status: Optional[int]
    message: str
