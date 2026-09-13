# workers/integration-worker/app/models.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class OutboxEvent(Base):
    __tablename__ = "outbox_event"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    aggregate_type = Column(String(50), nullable=False)
    aggregate_id = Column(String(36), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    payload = Column(Text, nullable=False)
    status = Column(String(30), nullable=False, default="PENDING", index=True)
    retry_count = Column(Integer, nullable=False, default=0)
    correlation_id = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    processed_at = Column(DateTime, nullable=True)

class IntegrationMessage(Base):
    __tablename__ = "integration_message"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    correlation_id = Column(String(64), nullable=False, index=True)
    direction = Column(String(20), nullable=False, default="OUTBOUND")
    target_system = Column(String(50), nullable=False)
    payload = Column(Text, nullable=False)
    status = Column(String(30), nullable=False, default="ENQUEUED", index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class IntegrationAttempt(Base):
    __tablename__ = "integration_attempt"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    message_id = Column(String(36), ForeignKey("integration_message.id"), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False)
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    attempted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class DeadLetterMessage(Base):
    __tablename__ = "dead_letter_message"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    correlation_id = Column(String(64), nullable=False, index=True)
    original_payload = Column(Text, nullable=False)
    failure_reason = Column(Text, nullable=False)
    retry_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    replayed_at = Column(DateTime, nullable=True)