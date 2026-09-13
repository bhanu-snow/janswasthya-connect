import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Text, Integer
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class HospitalGroup(Base):
    """Primary tenant boundary (tenant_id = hospital_group_id)."""
    __tablename__ = "hospital_group"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    hospitals = relationship("Hospital", back_populates="hospital_group", cascade="all, delete-orphan")

class Hospital(Base):
    __tablename__ = "hospital"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    hospital_group_id = Column(String(36), ForeignKey("hospital_group.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    hospital_group = relationship("HospitalGroup", back_populates="hospitals")
    facilities = relationship("Facility", back_populates="hospital", cascade="all, delete-orphan")

class Facility(Base):
    __tablename__ = "facility"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    hospital_id = Column(String(36), ForeignKey("hospital.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    hospital = relationship("Hospital", back_populates="facilities")
    departments = relationship("Department", back_populates="facility", cascade="all, delete-orphan")

class Department(Base):
    __tablename__ = "department"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    facility_id = Column(String(36), ForeignKey("facility.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    facility = relationship("Facility", back_populates="departments")
    services = relationship("HealthcareService", back_populates="department", cascade="all, delete-orphan")

class HealthcareService(Base):
    __tablename__ = "healthcare_service"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    department_id = Column(String(36), ForeignKey("department.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    department = relationship("Department", back_populates="services")

class IdempotencyRecord(Base):
    __tablename__ = "idempotency_record"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    key = Column(String(255), nullable=False, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    request_hash = Column(String(64), nullable=False)
    response_code = Column(Integer, nullable=False)
    response_body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class CaseReference(Base):
    __tablename__ = "case_reference"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("hospital_group.id"), nullable=False, index=True)
    servicenow_sys_id = Column(String(32), nullable=True, index=True)
    case_number = Column(String(50), nullable=False, unique=True, index=True)
    hospital_id = Column(String(36), ForeignKey("hospital.id"), nullable=False)
    service_code = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="NEW")
    correlation_id = Column(String(64), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
