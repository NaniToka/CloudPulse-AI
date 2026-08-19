# CloudPulse AI — Enterprise Documentation Hub & Wiki Index

Welcome to the **CloudPulse AI** official technical documentation hub. This documentation suite provides deep-dive architectural specifications, API references, deployment playbooks, and security guides for engineers, SREs, administrators, and contributors.

---

## 📖 Quick Navigation

| # | Documentation Guide | Description |
| :--- | :--- | :--- |
| **1** | [**System Architecture**](architecture.md) | High-level system design, backend component structure, frontend structure, and request/data flow. |
| **2** | [**Tech Stack & Feature Overview**](tech-stack-and-features.md) | Deep dive into the technologies used and a comprehensive feature breakdown of all 38 backend modules and 36 frontend views. |
| **3** | [**Local Setup & Deterministic Demo Mode**](local-setup-and-demo-mode.md) | Step-by-step local development setup, complete environment variables reference table, and Demo Mode vs Live Cloud comparison. |
| **4** | [**Docker Setup & Production Deployment**](docker-and-deployment.md) | Docker Compose configurations (Dev/Prod), Kubernetes manifests deployment guide, production hardening checklist, and operations. |
| **5** | [**Database & Alembic Migrations**](database-and-migrations.md) | Relational database schema, Async ORM models, and the 16 Alembic migration history breakdown (`0001`–`0016`). |
| **6** | [**Authentication & RBAC Architecture**](auth-and-rbac.md) | Multi-tenant organization isolation, JWT authentication token lifecycle, password hashing, and granular RBAC permissions. |
| **7** | [**API Reference Documentation**](api-documentation.md) | REST API endpoints index across all 38 route groups, WebSockets metric streaming API, and Kubernetes health probes. |
| **8** | [**AI Architecture & AI Security**](ai-architecture-and-security.md) | Google Gemini LLM reasoning, ChromaDB RAG vector search, local SRE deterministic fallback engine, and AI security posture. |
| **9** | [**FinOps & Asset Intelligence Architecture**](finops-and-asset-intelligence.md) | FinOps cost governance, cost anomaly detection, FinOps data flow, asset inventory, and topological blast-radius calculation. |
| **10** | [**Kubernetes Intelligence & Autonomous AIOps**](kubernetes-and-aiops.md) | Kubernetes container telemetry, AIOps incident correlation, predictive anomaly engine, and autonomous self-healing closed loop. |
| **11** | [**Testing, Quality & CI/CD**](testing-and-cicd.md) | Pytest async test suite, Ruff/Bandit/ESLint quality gates, and GitHub Actions CI/CD pipelines. |
| **12** | [**Troubleshooting & Operations**](troubleshooting.md) | Operational playbooks, container diagnostics, database recovery steps, common error resolution, and FAQs. |

---

## 🎯 Project At A Glance

- **Repository**: `CloudPulse-AI`
- **Backend**: FastAPI 0.111, Python 3.12, SQLAlchemy 2.0 (AsyncSession), Alembic, Pydantic v2.
- **Frontend**: React 18, TypeScript 5.4, Vite 5, TailwindCSS 3.4, TanStack React Query, Zustand.
- **Data Stores**: PostgreSQL 15 (Relational DB), Redis 7 (Cache & Execution Locks), ChromaDB 0.5.5 (Vector Store).
- **AI Services**: Google Gemini 1.5 API (`google-generativeai`) with automatic fallback to an in-process deterministic SRE engine.
- **Observability**: OpenTelemetry tracing, sub-second WebSockets streaming, Prometheus metrics exposition.
- **License**: MIT Open Source.
