import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
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
