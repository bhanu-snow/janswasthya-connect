# JanSwasthya Connect

> **ServiceNow�FastAPI Healthcare Integration Platform**  
> Learning MVP: Enterprise Integration Architecture, Reliability Patterns, and Agent Readiness.

---

## 1. Project Overview & Intent

**JanSwasthya Connect** is an enterprise integration learning platform designed to model real-world interactions between an operational case management system (**ServiceNow**), integration and domain microservices (**Python/FastAPI**), relational persistence (**MariaDB**), and simulated external healthcare hospital systems.

### Primary Purpose
This is **not** a clinical EHR/EMR or patient diagnosis product. The healthcare context provides a realistic, regulated domain to master enterprise integration architecture, multi-tenancy, distributed data consistency, reliability patterns, and AI/MCP integration.

---

## 2. Core Domain & Tenant Model

The platform models an Indian healthcare organization hierarchy with strict server-side multi-tenancy:

\\\	ext
Hospital Group (Tenant Boundary: tenant_id = hospital_group_id)
    +-- Hospital
         +-- Facility
              +-- Department
                   +-- Healthcare Service
\\\

* **Tenant Boundary:** \	enant_id = hospital_group_id\
* **Data Policy:** 100% fictional/synthetic data. Real patient records, real clinical histories, and actual Aadhaar digits are strictly prohibited.

---

## 3. Architecture & Service Boundaries

The system strictly follows **Hexagonal / Ports and Adapters** architecture to prevent direct coupling:

\\\	ext
                 ServiceNow (System of Record: Cases, SLA, Workflow)
                                         �
                                       HTTPS (REST /api/v1/...)
                                         ?
                 FastAPI Boundary (Master Data & Case Integration)
                                         �
                   +-------------------------------------------+
                   ?                                           ?
             MariaDB 11.4                              Integration Worker
   (Master Data, Outbox, Idempotency)                          �
                                                               ?
                                                      Mock Provider System
                                                    (Appointments, Referrals)
\\\

### Non-Negotiable System Rules
1. **ServiceNow Boundary:** ServiceNow is the operational case system of record. It interacts solely via versioned HTTPS/REST APIs (\/api/v1/...\) and must **never** connect directly to MariaDB via SQL/JDBC.
2. **Database Portability:** MariaDB provides initial persistence. All persistence logic sits behind repository interfaces so analytical and persistence stores can migrate without rewriting core business logic.
3. **No Unjustified Infrastructure:** Kafka, RabbitMQ, Redis, Kubernetes, and API Gateways are deliberately excluded until proven necessary via an Architecture Decision Record (ADR).
4. **Agent Readiness (MCP):** An optional Model Context Protocol (MCP) server acts as a consumer adapter over existing FastAPI endpoints. An LLM/Agent **never** queries MariaDB directly.

---

## 4. Reliability & Integration Patterns

* **Header-Based Idempotency (\Idempotency-Key\):** Prevents duplicate business actions on retried requests using SHA-256 payload hashing and response caching.
* **Correlation Tracking (\X-Correlation-ID\):** End-to-end traceability across ServiceNow, FastAPI, MariaDB, and external providers.
* **Transactional Outbox:** Atomically commits domain changes and outbound message events in a single database transaction.
* **Bounded Exponential Backoff Retries:** Automatically handles transient network or provider failures without overwhelming downstream systems.
* **Dead-Letter Processing (DLQ):** Captures exhausted retries for administrative review and safe replay without modifying the original correlation ID.

---

## 5. Technology Stack

* **Language & Framework:** Python 3.11, FastAPI, Pydantic v2
* **Persistence & ORM:** MariaDB 11.4, SQLAlchemy 2.0, PyMySQL, Alembic
* **Testing & Quality:** Pytest, HTTPX, Ruff
* **Containerization:** Docker Desktop, Docker Compose
* **External Integrations:** ServiceNow (RESTMessageV2 / Flow Designer), Mock Provider System

---

## 6. Implementation Roadmap & Current Status

| Phase | Description | Status |
| :--- | :--- | :--- |
| **Phase 1** | Clean-slate environment baseline, Docker Compose, \GET /health\ | **Completed** |
| **Phase 2** | MariaDB 11 setup, Alembic migrations, Hierarchy schema | **Completed** |
| **Phase 3** | Synthetic seed data, Master Data REST APIs (\/api/v1/hospitals\) | **Completed** |
| **Phase 4** | Inbound Case Ingestion API (\POST /api/v1/cases\) with Idempotency | **Completed** |
| **Phase 5** | Mock Provider System (\:9000\) with fault injection & simulation | **Completed** |
| **Phase 6** | Reliability: Outbox tables, Integration Worker, Retries & DLQ | *Up Next* |
| **Phase 7** | Analytics facts and reporting repository abstraction | Pending |
| **Phase 8** | Model Context Protocol (MCP) server integration | Pending |

---

## 7. Local Development Quickstart

### Prerequisites
* Windows 10/11, macOS, or Linux
* Docker Desktop installed and running
* VS Code

### Running the Services
\\\powershell
# 1. Clone and enter directory
cd janswasthya-connect

# 2. Start all container services
docker compose up -d --build

# 3. Check running containers
docker compose ps
\\\

### Active Endpoints & Ports
* **Master Data Service:** [http://localhost:8001/docs](http://localhost:8001/docs)
* **Case Integration Service:** [http://localhost:8002/docs](http://localhost:8002/docs)
* **Mock Provider System:** [http://localhost:9000/docs](http://localhost:9000/docs)
* **Adminer (Database UI):** [http://localhost:8080](http://localhost:8080)
  * System: \MySQL\, Server: \mariadb\, User: \janswasthya_user\, DB: \janswasthya\

### Running the Test Suites
\\\powershell
# Master Data Service Tests
docker compose exec master-data-service pytest -v

# Case Integration Service Tests
docker compose exec case-integration-service pytest -v

# Mock Provider System Tests
docker compose exec mock-provider-system pytest -v
\\\

