# Business Use Case — ServiceNow + JanSwasthya

## 1. Purpose

JanSwasthya Connect is positioned as a healthcare integration and processing layer around ServiceNow operational workflows.

**ServiceNow manages the operational workflow; JanSwasthya manages external healthcare integration and reliable processing.**

This separation prevents ServiceNow from becoming tightly coupled to provider-specific integration logic.

## 2. Business Scenario

A healthcare organization may use ServiceNow to manage operational issues while provider systems remain outside ServiceNow.

A typical flow is:

```text
ServiceNow Incident
       |
       | Async Integration
       v
JanSwasthya
       |
       +--------------------+
       |                    |
       v                    v
Provider System        Analytics
```

## 3. End-to-End Business Flow

### Step 1 — Incident Creation

An operational healthcare issue is created as a ServiceNow Incident.

Relevant context may include:

- affected service
- facility/location
- department
- priority
- description
- operational context

### Step 2 — ServiceNow to JanSwasthya

ServiceNow sends the request through an asynchronous server-side integration flow.

Current implementation:

```text
Async Business Rule
        |
        v
RESTMessageV2 / HTTPS
```

ServiceNow does not wait for provider or analytics processing to complete.

### Step 3 — Case Creation

JanSwasthya's `case-integration-service`:

- validates the request
- handles idempotency
- handles correlation ID
- creates a `CaseReference`
- persists an `OutboxEvent`

### Step 4 — Durable Event Processing

Case creation and the OutboxEvent are persisted within the database transaction boundary.

```text
Database Transaction
      |
      +--> CaseReference
      |
      +--> OutboxEvent
```

### Step 5 — Independent Downstream Processing

The current design uses independent downstream events:

```text
CASE_ACCEPTED_FOR_DISPATCH
CASE_ACCEPTED_FOR_ANALYTICS
```

The worker processes them independently:

```text
                    +--> Provider
                    |
JanSwasthya Worker -+
                    |
                    +--> Analytics
```

Therefore an analytics failure does not require provider work to be redelivered.

## 4. Responsibility Boundaries

| System | Primary responsibility |
|---|---|
| ServiceNow | Operational workflow, Incident/Problem/Change lifecycle, user-facing engagement |
| JanSwasthya | External healthcare integration, case processing, reliability controls and event dispatch |
| Provider System | External healthcare/provider processing |
| Analytics Service | Analytics-oriented processing and reporting data |

JanSwasthya is not a replacement for ServiceNow, and ServiceNow is not being treated as the complete provider-integration processing engine.

## 5. Why Asynchronous Integration?

If ServiceNow waits synchronously for provider processing:

- provider latency can affect ServiceNow
- provider outages can affect the operational workflow
- retry responsibility becomes harder to isolate
- workflow and integration processing become tightly coupled

An asynchronous boundary reduces that coupling.

## 6. Reliability

### Idempotency

`Idempotency-Key` is used to protect against duplicate case creation during retries.

Payload-hash validation also prevents the same idempotency key from silently being reused with a different payload.

### Correlation ID

`X-Correlation-ID` helps trace a request across ServiceNow, JanSwasthya, worker and downstream systems.

### Retry

Downstream failures receive bounded retry attempts.

### Dead Letter

When retries are exhausted, failed work is persisted as dead-letter state for investigation or future reprocessing.

## 7. Why Outbox?

Suppose a case is created in the database but the application crashes before publishing the downstream event.

Without an outbox, the event could be lost.

With the outbox:

```text
Transaction
   |
   +--> CaseReference
   +--> OutboxEvent
```

Both become durable state, allowing the worker to process the event later.

## 8. Current Verified Evidence

The repository documents verification of a real ServiceNow PDI Incident crossing the integration boundary and creating a JanSwasthya case reference.

Verified incident:

`INC0010002_BHANU_ASYNC`

The documented verification includes HTTP `201` and a persisted `case_reference_id`.

Provider/analytics fan-out and the analytics failure path ending in retry and dead-letter persistence are also documented.

Evidence:

- `docs/06_CURRENT_STATE.md`
- `docs/07_SERVICENOW_INTEGRATION_VERIFICATION.md`
- ServiceNow verification section in `README.md`

## 9. ServiceNow Scope

The focused ServiceNow scope is:

- Incident
- Problem
- Change
- CMDB basics
- Flow Designer
- IntegrationHub basics
- REST / asynchronous integration

MID Server, SOAP, Kafka, API Gateway/iPaaS and OAuth2 are architecture patterns to understand and evaluate. They should not be implemented merely to add technology keywords.

## 10. Production Hardening

The current implementation is an MVP and does not claim complete production hardening.

Known areas include:

- authenticated tenant derivation
- production authentication/authorization
- production ingress
- exponential backoff
- stronger observability
- reconciliation
- production-grade edge configuration
- stronger operational controls

Implemented capabilities and future hardening are intentionally kept separate.
