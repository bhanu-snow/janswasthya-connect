from typing import Dict, Any, Tuple
import httpx


class AnalyticsAdapter:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def record_case(
        self,
        payload: Dict[str, Any],
        correlation_id: str
    ) -> Tuple[int, str, bool]:

        url = f"{self.base_url}/api/v1/analytics/cases"

        headers = {
            "X-Correlation-ID": correlation_id,
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.post(
                    url,
                    json=payload,
                    headers=headers
                )

                return (
                    response.status_code,
                    response.text,
                    response.is_success
                )

        except Exception as exc:
            return 0, str(exc), False