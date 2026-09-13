import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict
from fastapi import FastAPI, Header, HTTPException, status, Query
from app.schemas import AppointmentCreate, AppointmentResponse, ReferralCreate, ReferralResponse

app = FastAPI(
    title='JanSwasthya Connect - Mock Provider System',
    version='0.1.0'
)

# In-memory storage for simulated provider state
appointments_db: Dict[str, dict] = {}
referrals_db: Dict[str, dict] = {}

def apply_simulated_faults(mode: Optional[str]):
    """Simulate controllable failure modes per Section 23 of BRD."""
    if not mode:
        return
    mode = mode.lower()
    if mode == '400':
        raise HTTPException(status_code=400, detail='Simulated 400 Bad Request')
    elif mode == '404':
        raise HTTPException(status_code=404, detail='Simulated 404 Not Found')
    elif mode == '409':
        raise HTTPException(status_code=409, detail='Simulated 409 Conflict')
    elif mode == '500':
        raise HTTPException(status_code=500, detail='Simulated 500 Internal Server Error')

@app.get('/health')
def health():
    return {'status': 'healthy', 'service': 'mock-provider-system'}

@app.post('/api/v1/appointments', response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    payload: AppointmentCreate,
    x_simulate_mode: Optional[str] = Header(None, alias='X-Simulate-Mode'),
    x_simulate_delay_sec: Optional[int] = Header(None, alias='X-Simulate-Delay-Sec')
):
    if x_simulate_delay_sec and x_simulate_delay_sec > 0:
        await asyncio.sleep(x_simulate_delay_sec)

    apply_simulated_faults(x_simulate_mode)

    appt_id = f'APPT-{uuid.uuid4().hex[:8].upper()}'
    data = {
        'appointment_id': appt_id,
        'status': 'CONFIRMED',
        'scheduled_slot': payload.preferred_slot,
        'hospital_id': payload.hospital_id,
        'department_code': payload.department_code,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    appointments_db[appt_id] = data
    return data

@app.get('/api/v1/appointments/{appointment_id}', response_model=AppointmentResponse)
def get_appointment(appointment_id: str):
    if appointment_id not in appointments_db:
        raise HTTPException(status_code=404, detail='Appointment not found')
    return appointments_db[appointment_id]

@app.post('/api/v1/referrals', response_model=ReferralResponse, status_code=status.HTTP_201_CREATED)
async def create_referral(
    payload: ReferralCreate,
    x_simulate_mode: Optional[str] = Header(None, alias='X-Simulate-Mode')
):
    apply_simulated_faults(x_simulate_mode)

    ref_id = f'REF-{uuid.uuid4().hex[:8].upper()}'
    data = {
        'referral_id': ref_id,
        'status': 'PENDING_TRIAGE',
        'source_hospital_id': payload.source_hospital_id,
        'target_hospital_id': payload.target_hospital_id,
        'specialty': payload.specialty,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    referrals_db[ref_id] = data
    return data

@app.get('/api/v1/referrals/{referral_id}', response_model=ReferralResponse)
def get_referral(referral_id: str):
    if referral_id not in referrals_db:
        raise HTTPException(status_code=404, detail='Referral not found')
    return referrals_db[referral_id]
