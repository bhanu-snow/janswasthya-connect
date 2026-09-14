# ServiceNow Module Map

## 1. Purpose

This document explains which ServiceNow capabilities matter for the JanSwasthya healthcare use case and how they relate to the architecture.

The goal is:

> Business requirement → ServiceNow capability → Integration

rather than adding modules only for demonstration.

## 2. Module Overview

| ServiceNow Capability | Business Purpose | Project Relevance |
|---|---|---|
| Incident | Operational issue tracking | Core |
| Problem | Root cause / recurring issue management | Core learning |
| Change | Planned corrective action | Core learning |
| CMDB | CI/service relationships | Basic |
| Flow Designer | Visual workflow automation | Core learning |
| IntegrationHub | Managed/reusable integrations | Basic/conceptual |
| RESTMessageV2 | REST integration | Already relevant |
| Async Business Rule | Asynchronous server-side trigger | Already used |

## 3. Incident

Incident is used to track an operational issue and restore normal service.

Simple rule:

> Something is broken → Incident.

In this architecture:

```text
ServiceNow Incident
        |
        v
JanSwasthya CaseReference
```

ServiceNow owns the operational record; JanSwasthya owns the external integration processing.

### Interview Question

**Q: Incident aur JanSwasthya Case mein kya difference hai?**

**A:** Incident ServiceNow ka operational record hai. JanSwasthya CaseReference integration boundary ka record hai jo external healthcare processing ko track karta hai.

## 4. Problem

Problem is used to investigate recurring incidents and their underlying root cause.

```text
Repeated incidents
       |
       v
    Problem
       |
       v
Root Cause Analysis
```

Simple rule:

> Why does this keep happening? → Problem.

## 5. Change

Change is used to plan and safely execute a modification.

```text
Problem
   |
   v
Root Cause
   |
   v
Change
```

Typical concepts include implementation plan, risk, approval, schedule and rollback.

## 6. Incident → Problem → Change

A useful enterprise service-management relationship is:

```text
Incident
   |
   | recurring?
   v
Problem
   |
   | corrective modification required
   v
Change
```

## 7. CMDB

CMDB manages configuration items (CIs) and their relationships.

Example:

```text
Healthcare Application
        |
        v
Application Server
        |
        v
Database
```

A ServiceNow Incident can be associated with relevant CI/service context.

### Important Distinction

JanSwasthya business/master data:

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

is not automatically the same thing as CMDB data.

Business master data and technical configuration data have different purposes.

## 8. Flow Designer

Flow Designer is useful for visual business workflow automation.

Example:

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

### Flow Designer vs Business Rule

**Flow Designer:** visual business workflow and orchestration.

**Business Rule:** precise server-side record behavior.

Both are complementary.

## 9. RESTMessageV2

RESTMessageV2 is a ServiceNow capability for making REST API calls.

Conceptually:

```text
ServiceNow
    |
    | RESTMessageV2 / HTTPS
    v
JanSwasthya
```

It is appropriate for direct custom REST API invocation.

## 10. IntegrationHub

IntegrationHub provides reusable integration actions/connectors and workflow-oriented integration capabilities.

Conceptually:

```text
ServiceNow Workflow
        |
        v
IntegrationHub Action
        |
        v
External System
```

It becomes especially useful where reuse, managed connectors or enterprise integration governance matter.

### RESTMessageV2 vs IntegrationHub

| RESTMessageV2 | IntegrationHub |
|---|---|
| Direct REST invocation | Reusable integration capability |
| Lower-level control | Workflow-oriented |
| Custom REST calls | Connectors/actions |
| Precise API configuration | Reuse/governance |

Not every REST call needs to be forced through IntegrationHub.

## 11. MID Server

MID Server helps ServiceNow communicate with private/on-premise systems.

```text
ServiceNow Cloud
       |
       v
   MID Server
       |
       v
Private Network
```

It becomes relevant when the target system is not directly reachable from the ServiceNow environment.

## 12. SOAP

SOAP remains relevant for legacy enterprise integrations.

```text
ServiceNow
    |
    | SOAP
    v
Legacy System
```

If a target system exposes only SOAP, REST should not be forced unnecessarily.

## 13. Kafka

Kafka is useful for high-volume event streaming and multiple independent consumers.

```text
Producer
   |
 Kafka
 / | \
v  v  v
C1 C2 C3
```

Kafka is not required by the current JanSwasthya MVP.

It becomes more reasonable when event volume, consumer count, replay requirements or streaming needs justify the additional operational complexity.

## 14. OAuth2

OAuth2 is commonly used for secure API authorization.

```text
ServiceNow
    |
    | OAuth2 access token
    v
External API
```

Production authentication and authorization remain a hardening area for this MVP.

## 15. What We Actually Need to Learn

### Must Understand

- Incident
- Problem
- Change
- CMDB basics
- Flow Designer
- REST integration
- Async integration

### Basic Understanding

- IntegrationHub
- MID Server
- OAuth2
- SOAP

### Architecture Understanding

- Kafka
- API Gateway/iPaaS
- event streaming
- enterprise integration governance

Principle:

> Choose the technology because the requirement needs it, not because it is a popular architecture keyword.
