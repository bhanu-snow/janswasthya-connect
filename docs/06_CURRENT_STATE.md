### JanSwasthya Connect — Current Implementation State
Updated: 2026-09-13

#### Current milestone
Phase 5 complete (Mock Provider System Implemented). Ready for Phase 6 (Reliability: Outbox, Worker, Retry, and Dead-Letter Queue).

#### Implemented
- Master Data Service (:8001) with organization hierarchy endpoints.
- Relational schema with migrations: hospital_group, hospital, facility, department, healthcare_service, case_reference, idempotency_record.
- Case Integration Service (:8002) with inbound POST /api/v1/cases and idempotency enforcement.
- Mock Provider System (:9000) providing:
  - POST /api/v1/appointments and GET /api/v1/appointments/{id}
  - POST /api/v1/referrals and GET /api/v1/referrals/{id}
  - Failure mode simulations via headers: X-Simulate-Mode (400, 404, 409, 500) and X-Simulate-Delay-Sec.

#### Running services
- master-data-service :8001
- case-integration-service :8002
- mock-provider-system :9000
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
  - GET :9000/health
  - POST / GET :9000/api/v1/appointments
  - POST / GET :9000/api/v1/referrals

#### Integration status
- ServiceNow -> FastAPI: Inbound case contract verified
- FastAPI -> Provider: Mock provider verified with error-mode simulation
- Outbox / Retry / Dead letter: Pending (Phase 6)
- Idempotency: Verified

#### Tests
- Result: Passing across master-data-service, case-integration-service, and mock-provider-system

#### Active ADRs
- ADR-001 (Service Boundaries) - Accepted
- ADR-006 (Hospital Group as Tenant Boundary) - Accepted
- ADR-009 (Idempotency Strategy) - Accepted
- ADR-010 (Adapter Pattern for Provider Systems) - Accepted
