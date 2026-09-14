# JanSwasthya Connect

Production-style healthcare integration and analytics MVP demonstrating how **ServiceNow operational workflows can be connected reliably to external healthcare/provider systems**.

The project focuses on a practical enterprise architecture rather than adding infrastructure for its own sake.

> **ServiceNow manages the operational workflow. JanSwasthya manages external healthcare integration and reliable downstream processing.**

---

## Business Scenario

A healthcare organization may use ServiceNow as the central operational workflow platform while provider and healthcare systems remain outside ServiceNow.

A typical flow is:

```text
ServiceNow Incident
        |
        | Async REST / HTTPS
        v
JanSwasthya Case Integration
        |
        v
CaseReference + OutboxEvent
        |
        v
Integration Worker
       / \
      /   \
     v     v
Provider  Analytics
```

The architecture deliberately separates:

- ServiceNow operational workflow
- external healthcare integration
- provider processing
- analytics processing

This keeps provider-specific integration and reliability concerns outside the ServiceNow workflow boundary.

---

# Architecture

```text
                         ServiceNow
                      Incident / Workflow
                             |
                             | Async Business Rule
                             | RESTMessageV2 / HTTPS
                             v
                    +----------------------+
                    | Cloudflare HTTPS     |
                    | Dev Ingress          |
                    +----------+-----------+
                               |
                               v
                 +----------------------------+
                 | Case Integration Service   |
                 | :8002                      |
                 |                            |
                 | - Validation                |
                 | - Idempotency               |
                 | - Correlation ID            |
                 | - CaseReference             |
                 | - Outbox                    |
                 | - Integration Attempts      |
                 | - Dead Letter               |
                 +-------------+--------------+
                               |
                               v
                       +---------------+
                       |   OutboxEvent  |
                       +-------+-------+
                               |
                               v
                     +-------------------+
                     | Integration Worker|
                     +---------+---------+
                               |
                 +-------------+-------------+
                 |                           |
                 v                           v
        +------------------+       +------------------+
        | Mock Provider    |       | Analytics Service|
        | :9000            |       | :8003            |
        +------------------+       +------------------+
```

---

# Core Design

The integration boundary follows a durable asynchronous processing model:

```text
ServiceNow Incident
        |
        v
Async Integration
        |
        v
CaseReference
        |
        +--> CASE_ACCEPTED_FOR_DISPATCH
        |
        +--> CASE_ACCEPTED_FOR_ANALYTICS
```

Provider and analytics processing are intentionally independent.

An analytics failure should not force provider work to be redelivered.

---

# Services

## 1. Master Data Service — `:8001`

Owns healthcare business master data:

```text
Hospital Group
      |
      v
Hospital
      |
      v
Facility
      |
      v
Department
      |
      v
Healthcare Service
```

The hierarchy provides business ownership, operational location and healthcare service context.

---

## 2. Case Integration Service — `:8002`

The main integration boundary.

Responsibilities include:

- request validation
- idempotency
- payload hash validation
- correlation ID handling
- CaseReference persistence
- atomic outbox persistence
- integration message tracking
- integration attempt tracking
- bounded retry handling
- dead-letter persistence

---

## 3. Analytics Service — `:8003`

Provides analytics-oriented processing.

The application keeps an explicit repository/port boundary so the analytics domain is not tightly coupled to a specific persistence implementation.

---

## 4. Integration Worker

Consumes durable downstream work and routes independent events through separate adapters.

```text
Outbox
   |
   v
Worker
 /   \
v     v
Provider  Analytics
```

---

## 5. Mock Provider System — `:9000`

Represents an external healthcare/provider system for local integration and failure-path testing.

This is intentionally a mock downstream system.

The ServiceNow → JanSwasthya integration itself has been verified against a real ServiceNow PDI.

---

# Reliability Design

Healthcare integrations need protection against duplicate, lost and repeatedly failing messages.

## Idempotency

Requests use:

```text
Idempotency-Key
```

The system also validates the payload hash associated with the idempotency key.

This prevents a retry from silently creating another case and prevents the same key from being reused with a different payload.

---

## Correlation ID

Optional:

```text
X-Correlation-ID
```

The correlation ID provides traceability across:

```text
ServiceNow
    |
JanSwasthya
    |
Worker
   / \
Provider Analytics
```

---

## Atomic Outbox

Case creation and the corresponding event publication intent are persisted together.

```text
Database Transaction
       |
       +--> CaseReference
       |
       +--> OutboxEvent
```

This reduces the risk of losing downstream work between database persistence and event publication.

---

## Independent Downstream Events

Two logical downstream events are maintained:

```text
CASE_ACCEPTED_FOR_DISPATCH
CASE_ACCEPTED_FOR_ANALYTICS
```

They are processed independently.

Therefore:

```text
Provider Event
     |
     +--> PROCESSED

Analytics Event
     |
     +--> RETRY
     +--> RETRY
     +--> RETRY
     +--> DEAD_LETTER
```

An analytics outage does not require provider work to be retried.

---

## Retry and Dead Letter

Current retries are bounded.

When retry attempts are exhausted, failed work is persisted as dead-letter state rather than silently discarded.

### Current limitation

The current retry implementation is bounded but does not claim full production-grade exponential backoff.

Exponential backoff is a production hardening item.

---

# ServiceNow Integration

## Current Integration

The current ServiceNow integration uses:

```text
ServiceNow Incident
        |
        v
Async Business Rule
        |
        v
RESTMessageV2 / HTTPS
        |
        v
JanSwasthya
```

The asynchronous trigger keeps the ServiceNow operational transaction decoupled from downstream provider/analytics processing.

---

# Verified ServiceNow Integration

A real ServiceNow PDI integration has been verified.

Verified Incident:

```text
INC0010002_BHANU_ASYNC
```

The documented verification shows:

```text
ServiceNow Incident
        |
        v
JanSwasthya
        |
        v
HTTP 201
        |
        v
CaseReference persisted
```

The corresponding database verification is documented in:

```text
docs/07_SERVICENOW_INTEGRATION_VERIFICATION.md
```

This is the strongest current evidence that the ServiceNow → JanSwasthya integration boundary is working.

---

# ServiceNow Business Scope

The ServiceNow scope is intentionally focused on a coherent healthcare operational workflow.

## Core capabilities

- Incident
- Problem
- Change
- CMDB basics
- Flow Designer
- REST / asynchronous integration

## Integration learning

- RESTMessageV2
- IntegrationHub basics
- MID Server concepts
- OAuth2 concepts
- SOAP integration concepts
- Kafka/event-streaming concepts

Not every technology listed above is implemented in this MVP.

The purpose is to understand **when and why** each capability should be used.

---

# Incident → Problem → Change

The ServiceNow operational lifecycle can be understood as:

```text
Incident
   |
   | recurring / underlying cause?
   v
Problem
   |
   | corrective modification required?
   v
Change
```

Simple interpretation:

```text
Incident = Something is broken.

Problem  = Why does this keep happening?

Change   = How will we safely modify the environment?
```

This gives the project a real business workflow instead of treating ServiceNow only as an API source.

---

# CMDB and Business Master Data

JanSwasthya has its own healthcare business hierarchy:

```text
Hospital Group
    |
Hospital
    |
Facility
    |
Department
    |
Healthcare Service
```

This should not automatically be treated as the ServiceNow CMDB.

A useful distinction is:

```text
Business Master Data
        |
        +--> Hospital
        +--> Facility
        +--> Department
        +--> Healthcare Service

CMDB
        |
        +--> Technical / Operational CIs
        +--> Relationships
```

Only entities with clear operational dependency, impact or configuration-management value should be represented as CIs.

---

# Flow Designer

Flow Designer is the preferred learning area for visual ServiceNow workflow automation.

Conceptually:

```text
Incident Created
       |
       v
Condition
       |
       v
Action
       |
       v
Notify / Integrate
```

Business workflow should remain understandable and maintainable.

---

# RESTMessageV2 vs IntegrationHub

Both are relevant, but they solve slightly different problems.

| RESTMessageV2 | IntegrationHub |
|---|---|
| Direct REST invocation | Reusable integration capability |
| Lower-level control | Workflow-oriented |
| Custom REST APIs | Connectors/actions |
| Precise API configuration | Reuse and governance |

Not every REST API call needs to be forced through IntegrationHub.

The choice should follow the actual integration requirement.

---

# Integration Patterns — When to Use What?

## REST

Use when a direct API boundary is appropriate.

Current ServiceNow → JanSwasthya integration follows this model.

---

## Async Messaging

Use when downstream processing should not block the initiating operational workflow.

Current JanSwasthya design uses asynchronous processing for this reason.

---

## MID Server

Relevant when ServiceNow needs to communicate with private/on-premise systems that are not directly reachable from the ServiceNow environment.

```text
ServiceNow Cloud
       |
       v
   MID Server
       |
       v
Private Network
```

It is not required for the current publicly reachable HTTPS development endpoint.

---

## SOAP

Relevant for legacy enterprise systems that expose SOAP interfaces.

REST should not be forced when the target system is inherently SOAP-based.

---

## Kafka

Useful when the architecture requires:

- high event volume
- many independent consumers
- event streaming
- replay capabilities
- durable streaming infrastructure

Kafka is not required by the current MVP because Outbox + Worker already provides the required processing model.

---

## API Gateway / iPaaS

Useful when an enterprise requires centralized:

- API governance
- routing
- transformation
- security
- integration management

Additional middleware should be introduced only when those requirements justify its operational complexity.

---

## OAuth2

Relevant for production-grade API authorization.

The current MVP does not claim a complete production OAuth2 security implementation.

---

# Business Entity Model

The healthcare domain is represented as:

```text
Hospital Group
      |
Hospital
      |
Facility
      |
Department
      |
Healthcare Service
```

Conceptual ServiceNow mapping:

| JanSwasthya | ServiceNow Concept |
|---|---|
| Hospital Group | Organization / tenant boundary |
| Hospital | Organization / business unit |
| Facility | Location |
| Department | Department / operational ownership |
| Healthcare Service | Business/service context |
| Technical system | Configuration Item |
| Operational issue | Incident |

This is a conceptual mapping, not a forced one-to-one implementation.

---

# Tenant Model

Hospital Group provides a natural logical tenant boundary.

Conceptually:

```text
Tenant A
   |
   +--> Hospitals
   +--> Facilities
   +--> Departments
   +--> Services

Tenant B
   |
   +--> Hospitals
   +--> Facilities
   +--> Departments
   +--> Services
```

The current MVP uses simplified tenant mapping.

A production implementation should derive tenant context from authenticated identity rather than blindly trusting a client-provided tenant ID.

---

# Repository Structure

```text
janswasthya-connect/
│
├── README.md
│
├── docs/
│   ├── 06_CURRENT_STATE.md
│   ├── 07_SERVICENOW_INTEGRATION_VERIFICATION.md
│   ├── 08_BUSINESS_USE_CASE.md
│   ├── 09_SERVICENOW_MODULE_MAP.md
│   ├── 10_BUSINESS_ENTITY_MODEL.md
│   └── FAQ.md
│
├── master-data-service/
├── case-integration-service/
├── analytics-service/
├── integration-worker/
└── mock-provider/
```

---

# Documentation

| Document | Purpose |
|---|---|
| `docs/06_CURRENT_STATE.md` | Current implementation and architecture state |
| `docs/07_SERVICENOW_INTEGRATION_VERIFICATION.md` | Real ServiceNow PDI integration evidence |
| `docs/08_BUSINESS_USE_CASE.md` | Business scenario and system responsibilities |
| `docs/09_SERVICENOW_MODULE_MAP.md` | ServiceNow module and integration mapping |
| `docs/10_BUSINESS_ENTITY_MODEL.md` | Healthcare business entity hierarchy and ServiceNow mapping |
| `docs/FAQ.md` | Architecture and interview-oriented questions and answers |

---

# Local Services

| Component | Port | Purpose |
|---|---:|---|
| Master Data Service | `8001` | Healthcare master data |
| Case Integration Service | `8002` | External case integration boundary |
| Analytics Service | `8003` | Analytics processing |
| Mock Provider | `9000` | External provider simulation |

---

# API Contract

The case integration API expects an idempotency key.

Required:

```text
Idempotency-Key
```

Optional:

```text
X-Correlation-ID
```

The idempotency key protects the integration boundary from duplicate processing during retries.

---

# Current Status

## Verified

- ServiceNow Incident → JanSwasthya integration
- Real ServiceNow PDI request
- HTTP `201` response
- CaseReference persistence
- Idempotency handling
- Payload hash validation
- Correlation ID support
- Atomic outbox persistence
- Independent provider/analytics events
- Bounded retry behavior
- Dead-letter persistence
- Analytics failure → retry → dead-letter scenario

## Learning / Next

- Incident → Problem → Change lifecycle
- CMDB basics
- Flow Designer
- IntegrationHub basics
- ServiceNow business workflow modeling
- Evidence/screenshots for the above

## Future / Hardening

- lifecycle/status synchronization where justified
- production authentication/authorization
- authenticated tenant derivation
- production ingress
- exponential backoff
- stronger observability
- reconciliation
- operational replay controls
- capacity/performance testing
- disaster recovery considerations

---

# Known Limitations

This is an MVP and intentionally does not claim every enterprise capability.

Current limitations include:

1. Retry is bounded but not full exponential backoff.
2. Tenant authorization requires production hardening.
3. Production authentication/OAuth2 and least-privilege controls require further work.
4. Cloudflare Quick Tunnel is a development ingress mechanism and is not a production deployment model.
5. ServiceNow tenant/hospital/service mapping is simplified for the MVP.
6. Analytics reconciliation and operational read models are not complete.
7. Advanced infrastructure such as Kafka/MID Server is not implemented because the current requirement does not justify it.

---

# Architecture Principles

## 1. Requirement before technology

> Choose technology because the business or system requirement needs it, not because it is a popular architecture keyword.

## 2. Keep workflow and integration boundaries clear

ServiceNow owns operational workflow.

JanSwasthya owns external integration processing.

## 3. Prefer reliable simple designs

Outbox + Worker is sufficient for the current event-processing requirement.

Kafka should not be introduced without a requirement that justifies it.

## 4. Separate failure domains

Provider and Analytics processing are independent.

One downstream failure should not unnecessarily impact another.

## 5. Be explicit about production gaps

Implemented MVP capabilities and production hardening requirements are documented separately.

---

# Next Steps

The next phase is intentionally focused rather than adding more infrastructure.

1. Model the healthcare business scenario in the ServiceNow PDI.
2. Work through the Incident → Problem → Change lifecycle.
3. Add basic CMDB/service relationship understanding.
4. Build a small Flow Designer workflow around the business scenario.
5. Understand and demonstrate the IntegrationHub approach where it provides clear value.
6. Evaluate lifecycle/status synchronization between JanSwasthya and ServiceNow if required by the business flow.
7. Capture real ServiceNow screenshots and verification evidence.
8. Keep advanced patterns such as MID Server, Kafka, SOAP and API Gateway/iPaaS as architecture knowledge unless an actual requirement justifies implementation.

---

# Summary

JanSwasthya Connect demonstrates a practical healthcare integration architecture:

```text
ServiceNow
   |
   | Async REST
   v
JanSwasthya
   |
   | Durable Outbox
   v
Integration Worker
   |
   +--> Provider
   |
   +--> Analytics
```

The key architectural ideas demonstrated are:

- clear system boundaries
- asynchronous integration
- idempotency
- correlation IDs
- atomic outbox
- independent downstream events
- bounded retries
- dead-letter persistence
- healthcare business entity modeling
- ServiceNow operational workflow integration

The project deliberately avoids adding technology for technology's sake.
