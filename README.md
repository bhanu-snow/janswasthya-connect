# JanSwasthya Connect

**JanSwasthya Connect** is a production-style healthcare integration and
analytics MVP built to demonstrate practical Solution Architecture:
domain boundaries, multi-tenant modelling, REST integration,
transactional outbox, asynchronous workers, idempotency, correlation,
retries/DLQ, analytics persistence portability, and future MCP
readiness.

> **Current checkpoint: ServiceNow integration verified end-to-end
> against a live ServiceNow Personal Developer Instance (PDI).**

## What is actually working

The core path has been exercised, not only designed:

``` text
ServiceNow Incident
       |
       | Async Business Rule
       | RESTMessageV2 / HTTPS
       v
Cloudflare HTTPS endpoint
       |
       v
case-integration-service :8002
       |
       +--> CaseReference
       |
       +--> OutboxEvent
               |
               +--> CASE_ACCEPTED_FOR_DISPATCH
               |
               +--> CASE_ACCEPTED_FOR_ANALYTICS
                              |
                              v
                    integration-worker
                       |             |
                       v             v
                Mock Provider   analytics-service :8003
                                     |
                                     v
                             healthcare_case_fact
```

The ServiceNow-to-API leg was verified using an actual Incident record.
The resulting `case_reference` row was verified in MariaDB/Adminer.

## Current status

  Capability                             Status
  -------------------------------------- --------------
  Repository / Docker baseline           COMPLETE
  Master Data Service                    COMPLETE
  Case Integration Service               COMPLETE
  Idempotency                            COMPLETE
  Correlation IDs                        COMPLETE
  Transactional Outbox                   COMPLETE
  Integration audit records              COMPLETE
  Bounded retries                        COMPLETE
  Dead-letter persistence                COMPLETE
  Mock Provider System                   COMPLETE
  Analytics Service                      COMPLETE
  Analytics persistence port             COMPLETE
  Analytics end-to-end fan-out           COMPLETE
  ServiceNow Incident → JanSwasthya      **VERIFIED**
  ServiceNow lifecycle synchronization   NEXT
  True exponential backoff               HARDENING
  Tenant authorization hardening         PENDING
  Production authentication              PENDING
  MCP server                             FUTURE

## Domain / tenant model

The primary tenant is the **Hospital Group**.

``` text
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

Tenant context should ultimately be derived from authenticated identity
and server-side authorization rather than trusted directly from a
client-supplied `tenant_id`.

## Services

### Master Data Service

``` text
services/master-data-service/
```

Owns:

-   Hospital Group
-   Hospital
-   Facility
-   Department
-   Healthcare Service

Port: `8001`

### Case Integration Service

``` text
services/case-integration-service/
```

Owns the healthcare case ingestion boundary and integration reliability
state.

Responsibilities:

-   request validation
-   idempotency
-   correlation ID handling
-   `CaseReference` persistence
-   atomic outbox creation
-   integration message/attempt auditing
-   dead-letter persistence

Port: `8002`

Endpoint:

``` http
POST /api/v1/cases
```

Required header:

``` text
Idempotency-Key
```

Optional header:

``` text
X-Correlation-ID
```

### Analytics Service

``` text
services/analytics-service/
```

Port: `8003`

Endpoints:

``` http
GET  /health
POST /api/v1/analytics/cases
```

Primary table:

``` text
healthcare_case_fact
```

The analytics service uses a repository/port boundary so the application
service does not depend directly on MariaDB-specific persistence.

### Integration Worker

``` text
workers/integration-worker/
```

The existing worker is reused for downstream processing.

It routes:

``` text
CASE_ACCEPTED_FOR_DISPATCH
CASE_ACCEPTED_FOR_ANALYTICS
```

through separate adapters.

### Mock Provider System

``` text
mock-systems/mock-provider-system/
```

Port: `9000`

It provides a synthetic external healthcare provider boundary and
controlled failure simulation for reliability testing.

## Reliability architecture

The case transaction creates two independent downstream events:

``` text
CASE_ACCEPTED_FOR_DISPATCH
CASE_ACCEPTED_FOR_ANALYTICS
```

This is deliberate.

If analytics is unavailable while provider delivery succeeds:

``` text
Provider event   -> PROCESSED
Analytics event  -> RETRY -> DEAD_LETTER
```

The provider operation does not need to be repeated because analytics
failed.

Current reliability mechanisms:

-   Idempotency keys
-   Payload hash validation for idempotency-key reuse
-   Correlation IDs
-   Atomic outbox writes
-   Integration messages
-   Integration attempts
-   Bounded retries
-   Dead-letter persistence
-   Independent downstream event state

**Known hardening item:** the current worker retry mechanism is bounded
but does not yet implement true exponential backoff.

## Analytics persistence portability

Current:

``` text
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

Future adapters can target PostgreSQL or an analytical store such as
ClickHouse.

The architectural goal is portability at the application boundary; it
does **not** claim that a database migration is zero-effort.

## Database

The MVP intentionally uses one shared MariaDB instance.

This is a learning and implementation simplification. Logical service
boundaries are maintained even though the physical database is shared.

Operational migration history:

``` text
2a5d2593a683  create_master_data_tables
f7629d3baf9f  add_case_reference_and_idempotency
0e943d03e523  add_outbox_and_reliability_tables
```

Analytics has an independent Alembic version table:

``` text
analytics_alembic_version
```

Analytics migration:

``` text
b8b6e31bf5a3_create_healthcare_case_fact
```

## ServiceNow integration --- verified

ServiceNow is the operational case system of record.

The current PDI integration uses:

``` text
ServiceNow Incident
    |
    | Async Business Rule
    v
RESTMessageV2
    |
    | HTTPS
    v
Cloudflare Quick Tunnel
    |
    v
case-integration-service
```

### Verified live Incident

A real ServiceNow Incident was created with:

``` text
INC0010002_BHANU_ASYNC
```

The ServiceNow activity stream recorded:

``` text
JanSwasthya integration
HTTP Status: 201
```

The API response contained:

``` text
status: ACCEPTED
case_number: INC0010002_BHANU_ASYNC
```

and a JanSwasthya `case_reference_id`.

The same Incident was then visible in MariaDB/Adminer in the
`case_reference` table with:

``` text
case_number:
INC0010002_BHANU_ASYNC

servicenow_sys_id:
2010e83d3d7471011e7faa6feaad3c2

tenant_id:
830f21a0-3285-4697-b570-ccb0bdf33191

hospital_id:
3abf0419-1f03-4c98-8f2e-012a581e7497
```

This is the strongest current integration proof because it demonstrates
an actual ServiceNow record crossing the integration boundary and being
persisted by JanSwasthya Connect.

A second ServiceNow-side script invocation was also successfully tested
earlier using `RESTMessageV2`.

See:

``` text
docs/07_SERVICENOW_INTEGRATION_VERIFICATION.md
```

for the reproducible contract, configuration, evidence, and current
limitations.

## Cloudflare development endpoint

For the current local development setup:

``` text
ServiceNow
    |
    v
Cloudflare Quick Tunnel
    |
    v
Windows host :8002
    |
    v
Docker case-integration-service
```

The Quick Tunnel is intentionally a development mechanism. It is not
treated as a production ingress design.

## Docker runtime

Compose services:

``` text
mariadb
mock-provider-system
integration-worker
master-data-service
adminer
analytics-service
case-integration-service
```

Ports:

``` text
Master Data Service       :8001
Case Integration Service  :8002
Analytics Service        :8003
Mock Provider System      :9000
Adminer                   :8080
```

MariaDB remains internal to the Docker network.

## Verification philosophy

The repository is intended to show both **implementation** and
**evidence**.

Useful evidence should be reproducible from:

1.  source code and configuration in the repository
2.  database state visible through MariaDB/Adminer
3.  ServiceNow Incident activity and configuration
4.  API responses
5.  integration/outbox audit state
6.  automated tests where available

The latest ServiceNow verification is documented rather than presented
as an architectural assumption.

## Testing

Current automated coverage includes service-level tests for:

-   analytics health
-   analytics fact creation
-   existing fact update
-   fact ID preservation
-   mock provider behavior

Runtime verification has also covered:

-   case creation
-   idempotency
-   correlation propagation
-   outbox creation
-   provider dispatch
-   analytics dispatch
-   analytics fact persistence
-   analytics failure → retry → dead-letter behavior
-   ServiceNow Incident → Case Integration Service

## Known limitations

These are deliberately visible rather than hidden:

-   ServiceNow tenant/hospital/service mapping is currently hardcoded
    for the MVP demonstration.
-   The case API still accepts `tenant_id` in the request model;
    authenticated tenant derivation is a security-hardening task.
-   Current worker retries are bounded but not true exponential backoff.
-   Cloudflare Quick Tunnel is temporary and unauthenticated.
-   ServiceNow authentication hardening (OAuth 2.0 / least privilege) is
    still pending.
-   Async Business Rule implementation is a working MVP integration
    mechanism; a production design should keep the trigger thin and
    avoid unnecessary `current.update()` patterns.
-   Analytics reconciliation and dashboard read models are not complete.
-   MCP is not implemented.

## Architecture style

The project uses a pragmatic Hexagonal / Ports-and-Adapters approach:

``` text
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

The intent is to preserve meaningful boundaries without introducing
infrastructure that the MVP does not need.

## Project structure

``` text
janswasthya-connect/
|
+-- services/
|   +-- master-data-service/
|   +-- case-integration-service/
|   +-- analytics-service/
|
+-- mock-systems/
|   +-- mock-provider-system/
|
+-- workers/
|   +-- integration-worker/
|
+-- docs/
|   +-- 06_CURRENT_STATE.md
|   +-- 07_SERVICENOW_INTEGRATION_VERIFICATION.md
|
+-- tests/
+-- docker-compose.yml
+-- README.md
```

## Documentation

  --------------------------------------------------------------------------------------
  Document                                           Purpose
  -------------------------------------------------- -----------------------------------
  `docs/06_CURRENT_STATE.md`                         Current implementation checkpoint,
                                                     verified state, limitations, and
                                                     next work

  `docs/07_SERVICENOW_INTEGRATION_VERIFICATION.md`   Live ServiceNow integration
                                                     configuration and evidence

  `README.md`                                        Project overview and architecture
                                                     entry point
  --------------------------------------------------------------------------------------

The documentation directory is intentionally being brought back into
sync with the implementation. New architecture/ADR documents should be
added as the corresponding design decisions are finalized rather than
creating speculative documentation.

## Next steps

1.  ServiceNow lifecycle synchronization.
2.  Improve worker retry/backoff semantics.
3.  Add stronger automated worker integration tests.
4.  Add analytics aggregation and reconciliation.
5.  Harden tenant authorization.
6.  Replace development ingress/authentication with production-grade
    controls.
7.  Define MCP tools over stable application services.
8.  Complete ADR and security/threat-model documentation.
