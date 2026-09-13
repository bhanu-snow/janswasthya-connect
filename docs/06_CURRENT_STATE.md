# JanSwasthya Connect — Current Implementation State

Updated: 2026-09-13

## Current Milestone

**Phase 7 in progress — Analytics Service & Persistence Portability**

## Phase 6 — Integration Reliability Foundation

**Status: Completed**

Completed:

- Case Integration Service implemented.
- ServiceNow-facing case ingestion endpoint implemented.
- Idempotency-Key handling implemented.
- Request payload hash validation implemented for idempotency-key reuse.
- Correlation ID propagation implemented.
- CaseReference persistence implemented.
- Outbox pattern implemented.
- Atomic CaseReference + OutboxEvent transaction implemented.
- IntegrationMessage audit record implemented.
- IntegrationAttempt audit record implemented.
- Dead-letter persistence implemented.
- Existing Integration Worker implemented under:
  `workers/integration-worker/`
- Mock Provider System implemented.
- Provider adapter boundary implemented.
- Bounded retry behavior implemented.
- Docker Compose runtime verified.
- MariaDB runtime verified.
- Master Data Service remains available on port `8001`.
- Case Integration Service available on port `8002`.
- Mock Provider System available on port `9000`.
- Analytics Service available on port `8003`.

## Phase 7 — Analytics Service

**Status: In progress**

### Analytics Service Foundation

Implemented:

- New service:
  `services/analytics-service/`
- FastAPI application.
- `/health` endpoint.
- Analytics API under:
  `/api/v1/analytics`
- MariaDB persistence.
- SQLAlchemy models.
- Independent Alembic migration setup.
- Independent analytics Alembic version table:
  `analytics_alembic_version`
- Analytics migration:
  `b8b6e31bf5a3_create_healthcare_case_fact`
- Analytics fact table:
  `healthcare_case_fact`

### Analytics Fact Model

Current fact captures:

- `tenant_id`
- `case_reference_id`
- `hospital_id`
- `service_code`
- `status`
- `case_created_at`
- `case_updated_at`
- `ingested_at`

`case_reference_id` is unique to prevent duplicate analytics facts.

### Persistence Portability

Implemented a repository/port boundary:

```text
Application Service
       |
       v
CaseAnalyticsRepository
       |
       v
MariaDBCaseAnalyticsRepository
       |
       v
MariaDB
```

The application layer does not directly depend on MariaDB-specific persistence behavior.

Future database adapters can be introduced without changing the analytics application service.

Potential future targets include PostgreSQL or an analytical database such as ClickHouse, but no migration is currently planned.

### Analytics API Behavior

The analytics service supports case fact creation.

If a fact already exists for the same `case_reference_id`:

- The existing fact is updated.
- The existing fact ID is preserved.
- This provides idempotent case ingestion behavior.

Unit tests cover:

- New fact creation.
- Existing fact update.
- ID preservation during update.

## Phase 7 — End-to-End Analytics Integration

**Status: Completed for the initial flow**

The existing integration worker is reused.

No second worker was introduced.

The case integration service now includes case timestamps in the outbox payload:

- `case_created_at`
- `case_updated_at`

Case creation now atomically produces two independent outbox events:

```text
CASE_ACCEPTED_FOR_DISPATCH
CASE_ACCEPTED_FOR_ANALYTICS
```

This intentionally separates downstream retry state.

### Current Flow

```text
ServiceNow
    |
    v
case-integration-service
    |
    +-- CaseReference
    |
    +-- OutboxEvent
          |
          +-- CASE_ACCEPTED_FOR_DISPATCH
          |
          +-- CASE_ACCEPTED_FOR_ANALYTICS
                         |
                         v
                 integration-worker
                    |         |
                    v         v
                 Provider   Analytics
                              |
                              v
                     healthcare_case_fact
```

### Analytics Adapter

The existing integration worker now contains an analytics adapter:

```text
workers/integration-worker/app/adapters/analytics.py
```

The adapter communicates with the Analytics Service over HTTP.

Configured service endpoint:

```text
http://analytics-service:8003
```

Analytics endpoint:

```text
POST /api/v1/analytics/cases
```

Correlation ID is propagated to the Analytics Service.

### Independent Reliability Semantics

Provider delivery and analytics ingestion use separate outbox events.

This avoids coupling their retry state.

For example:

```text
Provider succeeds
Analytics fails
```

The provider event remains processed while the analytics event can retry independently.

This prevents a successful provider operation from being repeated solely because analytics processing failed.

## End-to-End Verification

A synthetic case was successfully processed:

```text
Case Number:
CS-ANALYTICS-003

Hospital:
Sunrise Hospital Kanpur

Service:
CARD-OPD

Status:
ACCEPTED

Correlation ID:
corr-analytics-test-003
```

Observed outbox state:

```text
CASE_ACCEPTED_FOR_ANALYTICS
    PROCESSED
    retry_count = 0

CASE_ACCEPTED_FOR_DISPATCH
    PROCESSED
    retry_count = 0
```

Observed analytics fact:

```text
tenant_id:
830f21a0-3285-4697-b570-ccb0bdf33191

case_reference_id:
7587fa33-8dbe-4f03-8ad2-08eaeb2a7820

hospital_id:
3abf0419-1f03-4c98-8f2e-012a581e7497

service_code:
CARD-OPD

status:
ACCEPTED
```

Therefore the following flow has been verified:

```text
Case API
    |
    v
CaseReference
    |
    v
Atomic Outbox
    |
    +-------------------------+
    |                         |
    v                         v
Provider Event          Analytics Event
    |                         |
    v                         v
Integration Worker      Integration Worker
    |                         |
    v                         v
Mock Provider           Analytics Service
                              |
                              v
                     healthcare_case_fact
```

## Current Docker Runtime

Current Compose services:

```text
mariadb
mock-provider-system
integration-worker
master-data-service
adminer
analytics-service
case-integration-service
```

Current exposed application ports:

```text
Master Data Service       :8001
Case Integration Service  :8002
Analytics Service        :8003
Mock Provider System      :9000
Adminer                   :8080
```

MariaDB port `3306` remains internal to the Docker network.

## Important Architecture Decisions

### Shared MariaDB

A shared MariaDB instance is intentionally used for the current MVP.

This is a learning-oriented simplification.

The services maintain logical ownership boundaries even though they currently share the same database instance.

A future experiment may evaluate database-per-service separation.

### Analytics Database Portability

Analytics persistence is accessed through a repository port.

Current:

```text
CaseAnalyticsRepository
        |
        v
MariaDBCaseAnalyticsRepository
```

Future:

```text
CaseAnalyticsRepository
        |
        +-- MariaDB adapter
        +-- PostgreSQL adapter
        +-- ClickHouse adapter
```

Portability does not imply zero migration effort.

### Existing Integration Worker

The existing:

```text
workers/integration-worker/
```

is reused for asynchronous downstream processing.

A separate analytics worker is intentionally not introduced.

### Outbox Fan-Out

Case creation produces independent downstream events.

Current events:

```text
CASE_ACCEPTED_FOR_DISPATCH
CASE_ACCEPTED_FOR_ANALYTICS
```

This allows independent:

- retry counters
- processing status
- integration messages
- integration attempts
- dead-letter handling

### MCP Direction

MCP is not yet implemented.

The intended future boundary is:

```text
LLM / Agent
      |
      v
MCP Server
      |
      v
Application Services
      |
      v
Authorization
      |
      v
Domain
      |
      v
Repositories / External Adapters
```

MCP must not:

- access MariaDB directly
- bypass authorization
- duplicate business logic
- replace the REST API

MCP will be considered only after the core REST/application capabilities are stable.

## Remaining Phase 7 Work

### Reliability Testing

Still required:

- Analytics HTTP 500 failure.
- Analytics timeout.
- Analytics service unavailable.
- Bounded retry verification.
- Retry counter verification.
- Dead-letter verification after retry exhaustion.
- Recovery after Analytics Service becomes available.
- Safe replay verification.
- Duplicate analytics event verification.
- Correlation ID traceability.
- IntegrationAttempt audit verification.

### Automated Tests

Strengthen automated tests for:

- Analytics event dispatch.
- Analytics success.
- Analytics transient failure.
- Retry behavior.
- Dead-letter behavior.
- Unknown event type behavior.
- Provider and analytics event independence.

### Analytics

Still required:

- Analytics aggregate queries.
- Dashboard-facing read APIs.
- Reconciliation capability.
- Delayed/missing event detection.
- ServiceNow analytics synchronization.

## ServiceNow Integration

ServiceNow is not yet connected to a verified external instance.

Current integration boundary:

```text
ServiceNow
    |
    | REST / HTTPS
    v
case-integration-service
```

Planned:

- ServiceNow scoped application.
- REST contract implementation.
- OAuth 2.0 / least-privilege authentication.
- Correlation ID propagation.
- ServiceNow case lifecycle synchronization.
- Integration contract validation.
- ServiceNow dashboard integration.

ServiceNow-specific table names, fields, plugins, licensing, and release-specific behavior must be verified against the target instance before implementation.

## Tenant Model

Primary tenant:

```text
Hospital Group
```

Hierarchy:

```text
Hospital Group
    |
    +-- Hospital
          |
          +-- Facility
                |
                +-- Department
                      |
                      +-- Healthcare Service
```

Current database relationship verified:

```text
hospital.hospital_group_id
        |
        v
hospital_group.id
```

The API must not blindly trust a client-supplied tenant identifier.

Tenant context should ultimately be derived from authenticated identity and server-side authorization context.

Tenant isolation remains a required security concern before exposing analytics capabilities externally.

## Reliability Model

Current reliability architecture:

```text
Business Transaction
      |
      +-- Business State
      |
      +-- Outbox Event
             |
             v
       Integration Worker
             |
             v
       External Adapter
             |
       +-----+-----+
       |           |
    Success      Failure
       |           |
   PROCESSED     Retry
                   |
              Max Retries
                   |
                   v
              DEAD_LETTER
```

The architecture uses:

- Idempotency
- Correlation IDs
- Atomic outbox writes
- Bounded retries
- Integration audit records
- Dead-letter persistence
- Safe replay as a future operational capability

## Known Test-Data Lessons

Synthetic `servicenow_sys_id` values must conform to the existing database representation.

The current schema rejected a generated UUID because the `servicenow_sys_id` column is shorter than 36 characters.

For testing, use a 32-character ServiceNow-style hexadecimal `sys_id`.

Synthetic hospital IDs must reference actual rows in the `hospital` table because `case_reference.hospital_id` has a foreign-key constraint.

Do not bypass referential integrity merely to simplify tests.

## Next Major Steps

1. Complete analytics reliability and retry testing.
2. Verify dead-letter and replay behavior.
3. Add automated worker integration tests.
4. Add analytics aggregation and reconciliation.
5. Connect the verified ServiceNow instance.
6. Implement ServiceNow synchronization.
7. Harden tenant authorization.
8. Define MCP tools over stable application capabilities.
9. Add MCP integration tests and authorization checks.
10. Complete architecture decision records.
11. Complete security/threat-model documentation.
12. Prepare portfolio-quality architecture and implementation documentation.

## Current Definition of Done

The current milestone is considered complete when:

- Case events reach analytics facts.
- Provider and analytics processing have independent retry state.
- Duplicate analytics events do not create duplicate facts.
- Failed analytics events are retried.
- Exhausted analytics events enter dead-letter state.
- Recovered analytics events can be replayed safely.
- Correlation IDs are traceable.
- Analytics reconciliation is implemented.
- Tenant authorization is enforced.
- ServiceNow integration is verified against the target instance.
- Architecture decisions are documented.

## Current Status Summary

```text
Foundation                         COMPLETE
Master Data Service                COMPLETE
Case Integration Service           COMPLETE
Outbox Reliability Foundation      COMPLETE
Mock Provider Integration          COMPLETE
Analytics Service                  COMPLETE
Analytics Persistence Port         COMPLETE
Analytics End-to-End Flow          COMPLETE
Analytics Reliability Testing      NEXT
Analytics Reconciliation           NEXT
ServiceNow Integration             PENDING
Tenant Authorization Hardening     PENDING
MCP Server                         FUTURE
Architecture Documentation         IN PROGRESS
```
