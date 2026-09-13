# JanSwasthya Connect --- ServiceNow Integration Verification

**Verification date:** 2026-09-13

## Purpose

This document records the first verified live integration between the
JanSwasthya Connect API and a real ServiceNow Personal Developer
Instance (PDI).

The objective is to make the integration claim auditable from the
repository and to distinguish verified behavior from planned production
hardening.

## Verified flow

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
case-integration-service :8002
        |
        +--> CaseReference
        |
        +--> Outbox Events
```

## ServiceNow configuration

Scoped application:

``` text
JanSwasthya Connect Integration
```

Application scope:

``` text
x_2221183_janswa_0
```

REST Message:

``` text
JanSwasthya Connect API
```

HTTP method:

``` text
Create Case
POST
```

API path:

``` text
/api/v1/cases
```

Required headers:

``` text
Content-Type: application/json
Idempotency-Key: <value>
X-Correlation-ID: <value>
```

Business Rule:

``` text
Table: Incident
When: Async
Insert: true
Update: false
Advanced: true
```

## Why Async matters

The initial synchronous Business Rule attempt failed because ServiceNow
blocked outbound HTTP from the scoped synchronous Business Rule.

The rule was changed to `Async`, after which the live Incident
integration succeeded.

This is an important platform-specific observation from the actual PDI
rather than an assumed design detail.

## Live verification

### ServiceNow record

``` text
INC0010002_BHANU_ASYNC
```

The Incident activity stream recorded:

``` text
JanSwasthya integration
HTTP Status: 201
```

The response included:

``` text
case_number:
INC0010002_BHANU_ASYNC

status:
ACCEPTED
```

The response also contained a JanSwasthya case reference and correlation
ID.

### MariaDB record

The same Incident was visible in:

``` text
case_reference
```

with:

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

The captured evidence therefore demonstrates:

``` text
ServiceNow record
      |
      v
HTTP 201
      |
      v
JanSwasthya case accepted
      |
      v
case_reference persisted in MariaDB
```

## Correlation and idempotency

The current Business Rule derives both values from the originating
Incident:

``` text
correlationId =
snow-incident-<incident_sys_id>

idempotencyKey =
snow-incident-<incident_sys_id>
```

For the verified Incident:

``` text
sys_id:
2010e83d3d7471011e7faa6feaad3c2
```

Therefore the logical integration identity is stable across retries of
the same Incident.

## Request mapping

The current MVP sends:

``` json
{
  "tenant_id": "<configured MVP tenant>",
  "case_number": "<incident number>",
  "servicenow_sys_id": "<incident sys_id>",
  "hospital_id": "<configured MVP hospital>",
  "service_code": "CARD-OPD"
}
```

This is intentionally sufficient to prove the integration boundary.

The tenant/hospital/service mapping is currently hardcoded and is
explicitly a production-hardening task.

## Repository-side evidence

The repository contains the implementation of:

``` text
POST /api/v1/cases
```

plus:

``` text
CaseReference
OutboxEvent
IntegrationMessage
IntegrationAttempt
DeadLetterMessage
```

The case integration service writes the business record and outbox
events transactionally.

The worker then processes:

``` text
CASE_ACCEPTED_FOR_DISPATCH
CASE_ACCEPTED_FOR_ANALYTICS
```

independently.

This means the ServiceNow integration does not bypass the established
application/reliability architecture.

## Earlier direct ServiceNow script verification

A direct ServiceNow `Scripts - Background` invocation was also
successfully tested using `RESTMessageV2`.

Example case:

``` text
CS-SNOW-SCRIPT-001
```

The JanSwasthya API returned HTTP `201`.

This provided an earlier controlled proof of the ServiceNow REST Message
configuration before the live Incident Business Rule was completed.

## Evidence screenshots

Two screenshots were captured during the verification session:

``` text
ServiceNow_Incident_created_inserted_in_mariaDB.JPG
ServiceNow_Incident_created_inserted_in_mariaDB_verify.JPG
```

They show:

1.  the ServiceNow Incident and its integration activity
2.  the corresponding MariaDB/Adminer `case_reference` data

The screenshots are conversation evidence. The repository should retain
the textual verification in this document even if the binary screenshots
are stored separately.

## What this proves

This checkpoint proves:

-   ServiceNow can invoke the JanSwasthya API.
-   The integration can operate asynchronously from an Incident Business
    Rule.
-   RESTMessageV2 can call the API over HTTPS.
-   The API accepts the ServiceNow case.
-   The case is persisted as a `case_reference`.
-   The existing JanSwasthya case/outbox architecture remains the
    integration boundary.

## What this does not prove

This checkpoint does **not** prove production readiness.

Still required:

-   OAuth 2.0 / least-privilege authentication
-   stable production ingress
-   tenant-aware identity mapping
-   lifecycle synchronization
-   production-grade ServiceNow error handling
-   ServiceNow-side retry strategy where appropriate
-   true exponential backoff in the JanSwasthya worker
-   production observability
-   security/threat-model review

## Reproduction outline

1.  Start the JanSwasthya Docker Compose stack.
2.  Ensure `case-integration-service` is reachable on port `8002`.
3.  Start a development HTTPS tunnel to the local API.
4.  Configure the ServiceNow REST Message to point to the HTTPS
    endpoint.
5.  Configure the Incident Business Rule as `Async`.
6.  Create a new Incident.
7.  Check the Incident activity stream for the HTTP response.
8.  Query `case_reference` in MariaDB/Adminer using the Incident number.
9.  Query `outbox_event` using the correlation ID to inspect downstream
    processing.
10. Check `integration_message`, `integration_attempt`, and
    `dead_letter_message` when testing failures.

## Evidence principle

A portfolio reviewer should be able to distinguish:

``` text
DESIGN
  !=
IMPLEMENTATION
  !=
RUNTIME VERIFICATION
  !=
PRODUCTION HARDENING
```

This document records the runtime verification separately from the
remaining hardening work.
