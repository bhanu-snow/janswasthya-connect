from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class HealthcareServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    department_id: str
    name: str
    code: str
    created_at: datetime

class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    facility_id: str
    name: str
    created_at: datetime
    services: List[HealthcareServiceOut] = []

class FacilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    hospital_id: str
    name: str
    created_at: datetime
    departments: List[DepartmentOut] = []

class HospitalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    hospital_group_id: str
    name: str
    code: str
    created_at: datetime
    facilities: List[FacilityOut] = []

class HospitalGroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    is_active: bool
    created_at: datetime
    hospitals: List[HospitalOut] = []
