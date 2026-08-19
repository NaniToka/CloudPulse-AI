# CloudPulse AI — Troubleshooting & Operations Playbook

This document provides operational diagnostics, container troubleshooting playbooks, database recovery procedures, and resolution steps for common runtime errors.

---

## 1. Operational Diagnostic Commands

### 1.1 Container Status & Logs
```bash
# View all running container statuses
docker compose ps

# Follow backend FastAPI logs
docker compose logs -f backend

# Follow frontend Nginx proxy logs
docker compose logs -f frontend

# Follow PostgreSQL database logs
docker compose logs -f postgres

# Follow Redis cache logs
docker compose logs -f redis
```

---

## 2. Database Recovery & Migration Operations

### 2.1 Re-apply Database Migrations
If database schema changes or new migrations are pulled:
```bash
# Execute inside backend container
docker compose exec backend alembic upgrade head
```

### 2.2 Complete Database Purge & Fresh Seed
To completely reset local development database state and seed fresh synthetic fixtures:
```bash
# Stop stack and remove volume volumes
docker compose down -v

# Re-launch containers and build fresh state
docker compose up --build -d
```

---

## 3. Common Error Resolution Guide

| Error Message / Symptom | Root Cause | Immediate Resolution Step |
| :--- | :--- | :--- |
| **`sqlalchemy.exc.OperationalError: Connection refused`** | PostgreSQL container is not running or host port 5432 is occupied. | Run `docker compose ps` to check container status. Clear host port with `lsof -i :5432` if occupied natively. |
| **`401 Unauthorized: Could not validate credentials`** | Expired JWT token or mismatched `SECRET_KEY` in environment. | Log out and re-authenticate via `/api/v1/auth/login`. Verify `SECRET_KEY` in `.env` matches between restarts. |
| **`WebSocket connection to 'ws://...' failed`** | CORS origin mismatch or missing WS upgrade headers in reverse proxy. | Verify `CORS_ORIGINS` in `.env` includes the client origin. Check Nginx config includes `Upgrade` and `Connection` headers. |
| **`RuntimeError: GEMINI_API_KEY is not configured`** | `GEMINI_API_KEY` is empty while calling Gemini directly. | The application handles this gracefully by switching to the Local SRE Engine. Set `GEMINI_API_KEY` in `.env` if live LLM reasoning is desired. |
| **`alembic.util.exc.CommandError: Target database is not up to date`** | Unapplied database migrations exist in `alembic/versions/`. | Run `alembic upgrade head` from the `backend` directory or container shell. |
| **`ModuleNotFoundError: No module named 'app'`** | Python PYTHONPATH missing backend root directory. | Run python commands from within `backend/` directory or run `export PYTHONPATH=$PYTHONPATH:$(pwd)`. |

---

## 4. FAQ & Operations Reference

### Q: Can I run CloudPulse AI without an internet connection?
**Yes!** Set `DEMO_MODE=true` and leave `GEMINI_API_KEY` blank. The system runs completely offline using the built-in deterministic SRE inference engine and local ChromaDB vector store.

### Q: How do I change the default admin password?
Log into the platform as `admin@cloudpulse.io` (default password: `Password123!`), navigate to **Settings** (`/settings`), and update your account password.

### Q: Where are vector embeddings stored?
Vector embeddings are persisted locally on disk inside the `chroma_db_data/` directory.
