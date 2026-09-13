from abc import ABC, abstractmethod
from typing import Optional

from app.models import HealthcareCaseFact


class CaseAnalyticsRepository(ABC):

    @abstractmethod
    def save(self, fact: HealthcareCaseFact) -> HealthcareCaseFact:
        pass

    @abstractmethod
    def get_by_case_reference_id(
        self,
        case_reference_id: str,
    ) -> Optional[HealthcareCaseFact]:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass