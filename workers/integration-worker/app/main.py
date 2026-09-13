import time
from app.config import PROVIDER_BASE_URL, POLL_INTERVAL_SECONDS
from app.database import SessionLocal
from app.adapters.mock_provider import MockProviderAdapter
from app.services.dispatcher import OutboxDispatcher
from app.models import OutboxEvent

def run_worker():
    adapter = MockProviderAdapter(base_url=PROVIDER_BASE_URL)
    dispatcher = OutboxDispatcher(provider_adapter=adapter)
    
    print("[Worker] Integration Worker started. Polling outbox_event...")
    while True:
        db = SessionLocal()
        try:
            pending_events = db.query(OutboxEvent).filter(
                OutboxEvent.status == "PENDING"
            ).limit(10).all()

            for event in pending_events:
                dispatcher.process_event(event, db)
        except Exception as err:
            print(f"[Worker] Polling loop error: {err}")
        finally:
            db.close()
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_worker()