# CloudPulse AI — FinOps Architecture & Asset Intelligence

This document specifies the FinOps cost governance architecture, continuous cloud spend tracking, FinOps data flow pipeline, asset inventory lifecycle engine, and topological blast-radius calculation.

---

## 1. FinOps Data Flow Architecture

The FinOps engine continuously ingests cloud cost items, evaluates budget policies, detects cost anomalies, and generates right-sizing remediation recommendations.

```mermaid
flowchart TB
    subgraph IngestionLayer["Cloud Cost Ingestion Layer"]
        AWSBill["AWS Cost Explorer API / Fixture"]
        GCPBill["GCP BigQuery Export / Fixture"]
        AzureBill["Azure Cost Management / Fixture"]
        ResourceData["Cloud Resource Inventory Telemetry"]
    end

    subgraph FinOpsCore["FinOps Governance Core Engine"]
        CostEngine["Cost Normalization & Aggregation Engine<br/>(backend/app/services/cost_engine.py)"]
        FinOpsGov["FinOps Policy Enforcement Engine<br/>(backend/app/services/finops_governance_engine.py)"]
        AnomalyDetect["Cost Anomaly Detection Engine"]
    end

    subgraph AnalyticsAI["FinOps Analytics & AI Recommendations"]
        WasteDetect["Idle & Unattached Resource Waste Scanner"]
        RightSizing["VM & DB Right-Sizing Calculation"]
        FinOpsAI["FinOps AI Advisor (Gemini / Local Engine)"]
    end

    subgraph ActionLayer["Action & Notification Layer"]
        BudgetAlerts["Budget Violation Alerts & Email Notifications"]
        RemediationPlan["AIOps Remediation Plan (Auto-Stop Idle VMs)"]
        ExecutiveReport["FinOps Executive Spend Report (PDF Export)"]
    end

    AWSBill --> CostEngine
    GCPBill --> CostEngine
    AzureBill --> CostEngine
    ResourceData --> CostEngine

    CostEngine --> FinOpsGov
    CostEngine --> AnomalyDetect

    FinOpsGov --> WasteDetect
    FinOpsGov --> RightSizing
    
    WasteDetect --> FinOpsAI
    RightSizing --> FinOpsAI
    AnomalyDetect --> FinOpsAI

    FinOpsAI --> BudgetAlerts
    FinOpsAI --> RemediationPlan
    FinOpsAI --> ExecutiveReport
```

---

## 2. Enterprise Cloud Asset Intelligence & Inventory

The Asset Intelligence Engine (`backend/app/services/asset_intelligence_engine.py`) aggregates multi-cloud resources across AWS, GCP, Azure, and Kubernetes into a unified inventory.

### Key Capabilities:
- **Resource Lifecycle Classification**: Categorizes assets as `ACTIVE`, `IDLE`, `DEGRADED`, `ORPHANED`, or `DECOMMISSIONED`.
- **Waste Identification**: Automatically flags unattached EBS volumes, unassociated Elastic IPs, idle load balancers, and underutilized EC2 instances (< 2% CPU average).
- **Security & Governance Risk Scoring**: Assigns a normalized risk score (0-100) based on patch status, open security group ports, and compliance policy violations.

---

## 3. Cloud Topology & Blast-Radius Engine

The Cloud Topology Engine (`backend/app/services/cloud_topology_engine.py`) constructs a directed graph representing infrastructure component dependencies across regions, clusters, databases, and microservices.

```mermaid
graph TD
    LB["Load Balancer (us-east-1)"] --> Gateway["api-gateway Pods"]
    Gateway --> AuthSvc["auth-service"]
    Gateway --> PaymentSvc["payment-service"]
    AuthSvc --> RedisCache[("Redis Session Cluster<br/>[CRITICAL DEPENDENCY]")]
    PaymentSvc --> DBPostgres[("Aurora PostgreSQL Primary<br/>[SINGLE POINT OF FAILURE]")]
    PaymentSvc --> StripeAPI["External Stripe Gateway"]

    classDef spof fill:#ff4d4d,stroke:#333,stroke-width:2px,color:#fff;
    class DBPostgres,RedisCache spof;
```

### Deterministic Blast-Radius Calculation:
When an engineer triggers a failure simulation (`POST /api/v1/topology/simulate-failure`), the engine calculates the topological blast radius:
1. **Graph Traversal**: Identifies all direct and transitive downstream dependencies.
2. **Blast Impact Rating**: Classifies severity as `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW` based on node criticality scores.
3. **Single Point of Failure (SPOF) Detection**: Flags nodes that have no redundant failover replicas.
4. **Safety Guards**: All failure simulations carry mandatory `"SIMULATION ONLY"` execution flags, ensuring live production infrastructure is never altered during testing.
