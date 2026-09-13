from datetime import datetime, timezone
from uuid import uuid4

from app.models import HealthcareCaseFact
from app.services import AnalyticsService


class FakeRepository:

    def __init__(self):
        self.facts = {}
        self.committed = False

    def save(self, fact):
        self.facts[fact.case_reference_id] = fact
        return fact

    def get_by_case_reference_id(self, case_reference_id):
        return self.facts.get(case_reference_id)

    def commit(self):
        self.committed = True


def test_record_case_creates_fact():
    repository = FakeRepository()
    service = AnalyticsService(repository)

    tenant_id = uuid4()
    case_reference_id = uuid4()
    hospital_id = uuid4()
    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)

    fact = service.record_case(
        tenant_id=tenant_id,
        case_reference_id=case_reference_id,
        hospital_id=hospital_id,
        service_code="CARDIOLOGY",
        status="OPEN",
        case_created_at=created_at,
        case_updated_at=updated_at,
    )

    assert isinstance(fact, HealthcareCaseFact)
    assert fact.case_reference_id == str(case_reference_id)
    assert fact.status == "OPEN"
    assert repository.committed is True


def test_record_case_updates_existing_fact():
    repository = FakeRepository()
    service = AnalyticsService(repository)

    tenant_id = uuid4()
    case_reference_id = uuid4()
    hospital_id = uuid4()
    created_at = datetime.now(timezone.utc)

    first = service.record_case(
        tenant_id=tenant_id,
        case_reference_id=case_reference_id,
        hospital_id=hospital_id,
        service_code="CARDIOLOGY",
        status="OPEN",
        case_created_at=created_at,
        case_updated_at=created_at,
    )

    updated_at = datetime.now(timezone.utc)

    second = service.record_case(
        tenant_id=tenant_id,
        case_reference_id=case_reference_id,
        hospital_id=hospital_id,
        service_code="CARDIOLOGY",
        status="CLOSED",
        case_created_at=created_at,
        case_updated_at=updated_at,
    )

    assert second.id == first.id
    assert second.status == "CLOSED"
    assert second.case_updated_at == updated_at
    assert len(repository.facts) == 1