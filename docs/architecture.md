# CloudPulse AI — Enterprise System Architecture

This document provides a detailed breakdown of the **CloudPulse AI** system architecture, component relationships, data flow patterns, backend module hierarchy, frontend client structure, and data persistence models.

---

## 1. High-Level System Architecture Diagram

The system follows an event-driven, microservices-ready layered architecture. The React SPA communicates with the FastAPI API Gateway via REST and WebSockets, while the backend orchestrates data across PostgreSQL, Redis, ChromaDB, and Google Gemini API (or the local deterministic fallback engine).

```mermaid
flowchart TB
    subgraph ClientLayer["Frontend Control Plane (React 18 + TypeScript + Vite)"]
        DashboardUI["Executive & Operational Dashboards"]
        TopologyUI["Cloud Topology & Blast Radius Center"]
        AssetUI["Cloud Asset Inventory Center"]
        RemediationUI["AIOps Action & Remediation Center"]
        RAGChatUI["AI Infrastructure Chat (RAG) UI"]
        WSClient["WebSocket Live Streaming Client"]
    end

    subgraph GatewayLayer["FastAPI Gateway & Middleware Layer"]
        Router["API v1 Master Router (/api/v1)"]
        CorsMW["CORS & Compression Middleware"]
        AuthMW["Security & Correlation ID Middleware"]
        RateLimitMW["In-Process Rate Limiter (Token Bucket)"]
        RBAC["Granular RBAC Authorization Engine"]
    end

    subgraph ServiceLayer["Core Domain Services & AI Engines"]
        AuthService["Auth & Tenant Isolation Service"]
        TelemetryService["Unified Telemetry Ingestion Service"]
        TopologyEngine["Cloud Topology & Blast-Radius Engine"]
        AssetEngine["Asset Intelligence & Inventory Engine"]
        IncidentEngine["Incident Correlation & RCA Engine"]
        FinOpsEngine["FinOps Governance & Cost Engine"]
        RemediationEngine["Automated Remediation Engine"]
        RAGEngine["RAG Vector Intelligence Engine"]
        AutonomousEngine["Autonomous Self-Healing Loop Engine"]
    end

    subgraph DataLayer["Persistence & Caching Infrastructure"]
        Postgres[(PostgreSQL 15 Relational DB)]
        Redis[(Redis 7 Cache & Execution Locks)]
        ChromaDB[(ChromaDB 0.5.5 Vector Store)]
    end

    subgraph AILayer["AI & LLM Services Layer"]
        GeminiAPI["Google Gemini 1.5 API"]
        LocalEngine["Local Deterministic SRE Engine (Fallback / Demo)"]
    end

    DashboardUI --> Router
    TopologyUI --> Router
    AssetUI --> Router
    RemediationUI --> Router
    RAGChatUI --> Router
    WSClient <--> Router

    Router --> CorsMW --> AuthMW --> RateLimitMW --> RBAC
    RBAC --> AuthService
    RBAC --> TelemetryService
    RBAC --> TopologyEngine
    RBAC --> AssetEngine
    RBAC --> IncidentEngine
    RBAC --> FinOpsEngine
    RBAC --> RemediationEngine
    RBAC --> RAGEngine
    RBAC --> AutonomousEngine

    AuthService --> Postgres
    AuthService --> Redis
    TelemetryService --> Postgres
    TopologyEngine --> Postgres
    AssetEngine --> Postgres
    IncidentEngine --> Postgres
    FinOpsEngine --> Postgres
    RemediationEngine --> Postgres
    AutonomousEngine --> Redis
    
    RAGEngine --> ChromaDB
    RAGEngine --> GeminiAPI
    RAGEngine -.-> LocalEngine
```

---

## 2. Backend Component Structure

The backend application is built on FastAPI and follows a modular repository pattern with strict separation between routes, services, data models, and database access.

```mermaid
graph TD
    BackendRoot["backend/app/"]
    
    BackendRoot --> Core["core/<br/>• config.py (Pydantic Settings)<br/>• security.py (JWT & Bcrypt)<br/>• middleware.py (Correlation & Rate Limit)<br/>• logging.py (Structlog)"]
    BackendRoot --> API["api/v1/<br/>• router.py (Master v1 Router)<br/>• endpoints/ (38 Domain Endpoints)"]
    BackendRoot --> Models["models/<br/>• 34 SQLAlchemy ORM Models<br/>• Declarative Base & Mixins"]
    BackendRoot --> Schemas["schemas/<br/>• Pydantic v2 Request/Response Validation"]
    BackendRoot --> CRUD["crud/<br/>• Repository Pattern Base CRUD Classes"]
    BackendRoot --> DB["db/<br/>• session.py (AsyncEngine & AsyncSession)<br/>• init_db.py (Database Seeding)"]
    BackendRoot --> Services["services/<br/>• 67 Business Logic & AI Engines<br/>• Gemini API & Local SRE Fallback"]
    BackendRoot --> Telemetry["telemetry/<br/>• OpenTelemetry Exporter & Collectors"]
```

### Key Backend Components:
1. **API Router Layer (`app/api/v1/endpoints/`)**: Contains 38 router modules managing REST routes (`auth`, `incidents`, `topology`, `finops_governance`, `remediation`, etc.).
2. **Business Logic Layer (`app/services/`)**: Contains 67 service modules powering topology calculations, blast radius predictions, AI log parsing, RAG querying, FinOps cost policies, and autonomous self-healing loops.
3. **ORM Models Layer (`app/models/`)**: Defines SQLAlchemy 2.0 async models with table constraints, foreign keys, indexes, and JSON fields.
4. **Database Session Layer (`app/db/session.py`)**: Uses `asyncpg` driver with SQLAlchemy `AsyncSession` for high-concurrency non-blocking database queries.

---

## 3. Frontend Component Structure

The frontend is a single-page application (SPA) built with React 18, TypeScript, Vite, and TailwindCSS. It leverages TanStack React Query for async server-state caching and Zustand for lightweight global UI state.

```mermaid
graph TD
    FrontendRoot["frontend/src/"]
    
    FrontendRoot --> Layouts["layouts/<br/>• AuthLayout.tsx<br/>• DashboardLayout.tsx"]
    FrontendRoot --> Pages["pages/<br/>• 36 Page View Component Folders<br/>• dashboard, topology, assets, finops, etc."]
    FrontendRoot --> Components["components/<br/>• ui/ (Glassmorphic Design System)<br/>• auth/ (Protected & Guest Route Guards)<br/>• topology, assets, remediation, etc."]
    FrontendRoot --> Services["services/<br/>• Axios API Client Services<br/>• Token Interceptors & Error Handlers"]
    FrontendRoot --> Store["store/<br/>• Zustand Global Stores (authStore, uiStore)"]
    FrontendRoot --> Types["types/<br/>• TypeScript Interface Definitions"]
```

### Key Frontend Views (`src/pages/`):
- **Command Center & Executive Operations**: `/executive`, `/command-center`, `/dashboard`
- **Cloud Infrastructure & Topology**: `/topology`, `/assets`, `/cloud`, `/cloud/accounts`, `/cloud/resources`, `/infrastructure`, `/servers`
- **AIOps & Self-Healing Ops**: `/autonomous`, `/aiops`, `/remediation`, `/runbooks`, `/workflows`
- **FinOps & Cost Governance**: `/cost`, `/finops/governance`
- **Observability & Reliability**: `/monitoring`, `/tracing`, `/logs`, `/telemetry`, `/incidents`, `/sre`, `/slo`, `/reliability`, `/dependencies`, `/predictions`
- **Kubernetes & Digital Twin**: `/k8s`, `/k8s/pods`, `/k8s/deployments`, `/twin`, `/twin/simulation/:id`
- **AI Infrastructure Chat & Security**: `/chat`, `/ai`, `/security`, `/governance`
- **Organization & Administration**: `/organization`, `/settings`, `/alerts`, `/notifications`, `/platform-health`

---

## 4. End-to-End Request & Data Flow

When an SRE or executive interacts with CloudPulse AI, requests follow a strictly authenticated and validated pipeline:

```mermaid
sequenceDiagram
    autonumber
    actor User as SRE / Executive
    participant SPA as React Frontend
    participant Gateway as FastAPI Router
    participant Auth as RBAC / JWT Middleware
    participant Service as Domain Engine (e.g. Topology)
    participant Redis as Redis Cache
    participant DB as PostgreSQL DB
    participant AI as Gemini API / Local Fallback Engine

    User->>SPA: Select action (e.g., Run Blast Radius Simulation)
    SPA->>Gateway: POST /api/v1/topology/simulate-failure (Header: Bearer JWT)
    Gateway->>Auth: Extract & Validate JWT token
    Auth->>Redis: Check token revocation blocklist
    Redis-->>Auth: Token valid
    Auth->>Auth: Verify RBAC permissions (`require_roles("OPERATOR", "ADMIN")`)
    Auth-->>Gateway: Context authenticated (user_id, org_id, role)
    
    Gateway->>Service: Dispatch `simulate_topology_failure(node_id)`
    Service->>DB: Fetch infrastructure dependency graph
    DB-->>Service: Return nodes, edges, & telemetry metrics
    Service->>Service: Calculate topological blast-radius score
    
    alt Gemini AI Enabled
        Service->>AI: Request AI strategic recommendation
        AI-->>Service: Return structured AI recommendation
    else Demo / Fallback Mode
        Service->>AI: Invoke Local SRE Deterministic Engine
        AI-->>Service: Return deterministic offline recommendation
    end

    Service-->>Gateway: Return Simulation Result (Blast Radius, SPOFs, AI Advice)
    Gateway-->>SPA: HTTP 200 OK JSON Payload
    SPA-->>User: Render visual graph breakdown & risk alerts
```

---

## 5. Telemetry & Data Storage Strategy

| Data Type | Primary Store | Backup/Cache Store | Purpose |
| :--- | :--- | :--- | :--- |
| **Relational Data** | PostgreSQL 15 | Disk Snapshots | Users, Orgs, Teams, Projects, Incidents, SLOs, Policies, Runbooks |
| **Session & Locks** | Redis 7 | In-Memory Fallback | JWT Revocation list, Execution Locks for remediation, Metric Cache |
| **RAG Embeddings** | ChromaDB 0.5.5 | Local Disk (`chroma_db_data`) | Vector embeddings for logs, metrics, traces, and incident post-mortems |
| **Time-Series Metrics** | Postgres / Redis | Memory Buffer | Live WebSockets streaming metrics (CPU, Memory, Disk, RPS, P99) |
