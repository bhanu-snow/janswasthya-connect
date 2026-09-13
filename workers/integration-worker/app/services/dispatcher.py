import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import (
    OutboxEvent,
    IntegrationMessage,
    IntegrationAttempt,
    DeadLetterMessage,
)
from app.ports.provider import ProviderAdapterPort
from app.config import MAX_RETRIES


class OutboxDispatcher:
    def __init__(
        self,
        provider_adapter: ProviderAdapterPort,
        analytics_adapter,
        max_retries: int = MAX_RETRIES,
    ):
        self.provider = provider_adapter
        self.analytics = analytics_adapter
        self.max_retries = max_retries

    def process_event(self, event: OutboxEvent, db: Session) -> None:
        if event.event_type == "CASE_ACCEPTED_FOR_DISPATCH":
            self._process_provider_event(event, db)

        elif event.event_type == "CASE_ACCEPTED_FOR_ANALYTICS":
            self._process_analytics_event(event, db)

        else:
            event.status = "DEAD_LETTER"
            db.commit()

    def _process_provider_event(
        self,
        event: OutboxEvent,
        db: Session,
    ) -> None:

        payload_data = json.loads(event.payload)

        msg = IntegrationMessage(
            tenant_id=event.tenant_id,
            correlation_id=event.correlation_id,
            direction="OUTBOUND",
            target_system="mock-provider-system",
            payload=event.payload,
            status="IN_PROGRESS",
        )

        db.add(msg)
        db.flush()

        provider_payload = {
            "patient_identifier": f"SYNTH-PAT-{event.aggregate_id[:8]}",
            "hospital_id": payload_data.get("hospital_id"),
            "department_code": payload_data.get("service_code", "CARD-OPD"),
            "preferred_slot": datetime.now(timezone.utc).isoformat(),
            "reason": "Automated case dispatch from integration worker",
        }

        current_attempt_num = event.retry_count + 1

        status_code, response_text, is_success = (
            self.provider.dispatch_appointment(
                payload=provider_payload,
                correlation_id=event.correlation_id,
            )
        )

        self._handle_result(
            event=event,
            msg=msg,
            db=db,
            attempt_number=current_attempt_num,
            status_code=status_code,
            response_text=response_text,
            is_success=is_success,
        )

    def _process_analytics_event(
        self,
        event: OutboxEvent,
        db: Session,
    ) -> None:

        payload_data = json.loads(event.payload)

        msg = IntegrationMessage(
            tenant_id=event.tenant_id,
            correlation_id=event.correlation_id,
            direction="OUTBOUND",
            target_system="analytics-service",
            payload=event.payload,
            status="IN_PROGRESS",
        )

        db.add(msg)
        db.flush()

        analytics_payload = {
            "tenant_id": payload_data["tenant_id"],
            "case_reference_id": payload_data["case_id"],
            "hospital_id": payload_data["hospital_id"],
            "service_code": payload_data["service_code"],
            "status": "ACCEPTED",
            "case_created_at": payload_data["case_created_at"],
            "case_updated_at": payload_data["case_updated_at"],
        }

        current_attempt_num = event.retry_count + 1

        status_code, response_text, is_success = (
            self.analytics.record_case(
                payload=analytics_payload,
                correlation_id=event.correlation_id,
            )
        )

        self._handle_result(
            event=event,
            msg=msg,
            db=db,
            attempt_number=current_attempt_num,
            status_code=status_code,
            response_text=response_text,
            is_success=is_success,
        )

    def _handle_result(
        self,
        event: OutboxEvent,
        msg: IntegrationMessage,
        db: Session,
        attempt_number: int,
        status_code: int,
        response_text: str,
        is_success: bool,
    ) -> None:

        attempt = IntegrationAttempt(
            message_id=msg.id,
            attempt_number=attempt_number,
            response_status=status_code if status_code > 0 else None,
            response_body=response_text,
            error_message=(
                None
                if is_success
                else f"HTTP Status {status_code}: {response_text}"
            ),
        )

        db.add(attempt)

        if is_success:
            event.status = "PROCESSED"
            event.processed_at = datetime.now(timezone.utc)
            msg.status = "DELIVERED"

        else:
            event.retry_count += 1

            if event.retry_count >= self.max_retries:
                event.status = "DEAD_LETTER"
                msg.status = "FAILED"

                dlq = DeadLetterMessage(
                    tenant_id=event.tenant_id,
                    correlation_id=event.correlation_id,
                    original_payload=event.payload,
                    failure_reason=(
                        f"Exhausted retries. Last error: HTTP {status_code}"
                    ),
                    retry_count=event.retry_count,
                )

                db.add(dlq)

        db.commit()