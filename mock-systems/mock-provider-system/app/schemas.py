from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AppointmentCreate(BaseModel):
    patient_identifier: str = Field(..., description='Synthetic patient ID or MRN')
    hospital_id: str
    department_code: str
    preferred_slot: str
    reason: Optional[str] = None

class AppointmentResponse(BaseModel):
    appointment_id: str
    status: str
    scheduled_slot: str
    hospital_id: str
    department_code: str
    created_at: str

class ReferralCreate(BaseModel):
    patient_identifier: str
    source_hospital_id: str
    target_hospital_id: str
    specialty: str
    urgency: str

class ReferralResponse(BaseModel):
    referral_id: str
    status: str
    source_hospital_id: str
    target_hospital_id: str
    specialty: str
    created_at: str
