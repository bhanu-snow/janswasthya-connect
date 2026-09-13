### JanSwasthya Connect — Current Implementation State

Updated: 2026-09-13

#### Current milestone
Phase 7 in progress — Analytics Service & Persistence Portability.

#### Phase 6 — Completed
- Master Data Service (:8001).
- Case Integration Service (:8002).
- Mock Provider System (:9000).
- Integration Worker under `workers/integration-worker/`.
- Transactional Outbox.
- Bounded retries.
- Dead-letter routing.
- Integration audit trail.
- ProviderAdapterPort + MockProviderAdapter.
- MariaDB 11.4 with Alembic migrations.
- Phase 6 tests passing.

#### Phase 7 — Completed so far
- Created `services/analytics-service/`.
- Analytics REST API on :8003.
- `healthcare_case_fact` analytics table.
- Independent analytics Alembic version table: `analytics_alembic_version`.
- Analytics migration: `b8b6e31bf5a3_create_healthcare_case_fact`.
- CaseAnalyticsRepository port.
- MariaDBCaseAnalyticsRepository adapter.
- AnalyticsService application layer.
- Create/update behavior for an existing `case_reference_id`.
- Analytics unit tests passing.
- Analytics container added to Docker Compose.
- Analytics `/health` verified.
- Analytics case ingestion API verified against MariaDB.
- Repeated ingestion of the same `case_reference_id` preserves the existing fact and updates its status/timestamp.

#### Phase 7 — Not completed yet
- Existing `workers/integration-worker/` has NOT yet been modified for analytics.
- Existing outbox ? integration-worker flow has NOT yet been connected to analytics.
- End-to-end Case ? Outbox ? Worker ? Analytics verification is pending.
- Analytics persistence-portability ADR/documentation is pending.

#### Running services
- master-data-service :8001
- case-integration-service :8002
- analytics-service :8003
- mock-provider-system :9000
- integration-worker under `workers/integration-worker/`
- mariadb :3306
- adminer :8080

#### ServiceNow status
- Instance: Not connected / unverified.
- Scoped app: Pending.
- Inbound REST API contract: `POST /api/v1/cases`.

#### Important architecture decisions
- Hospital Group is the tenant boundary.
- ServiceNow remains the operational case system of record.
- FastAPI is the controlled integration boundary.
- Transactional Outbox is used for reliable asynchronous processing.
- Analytics is a separate service boundary.
- Analytics persistence is accessed through a repository port so the application layer is not coupled to MariaDB.
- Analytics currently uses MariaDB; future PostgreSQL/ClickHouse/etc. adapters remain possible.
- Existing `workers/integration-worker/` will be reused; no second worker will be created.

#### Current next step
Inspect the actual existing `workers/integration-worker/` outbox processing implementation and connect the existing flow to `analytics-service` without duplicating the worker or inventing a new event flow.
