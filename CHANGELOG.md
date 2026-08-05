# Changelog

All notable changes to **CloudPulse AI** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.0.0] - 2026-08-06

### Added
- **Multi-Tenant Enterprise SaaS Architecture**:
  - `Organization`, `Team`, `Project`, `OrganizationMember`, `Invitation`, and `AuditLog` database models and CRUD repository.
  - Granular Role-Based Access Control (RBAC) middleware for `Owner`, `Admin`, `Manager`, `Engineer`, and `Viewer` across 9 permissions.
  - Organization & Workspace Project navbar switchers in React UI.
  - Interactive Granular Permission Matrix editor & security audit trail timeline.
- **Autonomous AIOps Agent Center**:
  - 6-phase Autonomous Agent Loop (`Observe ➔ Detect ➔ Analyze ➔ Plan ➔ Recommend ➔ Verify`).
  - Cross-telemetry correlation engine powered by Google Gemini API.
  - Human-in-the-loop explainable AI action approval drawer with CLI candidates.
- **AI Security & Cloud Compliance Center**:
  - 9 automated cloud security domain scanners.
  - Compliance framework scorecards (CIS, ISO 27001, SOC 2, NIST, PCI-DSS, HIPAA, GDPR).
  - Provider x Severity Risk Heatmap matrix & Wiz-style finding detail drawer.
- **AI Runbook Generator & Auto Remediation Center**:
  - Automated executable runbook generation for infrastructure incidents.
  - CLI/Kubernetes/Terraform step execution timeline.
- **AI Infrastructure Chat (RAG)**:
  - ChromaDB vector store engine indexing metrics, logs, traces, incidents, alerts, and cost reports across 6 collections.
- **Distributed Tracing Platform**:
  - OpenTelemetry trace & span visualization across microservice request cascades.
  - Service Map topology & latency waterfall graphs.
- **Real-Time Observability Engine**:
  - WebSocket streaming metrics engine for Datadog / Grafana style sub-second telemetry updates.
- **Predictive Incident Detection Engine**:
  - Machine learning anomaly forecasting predicting outages before occurrence.
- **AI Cloud Cost Optimizer**:
  - FinOps spend analytics, monthly run-rate forecasts, and actionable cost recommendations.
- **AI Log Analyzer**:
  - Automated log parsing, root cause analysis, and severity classification.
- **Incident Management Platform**:
  - Incident lifecycle management with severity assignment, engineer routing, and AI post-mortems.
- **Enterprise Core Dashboard & Authentication**:
  - Glassmorphic dashboard UI with dark mode, system status indicators, JWT auth with refresh token rotation.
