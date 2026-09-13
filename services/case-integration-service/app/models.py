import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Text
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

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
    tenant_id = Column(String(36), nullable=False, index=True)
    servicenow_sys_id = Column(String(32), nullable=True, index=True)
    case_number = Column(String(50), nullable=False, unique=True, index=True)
    hospital_id = Column(String(36), nullable=False)
    service_code = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="ACCEPTED")
    correlation_id = Column(String(64), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
