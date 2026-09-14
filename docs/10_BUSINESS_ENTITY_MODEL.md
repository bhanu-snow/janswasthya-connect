# Business Entity Model — Healthcare Domain

## 1. Purpose

JanSwasthya represents the healthcare organization through a simple business hierarchy:

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

This model represents organization, operational location and healthcare service context.

## 2. Hospital Group

Hospital Group represents the highest-level business ownership and logical tenant boundary.

Example:

```text
ABC Healthcare Group
```

A group can contain multiple hospitals.

### Why Tenant Boundary?

Different healthcare groups require logical data isolation.

Therefore:

```text
Hospital Group = logical tenant boundary
```

The current MVP uses simplified/hardcoded tenant mapping.

A production implementation should derive tenant context from authenticated identity.

## 3. Hospital

Hospital represents an individual healthcare organization or business unit.

Example:

```text
ABC Healthcare Group
       |
       +--> ABC City Hospital
       +--> ABC Central Hospital
```

## 4. Facility

Facility represents a physical or operational location.

Example:

```text
ABC City Hospital
       |
       +--> Main Campus
       +--> Emergency Center
       +--> Diagnostic Center
```

## 5. Department

Department represents an operational unit inside a hospital/facility.

Example:

```text
Main Campus
     |
     +--> Emergency
     +--> Cardiology
     +--> Radiology
     +--> Pharmacy
```

## 6. Healthcare Service

Healthcare Service represents the actual service being delivered.

Example:

```text
Cardiology Department
        |
        +--> Cardiology Consultation
        +--> Cardiac Diagnostics
```

## 7. Complete Example

```text
ABC Healthcare Group
        |
        v
ABC City Hospital
        |
        v
Main Campus
        |
        v
Emergency Department
        |
        v
Emergency Care Service
```

If Emergency Care Service has an operational issue, ServiceNow can track it as an Incident while JanSwasthya handles external healthcare integration.

## 8. ServiceNow Mapping

The following is a conceptual mapping, not a mandatory one-to-one implementation.

| JanSwasthya Entity | ServiceNow Concept |
|---|---|
| Hospital Group | Organization / tenant boundary |
| Hospital | Organization / business unit |
| Facility | Location |
| Department | Department / operational ownership |
| Healthcare Service | Business/service context |
| Technical system | Configuration Item (CI) |
| Operational issue | Incident |

The exact ServiceNow data model should be driven by the business requirement.

## 9. Business Master Data vs CMDB

This distinction is important.

### Business Master Data

Represents business entities:

```text
Hospital
Facility
Department
Healthcare Service
```

### CMDB

Primarily represents technical/operational configuration items and relationships.

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

### Why Not Put Everything in CMDB?

Making every Hospital, Facility, Department and business entity a CI can unnecessarily complicate the CMDB.

Better principle:

> Model a business entity in CMDB only when its operational dependency, impact or configuration-management value justifies it.

JanSwasthya can retain the canonical healthcare master-data model while ServiceNow provides operational/technical relationship context.

## 10. Incident Relationship

Conceptually:

```text
ServiceNow Incident
       |
       +--> affected Service / CI
       |
       +--> Facility / Location
       |
       +--> Department context
       |
       v
JanSwasthya CaseReference
```

This connects operational issue tracking with external processing.

## 11. Tenant Isolation

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

Tenant A must not access Tenant B's data.

### Current MVP

Tenant handling is simplified and includes configured mapping.

### Production Model

```text
Authenticated Identity
        |
        v
Tenant Context
        |
        v
Authorization
        |
        v
Business Data
```

A client-provided tenant ID should not be blindly trusted in production.

## 12. Why This Model Matters

The hierarchy helps define:

- data ownership
- tenant boundaries
- operational context
- ServiceNow mapping
- authorization
- analytics dimensions

Therefore the business entity model is an architecture input, not just a database structure.

## 13. Design Principle

> **Model business entities according to business purpose and map them to ServiceNow concepts according to operational purpose.**

A one-to-one mapping should not be forced where the semantics are different.
