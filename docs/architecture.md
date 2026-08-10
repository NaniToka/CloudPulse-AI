# CloudPulse-AI — Enterprise System Architecture Documentation

## 1. System Architecture Diagram

```mermaid
graph TB
    subgraph Client Layer
        WebBrowser["Web Browser (React SPA)"]
        CLI["CLI / API Consumers"]
    end

    subgraph Ingress & Gateway Layer
        Nginx["Nginx Reverse Proxy (Port 80/443)"]
        SPA_Static["Static Assets (/usr/share/nginx/html)"]
    end

    subgraph Backend Application Layer (FastAPI)
        AuthMW["Security & Correlation Middleware"]
        Router["API Router (/api/v1)"]
        
        subgraph Core Services
            AuthService["Auth & RBAC Service"]
            TelemetryService["Telemetry & Metric Ingestion"]
            IncidentService["Incident & RCA Engine"]
            CostService["FinOps Cost Optimizer"]
            LogService["AI Log Parser & Analyzer"]
            RAGService["RAG Intelligence Pipeline"]
            AIOpsService["Autonomous AIOps Agent"]
            RunbookService["Runbook Automation Service"]
        end
    end

    subgraph Data & Storage Layer
        PostgreSQL[("PostgreSQL 15 (Relational DB)")]
        Redis[("Redis 7 (Cache & Sessions)")]
        ChromaDB[("ChromaDB (Vector Store)")]
    end

    subgraph AI Intelligence Layer
        GeminiAPI["Google Gemini 1.5 API"]
        LocalEngine["Local Deterministic SRE Engine (Fallback)"]
    end

    WebBrowser --> Nginx
    CLI --> Nginx
    Nginx --> SPA_Static
    Nginx -->|Proxy /api/*| AuthMW
    AuthMW --> Router

    Router --> AuthService
    Router --> TelemetryService
    Router --> IncidentService
    Router --> CostService
    Router --> LogService
    Router --> RAGService
    Router --> AIOpsService
    Router --> RunbookService

    AuthService --> PostgreSQL
    AuthService --> Redis
    TelemetryService --> PostgreSQL
    IncidentService --> PostgreSQL
    CostService --> PostgreSQL
    LogService --> PostgreSQL
    RAGService --> ChromaDB
    RAGService --> GeminiAPI
    RAGService -.-> LocalEngine
    LogService --> GeminiAPI
    LogService -.-> LocalEngine
    AIOpsService --> PostgreSQL
    RunbookService --> PostgreSQL
```

---

## 2. Authentication & RBAC Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Engineer
    participant Frontend as React Client
    participant Backend as FastAPI Auth
    participant DB as PostgreSQL
    participant Redis as Redis Cache

    User->>Frontend: Enter credentials (email, password)
    Frontend->>Backend: POST /api/v1/auth/login
    Backend->>DB: Query User record by email
    DB-->>Backend: Return User (hash, salt, role)
    Backend->>Backend: Verify bcrypt password hash
    Backend->>Backend: Generate JWT Access (30m) & Refresh (7d) tokens
    Backend-->>Frontend: Return { access_token, refresh_token, user_profile }
    Frontend->>Frontend: Store tokens in secure state memory

    Note over Frontend,Backend: Authenticated API Requests
    Frontend->>Backend: GET /api/v1/incidents (Authorization: Bearer <token>)
    Backend->>Redis: Check if token is in revocation blocklist
    Redis-->>Backend: Token valid
    Backend->>Backend: Verify JWT signature & extract user_id, role
    Backend->>Backend: Validate RBAC permissions (require_roles)
    Backend->>DB: Execute query scoped to user/tenant
    DB-->>Backend: Return data
    Backend-->>Frontend: HTTP 200 OK with data payload
```

---

## 3. RAG Intelligence Pipeline Flow

```mermaid
sequenceDiagram
    autonumber
    actor SRE as SRE Engineer
    participant UI as RAG Chat UI
    participant RAG as RAG Service
    participant VectorDB as ChromaDB Vector Store
    participant AI as Gemini AI / Local Engine
    participant DB as Chat History DB

    SRE->>UI: "Why is api-gateway P99 latency spiking?"
    UI->>RAG: POST /api/v1/rag/query
    RAG->>RAG: Preprocess query & extract entity keywords
    RAG->>VectorDB: Semantic vector search on metrics, traces, incidents
    VectorDB-->>RAG: Return top-K relevant context documents
    RAG->>RAG: Construct grounded prompt with telemetry evidence
    
    alt Gemini API Key Configured
        RAG->>AI: Send prompt to Gemini 1.5 Pro
        AI-->>RAG: Return structured JSON (answer, citations, root cause)
    else Fallback / Demo Mode
        RAG->>AI: Invoke Local SRE Deterministic Inference Engine
        AI-->>RAG: Return grounded diagnostics & recommendations
    end

    RAG->>DB: Persist query & response in session history
    RAG-->>UI: Return RAGQueryResponse with citations & evidence
    UI-->>SRE: Render Markdown diagnostics, related alerts, and action items
```

---

## 4. Incident Lifecycle & Correlation Engine

```mermaid
stateDiagram-v2
    [*] --> DETECTED: Metric anomaly or log error threshold breached
    DETECTED --> CORRELATED: Multi-service topology correlation & deduplication
    CORRELATED --> INVESTIGATING: SRE engineer assigned / alerted
    INVESTIGATING --> IDENTIFIED: AI Root Cause Analysis (RCA) completed
    IDENTIFIED --> MITIGATING: Automated runbook approved or scaling action dispatched
    MITIGATING --> RESOLVED: Telemetry returns within SLA baseline thresholds
    RESOLVED --> CLOSED: Post-mortem generated and incident archived
    CLOSED --> [*]
```

---

## 5. Deployment Topology

```mermaid
graph LR
    subgraph Host / Cloud Instance
        subgraph Docker Bridge Network
            FE[frontend:80<br/>Nginx SPA Proxy]
            BE[backend:8000<br/>FastAPI ASGI]
            PG[postgres:5432<br/>PostgreSQL 15]
            RD[redis:6379<br/>Redis 7]
            CH[chromadb:8000<br/>Chroma Vector DB]
        end
    end

    HostPort80[Port 80 / 5173] --> FE
    FE -->|HTTP Proxy| BE
    BE --> PG
    BE --> RD
    BE --> CH
```
