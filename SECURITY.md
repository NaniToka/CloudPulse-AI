# Security Policy

## 🔒 Security Overview

CloudPulse AI takes security seriously. As an enterprise-grade cloud observability and AI engine, maintaining tenant data isolation, API security, and secure LLM inference is our highest priority.

---

## 🛡️ Supported Versions

We actively release security patches and updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| v1.x    | :white_check_mark: |
| < v1.0  | :x:                |

---

## 📩 Reporting Vulnerabilities

If you discover a potential security vulnerability in CloudPulse AI, please **do not** open a public issue.

Instead, please report it responsibly by emailing **security@cloudpulse.ai** or using GitHub Private Vulnerability Reporting.

### Please Include:
- Description of the vulnerability and operational impact
- Step-by-step proof-of-concept (PoC) or script to reproduce
- Affected components (e.g. JWT Auth, RBAC Middleware, Gemini RAG, WebSockets)

### Our Response Timeline:
- **Acknowledgement**: Within 24 hours
- **Assessment**: Within 72 hours
- **Patch Release**: Within 7 business days for Critical/High severity vulnerabilities

---

## 🔐 Security Architecture Practices

- **Tenant Data Isolation**: Multi-tenant database foreign-key constraints & RBAC authorization middleware.
- **Secrets & Credentials**: No hardcoded API keys or credentials; managed via environment variables.
- **Authentication**: JWT access tokens (15-min expiration) + secure HTTP-only refresh tokens.
- **Input Validation**: Pydantic v2 strict schema parsing on all API payloads.
