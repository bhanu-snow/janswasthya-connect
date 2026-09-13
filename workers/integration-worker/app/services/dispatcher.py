import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import OutboxEvent, IntegrationMessage, IntegrationAttempt, DeadLetterMessage
from app.ports.provider import ProviderAdapterPort
from app.config import MAX_RETRIES

class OutboxDispatcher:
    def __init__(self, provider_adapter: ProviderAdapterPort, max_retries: int = MAX_RETRIES):
        self.provider = provider_adapter
        self.max_retries = max_retries

    def process_event(self, event: OutboxEvent, db: Session) -> None:
        payload_data = json.loads(event.payload)

        # 1. Audit Message Record
        msg = IntegrationMessage(
            tenant_id=event.tenant_id,
            correlation_id=event.correlation_id,
            direction="OUTBOUND",
            target_system="mock-provider-system",
            payload=event.payload,
            status="IN_PROGRESS"
        )
        db.add(msg)
        db.flush()

        # 2. Prepare Provider Payload
        provider_payload = {
            "patient_identifier": f"SYNTH-PAT-{event.aggregate_id[:8]}",
            "hospital_id": payload_data.get("hospital_id"),
            "department_code": payload_data.get("service_code", "CARD-OPD"),
            "preferred_slot": datetime.now(timezone.utc).isoformat(),
            "reason": "Automated case dispatch from integration worker"
        }

        # 3. Call External System via Adapter
        current_attempt_num = event.retry_count + 1
        status_code, response_text, is_success = self.provider.dispatch_appointment(
            payload=provider_payload,
            correlation_id=event.correlation_id
        )

        attempt = IntegrationAttempt(
            message_id=msg.id,
            attempt_number=current_attempt_num,
            response_status=status_code if status_code > 0 else None,
            response_body=response_text,
            error_message=None if is_success else f"HTTP Status {status_code}: {response_text}"
        )
        db.add(attempt)

        # 4. Handle Outcome
        if is_success:
            event.status = "PROCESSED"
            event.processed_at = datetime.now(timezone.utc)
            msg.status = "DELIVERED"
            db.commit()
        else:
            event.retry_count += 1
            if event.retry_count >= self.max_retries:
                event.status = "DEAD_LETTER"
                msg.status = "FAILED"
                dlq = DeadLetterMessage(
                    tenant_id=event.tenant_id,
                    correlation_id=event.correlation_id,
                    original_payload=event.payload,
                    failure_reason=f"Exhausted retries. Last error: HTTP {status_code}",
                    retry_count=event.retry_count
                )
                db.add(dlq)
            db.commit()