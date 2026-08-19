# CloudPulse AI — Docker Setup, Production Deployment & Troubleshooting Guide

This document provides complete instructions for containerized deployment using Docker Compose, enterprise Kubernetes production deployment manifests, production hardening checklists, and an operational troubleshooting playbook.

---

## 1. Docker Setup (One-Command Launch)

CloudPulse AI provides multi-container configurations for both local development and production environments.

### 1.1 Development Stack (`docker-compose.yml`)

The development Compose file orchestrates five core containers: `frontend`, `backend`, `postgres`, `redis`, and `chromadb`.

```bash
# 1. Clone repository and navigate to root directory
git clone https://github.com/NaniToka/CloudPulse-AI.git
cd CloudPulse-AI

# 2. Copy environment template
cp .env.example .env

# 3. Launch all containers in detached mode
docker compose up --build -d

# 4. Check service status
docker compose ps
```

#### Development Ports Mapping:
- 🌐 **Frontend React SPA**: `http://localhost:5173` (or `http://localhost:80`)
- ⚡ **Backend FastAPI API**: `http://localhost:8000`
- 📖 **Swagger OpenAPI Docs**: `http://localhost:8000/docs`
- 🗄️ **PostgreSQL Database**: `localhost:5432`
- 🔴 **Redis Cache**: `localhost:6379`
- 🔍 **ChromaDB Vector Store**: `localhost:8001`

---

### 1.2 Production Stack (`docker-compose.production.yml`)

The production stack uses production-ready Nginx frontend proxy containers, multi-worker uvicorn backend instances, volume persistence, and isolated internal networks.

```bash
# Launch production stack
docker compose -f docker-compose.production.yml up -d --build

# Verify health status
docker compose -f docker-compose.production.yml ps
```

---

## 2. Production Kubernetes Deployment Guide

The repository includes production-ready Kubernetes manifests located in `deployment/kubernetes/`:

```
deployment/kubernetes/
├── namespace.yaml                # Namespace `cloudpulse-ai`
├── configmap.yaml                # Non-sensitive runtime variables
├── secrets.yaml                  # Base64 encrypted secrets (JWT, DB passwords)
├── postgres-statefulset.yaml     # Persistent PostgreSQL StatefulSet & PV/PVC
├── redis-deployment.yaml         # Redis cache deployment & service
├── backend-deployment.yaml       # FastAPI backend deployment (Multi-replica)
├── frontend-deployment.yaml      # Nginx React frontend deployment
├── services.yaml                 # ClusterIP & NodePort service definitions
├── ingress.yaml                  # Nginx Ingress Controller routing rules
└── hpa.yaml                      # Horizontal Pod Autoscaler (HPA) policies
```

### Deployment Steps:

```bash
# 1. Create dedicated namespace
kubectl apply -f deployment/kubernetes/namespace.yaml

# 2. Apply ConfigMaps and Secrets
kubectl apply -f deployment/kubernetes/configmap.yaml
kubectl apply -f deployment/kubernetes/secrets.yaml

# 3. Deploy Stateful databases
kubectl apply -f deployment/kubernetes/postgres-statefulset.yaml
kubectl apply -f deployment/kubernetes/redis-deployment.yaml

# 4. Deploy Backend and Frontend microservices
kubectl apply -f deployment/kubernetes/backend-deployment.yaml
kubectl apply -f deployment/kubernetes/frontend-deployment.yaml

# 5. Expose Services and Ingress Routing
kubectl apply -f deployment/kubernetes/services.yaml
kubectl apply -f deployment/kubernetes/ingress.yaml
kubectl apply -f deployment/kubernetes/hpa.yaml

# 6. Verify cluster pod rollout
kubectl get pods -n cloudpulse-ai -o wide
```

---

## 3. Production Hardening Checklist

When preparing CloudPulse AI for enterprise production environments, enforce the following security controls:

1. **Cryptographic Secret Generation**:
   Generate secure 32-byte hex strings for `SECRET_KEY` and `JWT_SECRET_KEY`:
   ```bash
   openssl rand -hex 32
   ```
2. **CORS Restrictions**:
   Restrict `CORS_ORIGINS` in `.env` to trusted domains:
   ```ini
   CORS_ORIGINS=https://app.cloudpulse.io,https://dashboard.cloudpulse.io
   ```
3. **ASGI Worker Sizing**:
   Configure `uvicorn` workers in `backend/Dockerfile` based on server CPU core count:
   ```dockerfile
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--no-access-log"]
   ```
4. **Database Connection Pooling**:
   Tune SQLAlchemy async pool sizes for high-concurrency loads in production:
   ```python
   engine = create_async_engine(
       settings.DATABASE_URL,
       pool_size=20,
       max_overflow=10,
       pool_pre_ping=True,
   )
   ```
5. **Nginx Security Headers**:
   Ensure Nginx injects HSTS, `X-Frame-Options DENY`, `X-Content-Type-Options nosniff`, and `Content-Security-Policy`.

---

## 4. Operational Probes & Health Checks

CloudPulse AI exposes Kubernetes-compatible health endpoints:

### Liveness Probe (`GET /health`)
Validates app responsiveness and database/redis connectivity.
```json
{
  "status": "ok",
  "app": "CloudPulse AI",
  "version": "1.0.0",
  "env": "production",
  "dependencies": {
    "database": "healthy",
    "redis": "healthy",
    "ai": "gemini-cloud-ai"
  }
}
```

### Readiness Probe (`GET /ready`)
Validates container readiness to receive incoming web traffic. Returns HTTP 503 if critical dependencies are unreachable.

### Prometheus Metrics Endpoint (`GET /metrics`)
Exposes formatted Prometheus metrics (`cloudpulse_http_requests_total`, `cloudpulse_request_duration_seconds`).

---

## 5. Troubleshooting Playbook

### 5.1 Inspect Container Logs
```bash
# View live backend logs
docker compose logs -f backend

# View frontend proxy logs
docker compose logs -f frontend

# View database logs
docker compose logs -f postgres
```

### 5.2 Reset Database & Re-seed Synthetic Fixtures
```bash
# Stop containers and purge named volumes
docker compose down -v

# Re-launch and run Alembic migrations
docker compose up --build -d
```

### 5.3 Common Diagnostic Scenarios

| Symptom | Probable Cause | Remediation |
| :--- | :--- | :--- |
| **`500 Internal Server Error` on Login** | Database table missing or un-migrated. | Run `alembic upgrade head` inside backend container. |
| **`401 Unauthorized` on API Calls** | Expired JWT token or mismatched `SECRET_KEY`. | Re-authenticate at `/api/v1/auth/login` to obtain fresh token. |
| **WebSockets Disconnect (`/metrics/ws`)** | CORS origin blocked or reverse proxy buffer. | Verify `CORS_ORIGINS` includes client URL and Nginx supports WS upgrade headers. |
| **RAG Queries Return Generic Answers** | `GEMINI_API_KEY` missing or invalid quota. | System automatically degrades to local SRE engine. Verify key in `.env`. |
| **PostgreSQL Connection Refused** | Container health check failed or port 5432 occupied. | Verify host port binding with `lsof -i :5432` or inspect `docker compose logs postgres`. |
