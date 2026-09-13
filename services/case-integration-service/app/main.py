import hashlib
import json
import uuid
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CaseReference, IdempotencyRecord, OutboxEvent
from app.schemas import InboundCaseCreate, InboundCaseResponse

app = FastAPI(
    title="JanSwasthya Connect - Case Integration Service",
    version="0.1.0"
)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "case-integration-service"}

@app.post("/api/v1/cases", response_model=InboundCaseResponse, status_code=status.HTTP_201_CREATED)
def ingest_case(
    payload: InboundCaseCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-ID"),
    db: Session = Depends(get_db)
):
    correlation_id = x_correlation_id or f"corr-{uuid.uuid4()}"
    raw_payload_bytes = json.dumps(payload.model_dump(), sort_keys=True).encode("utf-8")
    payload_hash = hashlib.sha256(raw_payload_bytes).hexdigest()

    # 1. Check Idempotency Key
    existing_key = db.query(IdempotencyRecord).filter(
        IdempotencyRecord.key == idempotency_key,
        IdempotencyRecord.tenant_id == payload.tenant_id
    ).first()

    if existing_key:
        if existing_key.request_hash != payload_hash:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Idempotency key reuse with different request payload."
            )
        cached_response = json.loads(existing_key.response_body)
        return cached_response

    # 2. Check Case Uniqueness
    existing_case = db.query(CaseReference).filter(CaseReference.case_number == payload.case_number).first()
    if existing_case:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Case {payload.case_number} already ingested with ID {existing_case.id}."
        )

    # 3. Create Case Reference
    new_case = CaseReference(
        tenant_id=payload.tenant_id,
        servicenow_sys_id=payload.servicenow_sys_id,
        case_number=payload.case_number,
        hospital_id=payload.hospital_id,
        service_code=payload.service_code,
        status="ACCEPTED",
        correlation_id=correlation_id
    )
    db.add(new_case)
    db.flush()

    # 4. Atomic Outbox Enqueue
    outbox_payload = {
        "case_id": new_case.id,
        "case_number": new_case.case_number,
        "hospital_id": new_case.hospital_id,
        "service_code": new_case.service_code,
        "tenant_id": new_case.tenant_id,
        "correlation_id": correlation_id,
        "case_created_at": new_case.created_at.isoformat(),
        "case_updated_at": new_case.updated_at.isoformat(),
    }

    provider_outbox_entry = OutboxEvent(
        tenant_id=payload.tenant_id,
        aggregate_type="CaseReference",
        aggregate_id=new_case.id,
        event_type="CASE_ACCEPTED_FOR_DISPATCH",
        payload=json.dumps(outbox_payload),
        status="PENDING",
        correlation_id=correlation_id
    )

    analytics_outbox_entry = OutboxEvent(
        tenant_id=payload.tenant_id,
        aggregate_type="CaseReference",
        aggregate_id=new_case.id,
        event_type="CASE_ACCEPTED_FOR_ANALYTICS",
        payload=json.dumps(outbox_payload),
        status="PENDING",
        correlation_id=correlation_id
    )

    db.add(provider_outbox_entry)
    db.add(analytics_outbox_entry)
    
    response_data = {
        "case_reference_id": new_case.id,
        "case_number": new_case.case_number,
        "status": new_case.status,
        "correlation_id": new_case.correlation_id,
        "message": "Case successfully received and registered and stored for analytics usage as well."
    }

    # 5. Record Idempotency and Commit Transaction
    idem_record = IdempotencyRecord(
        key=idempotency_key,
        tenant_id=payload.tenant_id,
        request_hash=payload_hash,
        response_code=status.HTTP_201_CREATED,
        response_body=json.dumps(response_data)
    )
    db.add(idem_record)
    db.commit()

    return response_data
