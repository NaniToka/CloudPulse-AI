# CloudPulse AI — API Documentation & Endpoints Reference

This document provides a reference guide for all **38 REST API endpoint route groups** registered under `/api/v1`, the real-time WebSockets metric streaming interface, and system health probes.

---

## 1. Interactive OpenAPI / Swagger Documentation

When the backend FastAPI application is running, full interactive OpenAPI schemas and API testing interfaces are available at:

- 📖 **Swagger UI**: `http://localhost:8000/docs`
- 📘 **ReDoc UI**: `http://localhost:8000/redoc`
- 📄 **Raw OpenAPI JSON Spec**: `http://localhost:8000/openapi.json`

---

## 2. API Endpoint Groups Index (38 Route Modules)

All endpoints require a valid Bearer JWT header except public auth and system probes:
`Authorization: Bearer <your_access_token>`

| Tag / Route Group | Prefix | Key Endpoints & Functionality |
| :--- | :--- | :--- |
| **`Authentication`** | `/api/v1/auth` | `POST /login` — User login & JWT token pair generation.<br/>`POST /register` — New account registration.<br/>`POST /refresh` — Access token refresh.<br/>`POST /logout` — Token revocation in Redis blocklist. |
| **`System`** | `/health`, `/ready`, `/metrics` | `GET /health` — Application & dependency liveness probe.<br/>`GET /ready` — K8s readiness probe.<br/>`GET /metrics` — Prometheus metrics exposition. |
| **`AI Copilot`** | `/api/v1/ai` | `POST /chat` — Non-streaming AI copilot query.<br/>`POST /stream` — SSE streaming AI copilot response. |
| **`Log Analyzer`** | `/api/v1/logs` | `POST /analyze` — AI log snippet root cause analysis.<br/>`GET /clusters` — Error log pattern clustering.<br/>`GET /ingest` — Live server log ingestion stream. |
| **`Cost Optimizer`** | `/api/v1/cost` | `GET /summary` — Cloud spend breakdown.<br/>`GET /idle-resources` — Unattached volume & idle VM waste.<br/>`GET /recommendations` — Right-sizing & RI savings. |
| **`Incident Management`** | `/api/v1/incidents` | `GET /` — List incidents with filters.<br/>`POST /` — Create new incident ticket.<br/>`GET /{id}/rca` — Retrieve AI Root Cause Analysis.<br/>`POST /{id}/acknowledge` — Assign and acknowledge. |
| **`Predictive Analytics`** | `/api/v1/predictions` | `GET /anomalies` — Machine learning anomaly predictions.<br/>`GET /capacity` — CPU/Memory/Disk exhaustion forecasting. |
| **`Real-Time Observability`**| `/api/v1/metrics` | `GET /query` — Query time-series telemetry metrics.<br/>`WS /ws` — WebSockets sub-second metric streaming. |
| **`Service Dependencies`** | `/api/v1/dependencies` | `GET /graph` — Multi-service dependency node graph.<br/>`GET /root-cause` — Downstream failure origin calculation. |
| **`Distributed Tracing`** | `/api/v1/traces` | `GET /` — Search OpenTelemetry distributed trace spans.<br/>`GET /{trace_id}` — Trace waterfall tree hierarchy. |
| **`RAG Infrastructure Chat`**| `/api/v1/chat` | `POST /query` — Query vector RAG memory with evidence citations. |
| **`Auto Remediation Center`**| `/api/v1/runbooks` | `GET /` — List available automated SRE runbooks.<br/>`POST /{id}/execute` — Trigger automated runbook action. |
| **`AI Security & Compliance`**| `/api/v1/security` | `GET /scans` — CSPM security posture evaluation.<br/>`GET /findings` — Active cloud vulnerability risk scores. |
| **`Autonomous AIOps Agent`**| `/api/v1/aiops` | `GET /status` — 6-phase autonomous AIOps loop state.<br/>`POST /trigger-loop` — Manual AIOps cycle trigger. |
| **`SRE Reliability Center`** | `/api/v1/sre` | `GET /overview` — SRE reliability metrics, toil, post-mortems. |
| **`Cloud Governance`** | `/api/v1/governance` | `GET /compliance` — Security framework evaluations (CIS, SOC2). |
| **`FinOps Governance`** | `/api/v1/finops` | `GET /budgets` — Budget status and policy enforcement. |
| **`Executive Command Center`**| `/api/v1/executive` | `GET /dashboard` — Executive cloud health & risk scorecards. |
| **`Autonomous Self-Healing`**| `/api/v1/autonomous` | `GET /policies` — Autonomy safety levels & maintenance windows. |
| **`SLO Intelligence`** | `/api/v1/slo` | `GET /definitions` — Service Level Objectives & error budgets. |
| **`Command Center`** | `/api/v1/command-center`| `GET /overview` — Consolidated executive command metrics. |
| **`Service Reliability 2.0`** | `/api/v1/reliability` | `GET /analytics` — End-to-end reliability analytics. |
| **`AIOps Action Center`** | `/api/v1/remediation` | `GET /plans` — Active remediation plans & rollbacks. |
| **`Asset Intelligence`** | `/api/v1/assets` | `GET /inventory` — Multi-cloud asset tracking & risk scores. |
| **`Topology & Blast Radius`**| `/api/v1/topology` | `GET /graph` — Multi-cloud infrastructure graph.<br/>`POST /simulate-failure` — Topological blast radius calculation. |
| **`Platform Health`** | `/api/v1/platform` | `GET /readiness` — Production readiness scorecards. |
| **`Kubernetes Intelligence`**| `/api/v1/kubernetes` | `GET /clusters`, `GET /pods`, `GET /deployments`. |
| **`Multi-Cloud Observability`**| `/api/v1/cloud` | `GET /summary`, `GET /accounts`, `GET /resources`. |
| **`Digital Twin`** | `/api/v1/twin` | `GET /state`, `POST /simulate`. |
| **`Workflow Automation`** | `/api/v1/workflows` | `GET /`, `POST /builder`. |
| **`Unified Telemetry`** | `/api/v1/telemetry` | `POST /ingest`, `GET /stream`. |
| **`Users & Organizations`** | `/users`, `/organizations`, `/teams`, `/projects`, `/members`, `/servers`, `/alerts`, `/notifications`. |

---

## 3. WebSockets Sub-Second Metric Streaming API

CloudPulse AI provides real-time WebSockets streaming for live dashboard monitoring:

- **WebSocket URL**: `ws://localhost:8000/api/v1/metrics/ws`
- **Protocol**: WS / WSS
- **Message Format**: JSON payload streamed at sub-second intervals (every 1000ms):

```json
{
  "timestamp": 1786380450.12,
  "metrics": {
    "cpu_utilization_percent": 68.4,
    "memory_utilization_percent": 74.2,
    "disk_io_bytes_per_sec": 1450200,
    "network_throughput_mbps": 42.8,
    "requests_per_second": 1240,
    "p99_latency_ms": 142.5,
    "error_rate_percent": 0.04
  },
  "status": "HEALTHY"
}
```

---

## 4. Standard HTTP Response & Error Schemas

All REST endpoints return standardized JSON payloads:

### Successful Response Format (HTTP 200 / 201)
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response Format (HTTP 4xx / 5xx)
```json
{
  "detail": "Detailed human-readable error description",
  "error_code": "ERR_RESOURCE_NOT_FOUND",
  "status_code": 404,
  "timestamp": "2026-08-19T19:14:20Z"
}
```
