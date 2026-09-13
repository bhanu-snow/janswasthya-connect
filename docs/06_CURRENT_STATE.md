### JanSwasthya Connect — Current Implementation State
Updated: 2026-09-13

#### Current milestone
Phase 6 complete (Reliability: Transactional Outbox, Integration Worker, Bounded Retries, and Dead-Letter Queue). Ready for Phase 7 (Analytics Service & Persistence Portability).

#### Implemented
- Master Data Service (:8001) with organization hierarchy endpoints.
- Case Integration Service (:8002) with atomic outbox event enqueueing.
- Mock Provider System (:9000) for appointment and referral simulation.
- Integration Worker (background process) implementing:
  - Polling outbox processor.
  - ProviderAdapterPort (Ports and Adapters architecture).
  - MockProviderAdapter for HTTP integration.
  - Audit trails across integration_message and integration_attempt.
  - Bounded exponential retries and dead_letter_message routing.
- MariaDB 11.4 relational schema with full Alembic migration history.

#### Running services
- master-data-service :8001
- case-integration-service :8002
- mock-provider-system :9000
- integration-worker (worker process)
- mariadb :3306 (internal network)
- adminer :8080 (development UI)

#### ServiceNow status
- Instance: Not connected / unverified
- Scoped app: Pending
- Inbound REST API contract established: POST /api/v1/cases

#### Database status
- MariaDB version: 11.4
- Tables: alembic_version, hospital_group, hospital, facility, department, healthcare_service, case_reference, idempotency_record, outbox_event, integration_message, integration_attempt, dead_letter_message

#### API status
- Implemented endpoints:
  - GET :8001/health
  - GET :8001/api/v1/hospital-groups
  - GET :8001/api/v1/hospitals
  - GET :8001/api/v1/facilities
  - GET :8001/api/v1/services
  - GET :8002/health
  - POST :8002/api/v1/cases
  - GET :9000/health
  - POST / GET :9000/api/v1/appointments
  - POST / GET :9000/api/v1/referrals

#### Integration status
- ServiceNow -> FastAPI: Inbound case contract verified
- FastAPI -> MariaDB: Atomic case + outbox commit verified
- Worker -> Provider: HTTP adapter dispatch verified
- Retries & Dead Letter: Verified via unit and integration tests

#### Tests
- Result: Passing across master-data-service, case-integration-service, mock-provider-system, and integration-worker

#### Active ADRs
- ADR-001 (Service Boundaries) - Accepted
- ADR-006 (Hospital Group as Tenant Boundary) - Accepted
- ADR-008 (Outbox Pattern) - Accepted
- ADR-009 (Idempotency Strategy) - Accepted
- ADR-010 (Adapter Pattern for Provider Systems) - Accepted
