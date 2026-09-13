### JanSwasthya Connect — Current Implementation State
Updated: 2026-09-13

#### Current milestone
Phase 3 complete (Master Data API & Organization Hierarchy Seeded). Ready for Phase 4 (ServiceNow Integration & Case Ingestion).

#### Implemented
- Docker Compose baseline with MariaDB 11.4 and FastAPI.
- Relational hierarchy models with Alembic migrations:
  hospital_group -> hospital -> facility -> department -> healthcare_service.
- Synthetic seed data for Sunrise Healthcare Group and Apollo Healthcare Group.
- Versioned master data endpoints:
  - GET /health
  - GET /api/v1/hospital-groups
  - GET /api/v1/hospitals (supports tenant_id filtering)
  - GET /api/v1/facilities (supports hospital_id filtering)
  - GET /api/v1/services (supports department_id filtering)

#### Running services
- master-data-service :8001
- mariadb :3306 (internal network)
- adminer :8080 (development UI)

#### ServiceNow status
- Instance: Not connected / unverified
- Scoped app: Pending Phase 4
- Inbound OAuth / REST integration: Pending Phase 4

#### Database status
- MariaDB version: 11.4
- Implemented migrations: alembic revision (create organization hierarchy tables)
- Tables: alembic_version, hospital_group, hospital, facility, department, healthcare_service

#### API status
- Implemented endpoints: /health, /api/v1/hospital-groups, /api/v1/hospitals, /api/v1/facilities, /api/v1/services
- OpenAPI location: http://localhost:8001/docs

#### Integration status
- ServiceNow -> FastAPI: Pending
- FastAPI -> ServiceNow: Pending
- FastAPI -> Provider: Pending
- Outbox / Retry / Dead letter: Pending (Phase 6)
- Idempotency: Pending (Phase 6)

#### Tests
- Last test command: docker compose exec master-data-service pytest -v
- Result: Passing

#### Known issues
None.

#### Open questions
- ServiceNow PDI (Personal Developer Instance) release version and inbound OAuth client configuration.

#### Active ADRs
- ADR-001 (Service Boundaries) - Draft/Pending
- ADR-006 (Hospital Group as Tenant Boundary) - Accepted
