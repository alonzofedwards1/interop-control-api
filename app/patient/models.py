from pydantic import BaseModel
from typing import Dict


class PatientSearchRequest(BaseModel):
    first_name: str
    last_name: str
    dob: str


class PatientSearchResponse(BaseModel):
    status: str
    execution_id: str
    criteria: Dict
