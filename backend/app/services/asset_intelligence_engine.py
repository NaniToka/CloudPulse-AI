"""
Enterprise Cloud Asset Intelligence Engine.

Provides unified resource discovery, inventory normalization, health scoring,
FinOps cost integration, security risk aggregation, governance compliance evaluation,
topology relationship discovery, and orphaned resource detection across AWS, Azure, GCP, and Kubernetes.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.schemas.assets import (
    AssetDetailResponse,
    AssetOverviewResponse,
    AssetProviderDistributionResponse,
    AssetProviderStat,
    AssetRegionDistributionResponse,
    AssetRegionStat,
    AssetRelationshipItem,
    AssetResourceItem,
    AssetServiceDistributionResponse,
    AssetServiceStat,
    AssetTopologyEdge,
    AssetTopologyNode,
    AssetTopologyResponse,
    AssetTypeDistributionResponse,
    AssetTypeStat,
    OrphanedResourceItem,
    OrphanedResourcesResponse,
)


def get_local_demo_assets() -> list[dict[str, Any]]:
    """Return realistic, deterministic multi-cloud & Kubernetes resource inventory dataset."""
    now_str = datetime.now(UTC).isoformat()
    return [
        # --- AWS Resources ---
        {
            "id": uuid.UUID("11111111-1111-4111-8111-111111111111"),
            "name": "payment-api-prod-ec2-01",
            "resource_type": "virtual_machine",
            "service": "EC2",
            "provider": "AWS",
            "region": "us-east-1",
            "availability_zone": "us-east-1a",
            "environment": "production",
            "status": "healthy",
            "cpu_percent": 34.5,
            "memory_percent": 62.0,
            "disk_percent": 45.0,
            "network_in_mbps": 12.4,
            "network_out_mbps": 28.1,
            "monthly_cost": 240.0,
            "risk_score": 15,
            "owner": "Payments-Team",
            "lifecycle_state": "ACTIVE",
            "is_orphaned": False,
            "security_findings_count": 0,
            "governance_compliance_status": "COMPLIANT",
            "tags": {"Environment": "production", "Team": "payments", "CostCenter": "CC-102"},
            "metadata": {"instance_type": "t3.xlarge", "vpc_id": "vpc-0a1b2c3d4e"},
            "created_at": datetime(2025, 1, 15, 10, 0, 0, tzinfo=UTC),
            "updated_at": datetime.now(UTC),
        },
        {
            "id": uuid.UUID("22222222-2222-4222-8222-222222222222"),
            "name": "orders-rds-postgres-main",
            "resource_type": "database",
            "service": "RDS",
            "provider": "AWS",
            "region": "us-east-1",
            "availability_zone": "us-east-1b",
            "environment": "production",
            "status": "warning",
            "cpu_percent": 78.2,
            "memory_percent": 84.1,
            "disk_percent": 62.0,
            "network_in_mbps": 45.0,
            "network_out_mbps": 52.0,
            "monthly_cost": 680.0,
            "risk_score": 45,
            "owner": "Data-Eng",
            "lifecycle_state": "ACTIVE",
            "is_orphaned": False,
            "security_findings_count": 2,
            "governance_compliance_status": "NON_COMPLIANT",
            "tags": {"Environment": "production", "Service": "orders"},
            "metadata": {"engine": "postgres-15", "multi_az": True, "storage_gb": 500},
            "created_at": datetime(2025, 1, 10, 8, 30, 0, tzinfo=UTC),
            "updated_at": datetime.now(UTC),
        },
        {
            "id": uuid.UUID("33333333-3333-4333-8333-333333333333"),
            "name": "cloudpulse-analytics-data-lake",
            "resource_type": "storage",
            "service": "S3",
            "provider": "AWS",
            "region": "us-west-2",
            "availability_zone": None,
            "environment": "production",
            "status": "healthy",
            "cpu_percent": None,
            "memory_percent": None,
            "disk_percent": 12.0,
            "network_in_mbps": 5.0,
            "network_out_mbps": 8.0,
            "monthly_cost": 180.0,
            "risk_score": 5,
            "owner": "Analytics-Team",
            "lifecycle_state": "ACTIVE",
            "is_orphaned": False,
            "security_findings_count": 0,
            "governance_compliance_status": "COMPLIANT",
            "tags": {"Environment": "production", "DataClass": "Confidential"},
            "metadata": {"bucket_versioning": True, "encryption": "AES256"},
            "created_at": datetime(2025, 2, 1, 14, 0, 0, tzinfo=UTC),
            "updated_at": datetime.now(UTC),
        },
        {
            "id": uuid.UUID("44444444-4444-4444-8444-444444444444"),
            "name": "unattached-ebs-vol-dev-99",
            "resource_type": "storage",
            "service": "EBS",
            "provider": "AWS",
            "region": "us-east-1",
            "availability_zone": "us-east-1a",
            "environment": "development",
            "status": "stopped",
            "cpu_percent": None,
            "memory_percent": None,
            "disk_percent": 0.0,
            "network_in_mbps": 0.0,
            "network_out_mbps": 0.0,
            "monthly_cost": 85.0,
            "risk_score": 60,
            "owner": "Unassigned",
            "lifecycle_state": "ORPHANED",
            "is_orphaned": True,
            "security_findings_count": 1,
            "governance_compliance_status": "NON_COMPLIANT",
            "tags": {},
            "metadata": {"volume_size_gb": 500, "state": "available", "attached_to": None},
            "created_at": datetime(2024, 11, 20, 11, 0, 0, tzinfo=UTC),
            "updated_at": datetime.now(UTC),
        },

        # --- Azure Resources ---
        {
            "id": uuid.UUID("55555555-5555-4555-8555-555555555555"),
            "name": "auth-vault-prod-vm",
            "resource_type": "virtual_machine",
            "service": "Virtual Machines",
            "provider": "Azure",
            "region": "eastus",
            "availability_zone": "eastus-1",
            "environment": "production",
            "status": "healthy",
            "cpu_percent": 28.0,
            "memory_percent": 55.0,
            "disk_percent": 40.0,
            "network_in_mbps": 8.0,
            "network_out_mbps": 12.0,
            "monthly_cost": 310.0,
            "risk_score": 10,
            "owner": "Security-Team",
            "lifecycle_state": "ACTIVE",
            "is_orphaned": False,
            "security_findings_count": 0,
            "governance_compliance_status": "COMPLIANT",
            "tags": {"Environment": "production", "Role": "auth"},
            "metadata": {"vm_size": "Standard_D4s_v3", "os_type": "Ubuntu-22.04"},
            "created_at": datetime(2025, 1, 5, 9, 0, 0, tzinfo=UTC),
            "updated_at": datetime.now(UTC),
        },
        {
            "id": uuid.UUID("66666666-6666-4666-8666-666666666666"),
            "name": "enterprise-customer-sqldb",
            "resource_type": "database",
            "service": "Azure SQL",
            "provider": "Azure",
            "region": "eastus2",
            "availability_zone": None,
            "environment": "production",
            "status": "healthy",
            "cpu_percent": 42.0,
            "memory_percent": 68.0,
            "disk_percent": 50.0,
            "network_in_mbps": 22.0,
            "network_out_mbps": 30.0,
            "monthly_cost": 540.0,
            "risk_score": 20,
            "owner": "Data-Eng",
            "lifecycle_state": "ACTIVE",
            "is_orphaned": False,
            "security_findings_count": 1,
            "governance_compliance_status": "COMPLIANT",
            "tags": {"Environment": "production"},
            "metadata": {"edition": "GeneralPurpose", "max_size_gb": 250},
            "created_at": datetime(2025, 1, 8, 12, 0, 0, tzinfo=UTC),
            "updated_at": datetime.now(UTC),
        },

        # --- GCP Resources ---
        {
            "id": uuid.UUID("77777777-7777-4777-8777-777777777777"),
            "name": "aiops-model-inference-n2",
            "resource_type": "virtual_machine",
            "service": "Compute Engine",
            "provider": "GCP",
            "region": "us-central1",
            "availability_zone": "us-central1-a",
            "environment": "production",
            "status": "degraded",
            "cpu_percent": 94.2,
            "memory_percent": 91.5,
            "disk_percent": 70.0,
            "network_in_mbps": 65.0,
            "network_out_mbps": 80.0,
            "monthly_cost": 420.0,
            "risk_score": 70,
            "owner": "AI-Ops-Team",
            "lifecycle_state": "DEGRADED",
            "is_orphaned": False,
            "security_findings_count": 3,
            "governance_compliance_status": "NON_COMPLIANT",
            "tags": {"Environment": "production", "Workload": "ml-inference"},
            "metadata": {"machine_type": "n2-standard-8", "gpu_attached": True},
            "created_at": datetime(2025, 1, 20, 16, 0, 0, tzinfo=UTC),
            "updated_at": datetime.now(UTC),
        },
        {
            "id": uuid.UUID("88888888-8888-4888-8888-888888888888"),
            "name": "telemetry-raw-bigquery-ds",
            "resource_type": "database",
            "service": "BigQuery",
            "provider": "GCP",
            "region": "us-central1",
            "availability_zone": None,
            "environment": "production",
            "status": "healthy",
            "cpu_percent": 20.0,
            "memory_percent": 30.0,
            "disk_percent": 15.0,
            "network_in_mbps": 110.0,
            "network_out_mbps": 95.0,
            "monthly_cost": 750.0,
            "risk_score": 5,
            "owner": "Analytics-Team",
            "lifecycle_state": "ACTIVE",
            "is_orphaned": False,
            "security_findings_count": 0,
            "governance_compliance_status": "COMPLIANT",
            "tags": {"Environment": "production"},
            "metadata": {"location": "US", "dataset_id": "telemetry_logs"},
            "created_at": datetime(2025, 1, 2, 7, 0, 0, tzinfo=UTC),
            "updated_at": datetime.now(UTC),
        },

        # --- Kubernetes Workloads & Clusters ---
        {
            "id": uuid.UUID("99999999-9999-4999-8999-999999999999"),
            "name": "cloudpulse-production-gke-01",
            "resource_type": "kubernetes_cluster",
            "service": "GKE",
            "provider": "Kubernetes",
            "region": "us-central1",
            "availability_zone": "us-central1-a",
            "environment": "production",
            "status": "healthy",
            "cpu_percent": 58.0,
            "memory_percent": 64.0,
            "disk_percent": 48.0,
            "network_in_mbps": 140.0,
            "network_out_mbps": 160.0,
            "monthly_cost": 1250.0,
            "risk_score": 10,
            "owner": "Platform-SRE",
            "lifecycle_state": "ACTIVE",
            "is_orphaned": False,
            "security_findings_count": 0,
            "governance_compliance_status": "COMPLIANT",
            "tags": {"Environment": "production", "Cluster": "gke-01"},
            "metadata": {"nodes_count": 12, "k8s_version": "1.28.5-gke.1200"},
            "created_at": datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC),
            "updated_at": datetime.now(UTC),
        },
        {
            "id": uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
            "name": "payment-microservice-pod-x71",
            "resource_type": "pod",
            "service": "Kubernetes",
            "provider": "Kubernetes",
            "region": "us-central1",
            "availability_zone": "us-central1-a",
            "environment": "production",
            "status": "healthy",
            "cpu_percent": 30.0,
            "memory_percent": 45.0,
            "disk_percent": 20.0,
            "network_in_mbps": 15.0,
            "network_out_mbps": 22.0,
            "monthly_cost": 45.0,
            "risk_score": 5,
            "owner": "Payments-Team",
            "lifecycle_state": "ACTIVE",
            "is_orphaned": False,
            "security_findings_count": 0,
            "governance_compliance_status": "COMPLIANT",
            "tags": {"app": "payment-api", "namespace": "prod-payments"},
            "metadata": {"namespace": "prod-payments", "node": "gke-node-104"},
            "created_at": datetime(2025, 2, 10, 11, 0, 0, tzinfo=UTC),
            "updated_at": datetime.now(UTC),
        },
    ]


def calculate_asset_overview(assets: list[dict[str, Any]]) -> AssetOverviewResponse:
    """Compute overall asset overview counts and cost statistics."""
    total = len(assets)
    aws_cnt = sum(1 for a in assets if a["provider"].upper() == "AWS")
    azure_cnt = sum(1 for a in assets if a["provider"].upper() == "AZURE")
    gcp_cnt = sum(1 for a in assets if a["provider"].upper() == "GCP")
    k8s_cnt = sum(1 for a in assets if a["provider"].upper() == "KUBERNETES")

    healthy = sum(1 for a in assets if a["status"].lower() == "healthy")
    warning = sum(1 for a in assets if a["status"].lower() == "warning")
    critical = sum(1 for a in assets if a["status"].lower() in ("critical", "degraded"))
    orphaned = sum(1 for a in assets if a.get("is_orphaned", False))
    idle = sum(1 for a in assets if a.get("lifecycle_state", "").upper() == "IDLE")

    total_cost = sum(a.get("monthly_cost", 0.0) for a in assets)
    potential_savings = sum(
        a.get("monthly_cost", 0.0) * 0.8 for a in assets if a.get("is_orphaned", False)
    )

    return AssetOverviewResponse(
        total_resources=total,
        aws_count=aws_cnt,
        azure_count=azure_cnt,
        gcp_count=gcp_cnt,
        kubernetes_count=k8s_cnt,
        healthy_count=healthy,
        warning_count=warning,
        critical_count=critical,
        orphaned_count=orphaned,
        idle_count=idle,
        total_monthly_cost=round(total_cost, 2),
        total_potential_savings=round(potential_savings, 2),
        mode_indicator="Demo / Local Asset Data",
        updated_at=datetime.now(UTC),
    )


def calculate_provider_distribution(assets: list[dict[str, Any]]) -> AssetProviderDistributionResponse:
    """Group asset counts and monthly cost by provider."""
    total = len(assets) or 1
    grouped: dict[str, dict[str, Any]] = {}

    for a in assets:
        prov = a["provider"]
        if prov not in grouped:
            grouped[prov] = {"count": 0, "cost": 0.0, "healthy": 0}
        grouped[prov]["count"] += 1
        grouped[prov]["cost"] += a.get("monthly_cost", 0.0)
        if a["status"].lower() == "healthy":
            grouped[prov]["healthy"] += 1

    stats = []
    for prov, d in grouped.items():
        score = (d["healthy"] / d["count"] * 100.0) if d["count"] > 0 else 100.0
        stats.append(
            AssetProviderStat(
                provider=prov,
                resource_count=d["count"],
                monthly_cost=round(d["cost"], 2),
                percentage=round((d["count"] / total) * 100.0, 1),
                health_score=round(score, 1),
            )
        )

    return AssetProviderDistributionResponse(providers=stats)


def get_asset_topology(assets: list[dict[str, Any]]) -> AssetTopologyResponse:
    """Generate deterministic resource topology graph linking workloads to infrastructure."""
    nodes = []
    for a in assets:
        nodes.append(
            AssetTopologyNode(
                id=str(a["id"]),
                name=a["name"],
                type=a["resource_type"],
                provider=a["provider"],
                region=a["region"],
                status=a["status"],
                cost=a["monthly_cost"],
            )
        )

    edges = [
        AssetTopologyEdge(
            source="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            target="11111111-1111-4111-8111-111111111111",
            label="DEPLOYS_ON",
        ),
        AssetTopologyEdge(
            source="11111111-1111-4111-8111-111111111111",
            target="22222222-2222-4222-8222-222222222222",
            label="CONNECTS_TO",
        ),
        AssetTopologyEdge(
            source="11111111-1111-4111-8111-111111111111",
            target="33333333-3333-4333-8333-333333333333",
            label="WRITES_TO",
        ),
        AssetTopologyEdge(
            source="77777777-7777-4777-8777-777777777777",
            target="88888888-8888-4888-8888-888888888888",
            label="QUERIES",
        ),
        AssetTopologyEdge(
            source="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            target="99999999-9999-4999-8999-999999999999",
            label="CONTAINED_IN",
        ),
    ]

    return AssetTopologyResponse(nodes=nodes, edges=edges)


def get_orphaned_resources(assets: list[dict[str, Any]]) -> OrphanedResourcesResponse:
    """Identify unutilized or orphaned cloud resources."""
    orphaned_items = []
    total_savings = 0.0

    for a in assets:
        if a.get("is_orphaned", False) or a.get("lifecycle_state", "").upper() == "ORPHANED":
            savings = a.get("monthly_cost", 0.0) * 0.95
            total_savings += savings
            orphaned_items.append(
                OrphanedResourceItem(
                    resource_id=str(a["id"]),
                    resource_name=a["name"],
                    provider=a["provider"],
                    service=a["service"],
                    region=a["region"],
                    reason="Unattached EBS Volume with zero I/O activity for > 30 days.",
                    monthly_cost=a.get("monthly_cost", 0.0),
                    potential_savings=round(savings, 2),
                    recommended_action="Delete unattached EBS volume or take snapshot and release.",
                )
            )

    return OrphanedResourcesResponse(
        total_orphaned=len(orphaned_items),
        total_potential_savings=round(total_savings, 2),
        orphaned_resources=orphaned_items,
    )


def get_asset_detail_by_id(
    assets: list[dict[str, Any]], resource_id: uuid.UUID | str
) -> AssetDetailResponse | None:
    """Retrieve comprehensive resource deep-dive details integrated with FinOps, Security, and Governance."""
    target_str = str(resource_id)
    target = None
    for a in assets:
        if str(a["id"]) == target_str:
            target = a
            break

    if not target:
        return None

    resource_item = AssetResourceItem.model_validate(target)

    # Deterministic Mock Integrations
    relationships = [
        AssetRelationshipItem(
            id="rel-1",
            source_id=target_str,
            source_name=target["name"],
            target_id="22222222-2222-4222-8222-222222222222",
            target_name="orders-rds-postgres-main",
            relationship_type="CONNECTS_TO",
            direction="OUTBOUND",
            confidence=0.98,
        )
    ]

    security_findings = [
        {
            "finding_id": "sec-001",
            "title": "Security Group Allows Unrestricted SSH Inbound",
            "severity": "HIGH",
            "cve_id": "CVE-2024-5510",
            "status": "OPEN",
        }
    ] if target.get("security_findings_count", 0) > 0 else []

    governance_violations = [
        {
            "violation_id": "gov-104",
            "policy_name": "Resource Encryption Required",
            "severity": "HIGH",
            "status": "OPEN",
            "recommendation": "Enable server-side encryption with KMS customer-managed key.",
        }
    ] if target.get("governance_compliance_status") == "NON_COMPLIANT" else []

    finops_opt = {
        "current_monthly_cost": target["monthly_cost"],
        "recommended_instance_type": "t3.medium",
        "potential_monthly_savings": round(target["monthly_cost"] * 0.4, 2),
        "confidence": 0.92,
    }

    related_incidents = [
        {
            "incident_id": "inc-802",
            "title": "High CPU Saturation & Latency Spike",
            "severity": "MEDIUM",
            "status": "RESOLVED",
        }
    ] if target["status"] in ("warning", "degraded") else []

    telemetry = {
        "cpu_percent": target.get("cpu_percent"),
        "memory_percent": target.get("memory_percent"),
        "disk_percent": target.get("disk_percent"),
        "network_in_mbps": target.get("network_in_mbps"),
        "network_out_mbps": target.get("network_out_mbps"),
    }

    return AssetDetailResponse(
        resource=resource_item,
        relationships=relationships,
        security_findings=security_findings,
        governance_violations=governance_violations,
        finops_optimization=finops_opt,
        related_incidents=related_incidents,
        telemetry_summary=telemetry,
    )
