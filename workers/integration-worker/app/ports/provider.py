from typing import Protocol, Dict, Any, Tuple

class ProviderAdapterPort(Protocol):
    def dispatch_appointment(
        self,
        payload: Dict[str, Any],
        correlation_id: str
    ) -> Tuple[int, str, bool]:
        """
        Dispatches appointment request to provider system.
        Returns: (http_status, response_text, is_success)
        """
        ...