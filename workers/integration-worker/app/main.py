import time

from app.config import (
    PROVIDER_BASE_URL,
    ANALYTICS_SERVICE_URL,
    POLL_INTERVAL_SECONDS,
)
from app.database import SessionLocal
from app.adapters.mock_provider import MockProviderAdapter
from app.adapters.analytics import AnalyticsAdapter
from app.services.dispatcher import OutboxDispatcher
from app.models import OutboxEvent


def run_worker():
    provider_adapter = MockProviderAdapter(
        base_url=PROVIDER_BASE_URL
    )

    analytics_adapter = AnalyticsAdapter(
        base_url=ANALYTICS_SERVICE_URL
    )

    dispatcher = OutboxDispatcher(
        provider_adapter=provider_adapter,
        analytics_adapter=analytics_adapter,
    )

    print("[Worker] Integration Worker started. Polling outbox_event...")

    while True:
        db = SessionLocal()

        try:
            pending_events = (
                db.query(OutboxEvent)
                .filter(OutboxEvent.status == "PENDING")
                .limit(10)
                .all()
            )

            for event in pending_events:
                dispatcher.process_event(event, db)

        except Exception as err:
            print(f"[Worker] Polling loop error: {err}")

        finally:
            db.close()

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_worker()