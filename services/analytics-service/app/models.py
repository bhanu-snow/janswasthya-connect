import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class HealthcareCaseFact(Base):
    __tablename__ = "healthcare_case_fact"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    tenant_id = Column(String(36), nullable=False, index=True)

    case_reference_id = Column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
    )

    hospital_id = Column(String(36), nullable=False, index=True)

    service_code = Column(String(50), nullable=False, index=True)

    status = Column(String(50), nullable=False, index=True)

    case_created_at = Column(DateTime, nullable=False)

    case_updated_at = Column(DateTime, nullable=False)

    ingested_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
