from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import HospitalGroup, Hospital, Facility, HealthcareService
from app.schemas import HospitalGroupOut, HospitalOut, FacilityOut, HealthcareServiceOut

app = FastAPI(
    title="JanSwasthya Connect - Master Data Service",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "master-data-service"
    }

@app.get("/api/v1/hospital-groups", response_model=List[HospitalGroupOut])
def list_hospital_groups(db: Session = Depends(get_db)):
    """List all hospital groups (tenants)."""
    return db.query(HospitalGroup).all()

@app.get("/api/v1/hospitals", response_model=List[HospitalOut])
def list_hospitals(
    tenant_id: Optional[str] = Query(None, description="Hospital Group ID"),
    db: Session = Depends(get_db)
):
    """List hospitals filtered by tenant (hospital group)."""
    query = db.query(Hospital)
    if tenant_id:
        query = query.filter(Hospital.hospital_group_id == tenant_id)
    return query.all()

@app.get("/api/v1/facilities", response_model=List[FacilityOut])
def list_facilities(
    hospital_id: Optional[str] = Query(None, description="Hospital ID"),
    db: Session = Depends(get_db)
):
    """List facilities filtered by hospital."""
    query = db.query(Facility)
    if hospital_id:
        query = query.filter(Facility.hospital_id == hospital_id)
    return query.all()

@app.get("/api/v1/services", response_model=List[HealthcareServiceOut])
def list_healthcare_services(
    department_id: Optional[str] = Query(None, description="Department ID"),
    db: Session = Depends(get_db)
):
    """List healthcare services filtered by department."""
    query = db.query(HealthcareService)
    if department_id:
        query = query.filter(HealthcareService.department_id == department_id)
    return query.all()
