### JanSwasthya Connect — Current Implementation State
Updated: 2026-09-13

#### Current milestone
Phase 4 complete (Inbound Case Ingestion API with Idempotency). Ready for Phase 5 (Mock Provider System).

#### Implemented
- Master Data Service (:8001) with organization hierarchy endpoints.
- Relational schema with migrations: hospital_group, hospital, facility, department, healthcare_service, case_reference, idempotency_record.
- Case Integration Service (:8002) with inbound POST /api/v1/cases.
- Header-based Idempotency (Idempotency-Key) and SHA-256 payload validation.
- Correlation ID propagation (X-Correlation-ID).

#### Running services
- master-data-service :8001
- case-integration-service :8002
- mariadb :3306 (internal network)
- adminer :8080 (development UI)

#### ServiceNow status
- Instance: Not connected / unverified
- Scoped app: Pending
- Inbound REST API contract established: POST /api/v1/cases

#### Database status
- MariaDB version: 11.4
- Tables: alembic_version, hospital_group, hospital, facility, department, healthcare_service, case_reference, idempotency_record

#### API status
- Endpoints:
  - GET :8001/health
  - GET :8001/api/v1/hospital-groups
  - GET :8001/api/v1/hospitals
  - GET :8001/api/v1/facilities
  - GET :8001/api/v1/services
  - GET :8002/health
  - POST :8002/api/v1/cases

#### Integration status
- ServiceNow -> FastAPI: Contract implemented (Inbound case ingestion)
- FastAPI -> Provider: Pending (Phase 5)
- Outbox / Retry / Dead letter: Pending (Phase 6)
- Idempotency: Implemented and verified

#### Tests
- Result: Passing (tests/test_health.py, tests/test_master_data.py, tests/test_case_ingestion.py)

#### Active ADRs
- ADR-001 (Service Boundaries) - Accepted
- ADR-006 (Hospital Group as Tenant Boundary) - Accepted
- ADR-009 (Idempotency Strategy) - Accepted
