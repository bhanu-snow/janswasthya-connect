from typing import Dict, Any, Tuple
import httpx
from app.ports.provider import ProviderAdapterPort

class MockProviderAdapter:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def dispatch_appointment(
        self,
        payload: Dict[str, Any],
        correlation_id: str
    ) -> Tuple[int, str, bool]:
        url = f"{self.base_url}/api/v1/appointments"
        headers = {
            "X-Correlation-ID": correlation_id,
            "Content-Type": "application/json"
        }
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(url, json=payload, headers=headers)
                return res.status_code, res.text, res.is_success
        except Exception as e:
            return 0, str(e), False