from datetime import datetime
from uuid import UUID

from app.models import HealthcareCaseFact
from app.repositories.case_analytics import CaseAnalyticsRepository


class AnalyticsService:

    def __init__(self, repository: CaseAnalyticsRepository):
        self.repository = repository

    def record_case(
        self,
        tenant_id: UUID,
        case_reference_id: UUID,
        hospital_id: UUID,
        service_code: str,
        status: str,
        case_created_at: datetime,
        case_updated_at: datetime,
    ) -> HealthcareCaseFact:

        existing = self.repository.get_by_case_reference_id(
            str(case_reference_id)
        )

        if existing:
            existing.status = status
            existing.case_updated_at = case_updated_at
            self.repository.commit()
            return existing

        fact = HealthcareCaseFact(
            tenant_id=str(tenant_id),
            case_reference_id=str(case_reference_id),
            hospital_id=str(hospital_id),
            service_code=service_code,
            status=status,
            case_created_at=case_created_at,
            case_updated_at=case_updated_at,
        )

        result = self.repository.save(fact)
        self.repository.commit()

        return result