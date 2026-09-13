import json
from unittest.mock import MagicMock
import pytest
from app.services.dispatcher import OutboxDispatcher
from app.models import OutboxEvent

def test_dispatcher_success():
    mock_adapter = MagicMock()
    mock_adapter.dispatch_appointment.return_value = (201, '{"status": "CONFIRMED"}', True)

    dispatcher = OutboxDispatcher(provider_adapter=mock_adapter, max_retries=3)

    db = MagicMock()
    event = OutboxEvent(
        id="evt-1",
        tenant_id="t-1",
        aggregate_id="agg-1",
        correlation_id="corr-1",
        payload=json.dumps({"hospital_id": "h-1", "service_code": "CARD-OPD"}),
        status="PENDING",
        retry_count=0
    )

    dispatcher.process_event(event, db)

    assert event.status == "PROCESSED"
    assert db.commit.called

def test_dispatcher_exhausted_retries_routes_to_dlq():
    mock_adapter = MagicMock()
    mock_adapter.dispatch_appointment.return_value = (500, "Internal Server Error", False)

    dispatcher = OutboxDispatcher(provider_adapter=mock_adapter, max_retries=3)

    db = MagicMock()
    event = OutboxEvent(
        id="evt-2",
        tenant_id="t-1",
        aggregate_id="agg-2",
        correlation_id="corr-2",
        payload=json.dumps({"hospital_id": "h-1"}),
        status="PENDING",
        retry_count=2  # Third attempt will fail and exhaust
    )

    dispatcher.process_event(event, db)

    assert event.status == "DEAD_LETTER"
    assert event.retry_count == 3
    assert db.commit.called