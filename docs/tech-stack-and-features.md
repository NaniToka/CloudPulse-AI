# CloudPulse AI — Tech Stack & Feature/Module Overview

This document presents a comprehensive matrix of the technologies powering **CloudPulse AI** and an exhaustive feature and module overview covering the 38 backend API router endpoints and 36 frontend view pages.

---

## 1. Technology Stack Matrix

| Layer | Component | Version / Library | Purpose & Implementation Details |
| :--- | :--- | :--- | :--- |
| **Backend Core** | FastAPI | 0.111.0 | Asynchronous ASGI web framework with automatic OpenAPI spec generation and Pydantic validation. |
| **Backend Runtime** | Python | 3.12+ | Execution environment using modern type hints (`X \| None`), `datetime.UTC`, and async/await syntax. |
| **Database ORM** | SQLAlchemy | 2.0.30 | Async ORM utilizing `AsyncSession` and `asyncpg` driver for non-blocking database queries. |
| **Database Migrations**| Alembic | 1.13.1 | Database schema versioning supporting async migrations (`0001` through `0016`). |
| **Relational Database**| PostgreSQL | 15.0 | Primary persistence store for users, organizations, incidents, SLOs, policies, and runbooks. |
| **Caching & Locking** | Redis | 7.0 (redis-py 5.0) | High-performance session store, token revocation blocklist, execution lock manager, and metrics cache. |
| **Vector Store** | ChromaDB | 0.5.5 | Embedded vector database storing semantic embeddings for telemetry RAG infrastructure chat. |
| **AI LLM API** | Google Gemini | 1.5 Pro / Flash | Generative AI engine for root-cause analysis, runbook synthesis, cost recommendations, and chat. |
| **Local AI Fallback** | Deterministic Engine | In-Process Python | Built-in SRE rule-based inference engine that executes when `GEMINI_API_KEY` is not provided or in offline mode. |
| **Logging & Security** | Structlog / Passlib | 24.1.0 / 1.7.4 | Structured JSON logging with correlation ID tracing and BCrypt password hashing. |
| **Frontend Core** | React | 18.3.1 | Component-driven user interface built with TypeScript and Vite production bundler. |
| **Frontend Language** | TypeScript | 5.4.5 | Strict type-checked language layer (`tsc --noEmit`) preventing runtime type errors. |
| **Styling & Icons** | Tailwind CSS / Lucide | 3.4.1 / Lucide React | Modern dark-mode glassmorphic design system with responsive utility classes and icon set. |
| **State & Async Query**| TanStack Query / Zustand| 5.28 / 4.5 | Server-state caching, invalidation, and lightweight global client store (`authStore`, `uiStore`). |
| **Live Telemetry** | WebSockets | Native WS | Sub-second metric streaming for real-time CPU, Memory, Network, RPS, and P99 latency charts. |
| **Distributed Tracing**| OpenTelemetry | Standard | Trace context propagation (`traceparent`), span collection, and waterfall trace view visualization. |
| **Containerization** | Docker / Compose | 24.0+ / v2.20+ | Multi-stage Dockerfiles (`backend/Dockerfile`, `frontend/Dockerfile`) and compose orchestration files. |

---

## 2. Backend Router Modules Overview (`app/api/v1/endpoints/`)

The backend API contains 38 registered router groups under `/api/v1`:

1. **`auth.py` (`/auth`)**: User login, registration, token refresh, logout, and password management.
2. **`telemetry.py` (`/telemetry`)**: Unified telemetry ingestion platform for metrics, logs, and spans.
3. **`twin.py` (`/twin`)**: Digital Twin infrastructure state model and failure simulation studio.
4. **`workflows.py` (`/workflows`)**: Workflow automation engine for multi-step incident remediation pipelines.
5. **`kubernetes.py` (`/kubernetes`)**: K8s cluster telemetry, namespace explorer, Pod metrics, and Deployment status.
6. **`cloud.py` (`/cloud`)**: Multi-cloud dashboard, cloud accounts connector status, and resource explorer.
7. **`users.py` (`/users`)**: User profile management, avatar updates, and user preference settings.
8. **`organizations.py` (`/organizations`)**: Multi-tenant Organization creation, settings, and subscription plans.
9. **`teams.py` (`/teams`)**: Departmental team scoping, team assignments, and member management.
10. **`projects.py` (`/projects`)**: Scoped project spaces for isolation of infrastructure monitoring assets.
11. **`servers.py` (`/servers`)**: Infrastructure server inventory, health status, CPU/Memory load, and metadata.
12. **`alerts.py` (`/alerts`)**: System monitoring alert rules, active alert triggers, and silence configurations.
13. **`notifications.py` (`/notifications`)**: User notification inbox, unread counts, and multi-channel notification dispatch.
14. **`members.py` (`/members`)**: Organization and Team membership management and role assignments.
15. **`ai.py` (`/ai`)**: AI SRE Copilot endpoint supporting non-streaming and Server-Sent Events (SSE) streaming chat.
16. **`logs.py` (`/logs`)**: AI log analysis, error clustering, log ingestion, and pattern anomaly detection.
17. **`cost.py` (`/cost`)**: Multi-cloud cost tracking, idle resource detection, cost breakdown, and right-sizing recommendations.
18. **`incidents.py` (`/incidents`)**: Incident lifecycle management, AI Root-Cause Analysis (RCA), timeline tracking, and impact evaluation.
19. **`predictions.py` (`/predictions`)**: Machine learning time-series forecasting for CPU, memory, disk, and SLO breach risks.
20. **`metrics.py` (`/metrics`)**: WebSockets metric streaming (`/metrics/ws`) and time-series metric queries.
21. **`dependencies.py` (`/dependencies`)**: Service dependency graph discovery, node mapping, and downstream failure propagation.
22. **`traces.py` (`/traces`)**: OpenTelemetry distributed trace collector, trace search, and span waterfall visualization.
23. **`rag_chat.py` (`/chat`)**: RAG infrastructure chat querying vector-indexed telemetry evidence.
24. **`runbooks.py` (`/runbooks`)**: AI runbook generator, static runbooks, and single-click automated execution.
25. **`security.py` (`/security`)**: CSPM security scanner, vulnerability risk scoring, and compliance posture reports.
26. **`aiops.py` (`/aiops`)**: Autonomous 6-phase AIOps loop agent (`Observe ➔ Detect ➔ Analyze ➔ Plan ➔ Execute ➔ Verify`).
27. **`sre.py` (`/sre`)**: SRE reliability hub, error budget calculations, toil metrics, and incident post-mortems.
28. **`governance.py` (`/governance`)**: Multi-framework security governance evaluation (CIS, ISO 27001, SOC 2, NIST, PCI-DSS, HIPAA, GDPR).
29. **`finops_governance.py` (`/finops`)**: FinOps budget policy enforcement, cost anomaly alerts, and automated spending guardrails.
30. **`executive.py` (`/executive`)**: Executive cloud command center, financial risk burn, health scores, and executive summaries.
31. **`autonomous.py` (`/autonomous`)**: Autonomous cloud self-healing operations, multi-tier safety controls, and maintenance windows.
32. **`slo.py` (`/slo`)**: Enterprise Service Level Objectives (SLOs), Service Level Indicators (SLIs), and error budget exhaustion forecasting.
33. **`command_center.py` (`/command-center`)**: Unified executive operations command center aggregating health, cost, and reliability metrics.
34. **`reliability.py` (`/reliability`)**: Service Reliability Engine 2.0 delivering end-to-end reliability analytics and SLO guardrails.
35. **`remediation.py` (`/remediation`)**: AIOps action & remediation center managing dry-run validations, approvals, and automated rollbacks.
36. **`assets.py` (`/assets`)**: Enterprise asset intelligence tracking resource lifecycle, idle waste, and security risk scores.
37. **`topology.py` (`/topology`)**: Enterprise cloud topology graph, topological blast radius calculation, and SPOF detection.
38. **`platform.py` (`/platform`)**: Platform health, production readiness scorecards, and engineering quality indicators.

---

## 3. Frontend View Pages Breakdown (`src/pages/`)

The frontend application provides 36 distinct view pages organized into logical domain modules:

- **Executive & Management**: Executive Command Center (`/executive`), Operations Command Center (`/command-center`), Main Dashboard (`/dashboard`), Platform Health (`/platform-health`).
- **Cloud Infrastructure & Assets**: Cloud Topology & Blast Radius (`/topology`), Asset Intelligence (`/assets`), Multi-Cloud Dashboard (`/cloud`), Cloud Accounts (`/cloud/accounts`), Cloud Resource Explorer (`/cloud/resources`), Infrastructure (`/infrastructure`), Server Inventory (`/servers`).
- **AIOps & Self-Healing Ops**: Autonomous Operations (`/autonomous`), AIOps Agent Center (`/aiops`), Action & Remediation Center (`/remediation`), Runbook Dashboard (`/runbooks`), Workflow Automation (`/workflows`).
- **FinOps Governance**: Cost Optimizer (`/cost`), FinOps Governance Center (`/finops/governance`).
- **Observability & Intelligence**: Real-Time WebSockets Monitoring (`/monitoring`), Distributed Tracing (`/tracing`), Log Analyzer (`/logs`), Telemetry Intelligence (`/telemetry`), Incidents Center (`/incidents`), SRE Reliability (`/sre`), SLO Intelligence (`/slo`), Service Reliability 2.0 (`/reliability`), Service Dependencies (`/dependencies`), Predictive Analytics (`/predictions`).
- **Kubernetes & Digital Twin**: K8s Overview (`/k8s`), Pod Explorer (`/k8s/pods`), Deployment Explorer (`/k8s/deployments`), Digital Twin (`/twin`), Failure Simulation Studio (`/twin/simulation/:id`).
- **AI Infrastructure & Security**: AI RAG Chat (`/chat`), AI Copilot (`/ai`), Security Center (`/security`), Compliance Governance (`/governance`).
- **Administration & Scoping**: Organization Settings (`/organization`), Settings (`/settings`), Alerts (`/alerts`), User Notifications (`/notifications`).
