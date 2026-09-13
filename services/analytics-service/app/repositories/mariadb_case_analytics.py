from typing import Optional

from sqlalchemy.orm import Session

from app.models import HealthcareCaseFact
from app.repositories.case_analytics import CaseAnalyticsRepository


class MariaDBCaseAnalyticsRepository(CaseAnalyticsRepository):

    def __init__(self, session: Session):
        self.session = session

    def save(self, fact: HealthcareCaseFact) -> HealthcareCaseFact:
        self.session.add(fact)
        self.session.flush()
        self.session.refresh(fact)
        return fact

    def get_by_case_reference_id(
        self,
        case_reference_id: str,
    ) -> Optional[HealthcareCaseFact]:
        return (
            self.session.query(HealthcareCaseFact)
            .filter(
                HealthcareCaseFact.case_reference_id == case_reference_id
            )
            .first()
        )

    def commit(self) -> None:
        self.session.commit()