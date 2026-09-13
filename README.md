# JanSwasthya Connect

Production-style healthcare integration and analytics platform built as a focused MVP for learning and demonstrating Solution Architecture, integration reliability, persistence portability, and AI/MCP readiness.

## Current Status

**Phase 7 — Analytics Service & Persistence Portability**

The core healthcare case-ingestion and integration foundation is implemented. Analytics is now integrated into the existing asynchronous outbox/worker flow and has been verified end-to-end.

The immediate next step is to finish analytics reliability testing and then move quickly to the ServiceNow implementation.

## Architecture

```text
                         ServiceNow
                             |
                         REST / HTTPS
                             |
                             v
                 case-integration-service
                             |
                    Atomic Transaction
                             |
              +--------------+--------------+
              |                             |
              v                             v
        CaseReference                  Outbox Events
                                            |
                         +------------------+------------------+
                         |                                     |
                         v                                     v
             CASE_ACCEPTED_FOR_DISPATCH          CASE_ACCEPTED_FOR_ANALYTICS
                         |                                     |
                         +------------------+------------------+
                                            |
                                            v
                                  integration-worker
                                      |         |
                                      v         v
                              Mock Provider   Analytics
                                                Service
                                                   |
                                                   v
                                         healthcare_case_fact
```

## Domain / Tenant Model

The primary tenant is the **Hospital Group**.

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

Tenant context is intended to be derived from authenticated identity and server-side authorization rather than blindly trusting a client-supplied `tenant_id`.

## Services

### Master Data Service

Location:

```text
services/master-data-service/
```

Current responsibility:

- Hospital Group
- Hospital
- Facility
- Department
- Healthcare Service

Runtime port:

```text
8001
```

### Case Integration Service

Location:

```text
services/case-integration-service/
```

Current responsibility:

- Receive healthcare case requests.
- Validate requests.
- Enforce idempotency.
- Generate/propagate correlation IDs.
- Persist `CaseReference`.
- Create reliable outbox events.
- Maintain the transactional boundary between business state and outbox state.

Runtime port:

```text
8002
```

Current endpoint:

```text
POST /api/v1/cases
```

The request requires:

```text
Idempotency-Key
```

An optional:

```text
X-Correlation-ID
```

can be supplied and is propagated through downstream processing.

### Analytics Service

Location:

```text
services/analytics-service/
```

Current responsibility:

- Receive analytics case facts.
- Persist healthcare case facts.
- Provide a persistence port for future database portability.
- Support idempotent create/update behavior by `case_reference_id`.

Runtime port:

```text
8003
```

Health endpoint:

```text
GET /health
```

Analytics endpoint:

```text
POST /api/v1/analytics/cases
```

Primary table:

```text
healthcare_case_fact
```

### Integration Worker

Location:

```text
workers/integration-worker/
```

The existing worker is reused for downstream integrations.

It currently processes:

```text
CASE_ACCEPTED_FOR_DISPATCH
CASE_ACCEPTED_FOR_ANALYTICS
```

The worker routes each event to its appropriate adapter.

Current adapters:

```text
workers/integration-worker/app/adapters/mock_provider.py
workers/integration-worker/app/adapters/analytics.py
```

### Mock Provider System

Location:

```text
services/mock-provider-system/
```

Used to simulate an external healthcare provider system and exercise the integration boundary.

Runtime port:

```text
9000
```

Current provider integration includes appointment dispatch.

## Analytics Persistence Architecture

Analytics persistence uses a repository/port boundary.

```text
AnalyticsService
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

The application service does not directly depend on MariaDB-specific persistence implementation.

The current database is MariaDB.

Future adapters may target PostgreSQL or an analytical database such as ClickHouse if justified.

Portability means the application boundary is prepared for another persistence implementation; it does not imply a zero-effort database migration.

## Analytics Fact

Current `healthcare_case_fact` fields:

```text
id
tenant_id
case_reference_id
hospital_id
service_code
status
case_created_at
case_updated_at
ingested_at
```

`case_reference_id` is unique.

When the same case is received again:

- The existing analytics fact is located.
- Its status and update timestamp are updated.
- Its fact ID is preserved.

This provides idempotent analytics ingestion behavior.

## Reliability Architecture

The integration foundation uses:

- Idempotency
- Correlation IDs
- Atomic outbox writes
- Integration message auditing
- Integration attempt auditing
- Bounded retries
- Dead-letter persistence
- Independent downstream event state

The case transaction creates independent events:

```text
CASE_ACCEPTED_FOR_DISPATCH
CASE_ACCEPTED_FOR_ANALYTICS
```

This is deliberate.

If provider delivery succeeds but analytics fails:

```text
Provider Event       -> PROCESSED
Analytics Event      -> RETRY / DEAD_LETTER
```

The provider operation does not need to be repeated merely because analytics processing failed.

## Current Database

The MVP currently uses a shared MariaDB instance.

This is an intentional simplification for the current learning and implementation stage.

Logical service boundaries are maintained even though services currently share the database instance.

A future database-per-service experiment can be evaluated separately.

## Database Migrations

Operational services use the existing Alembic migration history.

Actual current operational migration history includes:

```text
2a5d2593a683  create_master_data_tables
f7629d3baf9f  add_case_reference_and_idempotency
0e943d03e523  add_outbox_and_reliability_tables
```

Analytics has an independent Alembic version table:

```text
analytics_alembic_version
```

Analytics migration:

```text
b8b6e31bf5a3_create_healthcare_case_fact
```

This prevents the analytics migration process from attempting to manage operational tables in the shared database.

## Docker Compose

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

Application ports:

```text
Master Data Service       :8001
Case Integration Service  :8002
Analytics Service        :8003
Mock Provider System      :9000
Adminer                   :8080
```

MariaDB remains internal to the Docker network.

## End-to-End Verification

A synthetic case has been successfully processed through the analytics path.

Example:

```text
Case:
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

Verified:

```text
CASE_ACCEPTED_FOR_DISPATCH
    -> PROCESSED
    -> retry_count = 0

CASE_ACCEPTED_FOR_ANALYTICS
    -> PROCESSED
    -> retry_count = 0
```

The corresponding `healthcare_case_fact` was successfully created.

Therefore the current verified path is:

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

## Testing

Analytics service tests currently cover:

- Health endpoint.
- New analytics fact creation.
- Existing analytics fact update.
- Fact ID preservation during update.

Runtime verification has also confirmed:

- Analytics service starts successfully.
- Analytics health endpoint responds.
- Analytics API accepts case facts.
- Duplicate case ingestion updates the existing fact.
- Worker can reach the analytics service over the Docker network.
- Case integration creates both provider and analytics outbox events.
- Both events can be processed successfully.

## Current Limitations

The following are intentionally not complete yet:

- Full analytics failure/retry testing.
- Timeout/unavailability testing.
- Dead-letter replay testing.
- Automated worker integration tests.
- Analytics reconciliation.
- ServiceNow external-instance integration.
- Full tenant authorization enforcement.
- MCP server.
- Production authentication/authorization hardening.
- Production observability stack.

The current worker retry mechanism is bounded, but exponential backoff has not yet been fully implemented. This remains part of reliability hardening rather than being treated as complete.

## ServiceNow Direction

ServiceNow is intended to remain the operational case system of record.

Target architecture:

```text
ServiceNow
    |
    | REST / HTTPS
    v
case-integration-service
    |
    v
Application / Domain Logic
    |
    +-- MariaDB
    |
    +-- Outbox
```

The integration should use:

- REST/HTTPS.
- OAuth 2.0 where supported by the target deployment.
- Least-privilege access.
- Explicit API contracts.
- Correlation IDs.
- Idempotency.
- Timeouts.
- Schema validation.
- Controlled retries.

ServiceNow-specific table names, fields, plugins, licensing, and release-specific behavior will be verified against the actual target instance before implementation.

## MCP Direction

MCP is a future application-facing boundary.

Target architecture:

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

MCP will not:

- Access MariaDB directly.
- Bypass authorization.
- Duplicate business logic.
- Replace REST APIs.

Initial candidate read capabilities include:

```text
search_hospitals
get_hospital
list_healthcare_services
get_case_status
check_appointment_status
get_referral_status
get_document_request_status
```

MCP implementation will follow stabilization of the REST and application boundaries.

## Architecture Style

The project follows a pragmatic Hexagonal / Ports-and-Adapters approach:

```text
API
 |
 v
Application Service
 |
 v
Domain
 |
 v
Port
 |
 v
Infrastructure Adapter
```

The goal is to maintain useful architectural boundaries without introducing unnecessary abstraction.

Current examples include:

- Repository ports.
- Provider adapter ports.
- HTTP integration adapters.
- Application services.
- Pydantic API DTOs.
- Outbox-based asynchronous integration.

## Project Structure

High-level structure:

```text
janswasthya-connect/
|
+-- services/
|   +-- master-data-service/
|   +-- case-integration-service/
|   +-- analytics-service/
|   +-- mock-provider-system/
|
+-- workers/
|   +-- integration-worker/
|
+-- docs/
|   +-- 06_CURRENT_STATE.md
|
+-- docker-compose.yml
|
+-- README.md
```

## Immediate Next Steps

The implementation priority is intentionally short and execution-focused.

### 1. Finalize Analytics

Complete:

- Analytics HTTP 500 test.
- Analytics timeout/unavailability test.
- Retry behavior verification.
- Dead-letter behavior.
- Recovery and replay.
- Correlation/audit verification.
- Worker automated tests.
- Confirm current retry/backoff behavior and improve it where required.
- Update current-state documentation.
- Commit and push a clean analytics checkpoint.

### 2. Move Quickly to ServiceNow

After the analytics checkpoint:

- Verify the target ServiceNow instance.
- Define the inbound/outbound contract.
- Confirm authentication mechanism.
- Create/configure the required ServiceNow application boundary.
- Implement the REST integration.
- Map ServiceNow case data to the existing case model.
- Preserve idempotency and correlation semantics.
- Test ServiceNow -> Case Integration Service.
- Test case lifecycle synchronization.
- Add failure/retry handling around the real integration.

### 3. Analytics / Reconciliation

After ServiceNow integration:

- Define analytics read models.
- Add aggregate queries.
- Add reconciliation between operational case state and analytics facts.
- Identify missing, delayed, or failed analytics events.

### 4. MCP

Only after the core application capabilities are stable:

- Define MCP server boundary.
- Define tool contracts.
- Add authorization.
- Expose selected application capabilities.
- Test tenant isolation and failure behavior.

## Current Status

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
ServiceNow Integration             NEXT
Tenant Authorization Hardening     PENDING
MCP Server                         FUTURE
Architecture Documentation         IN PROGRESS
```

## Definition of Done for Current Milestone

The analytics milestone will be considered complete when:

- Case events reach analytics facts.
- Duplicate analytics events do not create duplicate facts.
- Provider and analytics processing have independent retry state.
- Analytics failures are retried.
- Retry exhaustion creates a dead-letter record.
- Recovered analytics events can be replayed safely.
- Correlation IDs are traceable.
- Integration attempts are auditable.
- Automated worker tests cover the analytics path.
- Analytics behavior is documented.

Once this checkpoint is complete, implementation priority moves directly to the ServiceNow integration.
