"""
Deterministic Local Security Detection Engine.

Detects 16 realistic security vulnerabilities across AWS, Azure, GCP, and Kubernetes:
- 3 Critical Findings (Public S3 bucket with PII, Privileged K8s Pod, Open SSH 0.0.0.0/0:22)
- 5 High Findings (Unencrypted GCP PostgreSQL, Public Azure Blob Container, Overly Permissive AWS Admin Role, Auto-mounted K8s SA Token, Plaintext ConfigMap Secrets)
- 5 Medium Findings (Shared Public AWS RDS Snapshot, Azure Key Vault Soft-Delete Disabled, GCP Default Compute SA, Unrestricted K8s API 6443, GCP Storage Versioning Disabled)
- 3 Low Findings (AWS User without MFA, Azure NSG Logging Disabled, GCP Subnet Flow Logs Disabled)
"""

from datetime import UTC, datetime, timedelta
from typing import Any

DETECTION_FIXTURES: list[dict[str, Any]] = [
    # --- 3 CRITICAL FINDINGS ---
    {
        "scan_name": "Publicly Exposed S3 Storage Bucket with Customer PII",
        "provider": "AWS",
        "region": "us-east-1",
        "resource": "s3://cloudpulse-prod-backups-bucket",
        "resource_type": "s3_bucket",
        "severity": "CRITICAL",
        "category": "Storage",
        "compliance_framework": "CIS AWS Foundations v2.0",
        "description": "S3 bucket acl 'public-read-write' allows unauthenticated internet principals to read and overwrite production database backup archives.",
        "recommendation": "Enable AWS S3 Block Public Access at the bucket level and attach explicit DenyUnencryptedObjectUploads bucket policy.",
        "risk_score": 9.8,
        "confidence": 0.98,
        "status": "OPEN",
        "evidence": [
            {
                "type": "configuration",
                "source": "AWS S3 Control API",
                "message": "BlockPublicAcls=False, IgnorePublicAcls=False, BlockPublicPolicy=False",
                "severity": "CRITICAL",
                "details": {"bucket": "cloudpulse-prod-backups-bucket", "owner_id": "123456789012"},
            },
            {
                "type": "network",
                "source": "Internet Scanner Probe",
                "message": "HTTP 200 OK returned on GET s3.amazonaws.com/cloudpulse-prod-backups-bucket/dump.sql.gz",
                "severity": "CRITICAL",
                "details": {"file_size_bytes": 145892014, "content_type": "application/gzip"},
            },
        ],
    },
    {
        "scan_name": "Kubernetes Pod Running with Privileged Host PID & SecurityContext",
        "provider": "Kubernetes",
        "region": "global",
        "resource": "k8s://production/payment-processor-pod-9f8d",
        "resource_type": "k8s_pod",
        "severity": "CRITICAL",
        "category": "Compute",
        "compliance_framework": "NSA-CISA Kubernetes Hardening Guide",
        "description": "Container pod running with privileged: true, hostPID: true, and CAP_SYS_ADMIN capabilities. Enables container escape to host node kernel.",
        "recommendation": "Set securityContext.privileged: false, allowPrivilegeEscalation: false, and enforce PodSecurityAdmission restricted profile.",
        "risk_score": 9.4,
        "confidence": 0.95,
        "status": "OPEN",
        "evidence": [
            {
                "type": "manifest",
                "source": "K8s Admission Controller",
                "message": "securityContext.privileged = true, hostPID = true, capabilities.add = ['SYS_ADMIN']",
                "severity": "CRITICAL",
                "details": {"namespace": "production", "pod": "payment-processor-pod-9f8d"},
            },
        ],
    },
    {
        "scan_name": "Inbound Security Group Rule Allows Open SSH (0.0.0.0/0:22) Ingress",
        "provider": "AWS",
        "region": "us-west-2",
        "resource": "sg-0a8f9c123456789ab (prod-db-vpc-sg)",
        "resource_type": "security_group",
        "severity": "CRITICAL",
        "category": "Network",
        "compliance_framework": "CIS AWS Foundations 1.2",
        "description": "Security Group sg-0a8f9c123456789ab contains ingress rule permitting 0.0.0.0/0 on port 22. Exposes production instances to brute-force SSH attacks.",
        "recommendation": "Remove 0.0.0.0/0 ingress rule on port 22 and restrict SSH access strictly to corporate VPN CIDR or AWS Systems Manager Session Manager.",
        "risk_score": 9.2,
        "confidence": 0.96,
        "status": "INVESTIGATING",
        "evidence": [
            {
                "type": "network_rule",
                "source": "AWS EC2 DescribeSecurityGroups API",
                "message": "IpPermissions: [{IpProtocol: tcp, FromPort: 22, ToPort: 22, IpRanges: [{CidrIp: 0.0.0.0/0}]}]",
                "severity": "CRITICAL",
                "details": {"vpc_id": "vpc-0123456789abcdef0", "group_name": "prod-db-vpc-sg"},
            },
        ],
    },

    # --- 5 HIGH FINDINGS ---
    {
        "scan_name": "Unencrypted GCP Cloud SQL PostgreSQL Database Instance",
        "provider": "GCP",
        "region": "us-central1",
        "resource": "projects/cloudpulse-prod/instances/cloudpulse-db-primary",
        "resource_type": "db_instance",
        "severity": "HIGH",
        "category": "Database",
        "compliance_framework": "NIST SP 800-53 r5",
        "description": "Cloud SQL PostgreSQL database is configured without Customer-Managed Encryption Keys (CMEK) and SSL enforcement is set to optional.",
        "recommendation": "Enable requireSsl: true in database flags and configure Cloud KMS CMEK encryption key.",
        "risk_score": 7.9,
        "confidence": 0.92,
        "status": "OPEN",
        "evidence": [
            {
                "type": "configuration",
                "source": "GCP Cloud SQL Admin API",
                "message": "ipConfiguration.requireSsl = False, diskEncryptionConfiguration.kmsKeyName = null",
                "severity": "HIGH",
                "details": {"instance": "cloudpulse-db-primary", "database_version": "POSTGRES_15"},
            },
        ],
    },
    {
        "scan_name": "Azure Blob Storage Container with Anonymous Public Read Access Enabled",
        "provider": "Azure",
        "region": "westeurope",
        "resource": "https://cloudpulsestorage.blob.core.windows.net/telemetry-logs",
        "resource_type": "blob_container",
        "severity": "HIGH",
        "category": "Storage",
        "compliance_framework": "ISO 27001:2022 A.8.12",
        "description": "Storage Container publicAccess level set to 'Container'. Allows unauthenticated blob listing and downloading of raw application logs.",
        "recommendation": "Set publicAccess to 'None' and enforce Azure Private Endpoints for storage account access.",
        "risk_score": 7.8,
        "confidence": 0.94,
        "status": "OPEN",
        "evidence": [
            {
                "type": "configuration",
                "source": "Azure Storage Management API",
                "message": "containerProperties.publicAccess = Container",
                "severity": "HIGH",
                "details": {"storage_account": "cloudpulsestorage", "container": "telemetry-logs"},
            },
        ],
    },
    {
        "scan_name": "Overly Permissive IAM AdministratorRole Assigned to EC2 Microservice Profile",
        "provider": "AWS",
        "region": "us-east-1",
        "resource": "arn:aws:iam::123456789012:role/EC2MicroserviceAdminRole",
        "resource_type": "iam_role",
        "severity": "HIGH",
        "category": "IAM",
        "compliance_framework": "SOC 2 Type II CC6.3",
        "description": "IAM Role assigned to EC2 instance profile contains attached policy AdministratorAccess (Action: *, Resource: *).",
        "recommendation": "Replace AdministratorAccess with least-privilege policies granting only required S3 and DynamoDB actions.",
        "risk_score": 7.6,
        "confidence": 0.95,
        "status": "OPEN",
        "evidence": [
            {
                "type": "iam_policy",
                "source": "AWS IAM GetRolePolicy API",
                "message": "AttachedManagedPolicies: [arn:aws:iam::aws:policy/AdministratorAccess]",
                "severity": "HIGH",
                "details": {"role_name": "EC2MicroserviceAdminRole"},
            },
        ],
    },
    {
        "scan_name": "Kubernetes ServiceAccount Token Automatically Mounted in Namespace Pods",
        "provider": "Kubernetes",
        "region": "global",
        "resource": "k8s://production/automount-sa-token",
        "resource_type": "k8s_serviceaccount",
        "severity": "HIGH",
        "category": "IAM",
        "compliance_framework": "CIS Kubernetes Benchmark v1.8",
        "description": "Default ServiceAccount automountServiceAccountToken is enabled. Allows compromised pod containers to steal API tokens.",
        "recommendation": "Set automountServiceAccountToken: false on ServiceAccount manifests unless explicit API access is required.",
        "risk_score": 7.4,
        "confidence": 0.91,
        "status": "OPEN",
        "evidence": [
            {
                "type": "manifest",
                "source": "K8s API Server Spec",
                "message": "ServiceAccount.default.automountServiceAccountToken = true",
                "severity": "HIGH",
                "details": {"namespace": "production", "service_account": "default"},
            },
        ],
    },
    {
        "scan_name": "Plaintext Database Passwords & JWT Secret Key Exposed in Kubernetes ConfigMap",
        "provider": "Kubernetes",
        "region": "global",
        "resource": "k8s://production/configmap/app-env-config",
        "resource_type": "k8s_configmap",
        "severity": "HIGH",
        "category": "Secrets",
        "compliance_framework": "PCI DSS v4.0 Requirement 8.3",
        "description": "ConfigMap app-env-config contains unencrypted sensitive keys 'DATABASE_PASSWORD' and 'JWT_SECRET_KEY' in data map.",
        "recommendation": "Migrate plaintext ConfigMap secrets to Kubernetes External Secrets Operator or HashiCorp Vault.",
        "risk_score": 7.3,
        "confidence": 0.97,
        "status": "MITIGATED",
        "evidence": [
            {
                "type": "secret_leak",
                "source": "K8s ConfigMap Inspector",
                "message": "Found sensitive keys in data: DATABASE_PASSWORD (len=24), JWT_SECRET_KEY (len=64)",
                "severity": "HIGH",
                "details": {"configmap": "app-env-config", "namespace": "production"},
            },
        ],
    },

    # --- 5 MEDIUM FINDINGS ---
    {
        "scan_name": "AWS RDS Database Snapshot Shared Publicly Across AWS Accounts",
        "provider": "AWS",
        "region": "eu-central-1",
        "resource": "rds:cloudpulse-db-snapshot-2026-08-01",
        "resource_type": "db_snapshot",
        "severity": "MEDIUM",
        "category": "Database",
        "compliance_framework": "CIS AWS Foundations 2.3",
        "description": "DBSnapshotAttribute 'restore' includes 'all', making snapshot publicly accessible to external AWS account IDs.",
        "recommendation": "Modify snapshot attribute to remove public restore permissions.",
        "risk_score": 5.8,
        "confidence": 0.90,
        "status": "OPEN",
        "evidence": [
            {
                "type": "configuration",
                "source": "AWS RDS DescribeDBSnapshotAttributes",
                "message": "AttributeName: restore, AttributeValues: ['all']",
                "severity": "MEDIUM",
                "details": {"snapshot_id": "cloudpulse-db-snapshot-2026-08-01"},
            },
        ],
    },
    {
        "scan_name": "Azure Key Vault Soft-Delete and Purge Protection Disabled",
        "provider": "Azure",
        "region": "eastus",
        "resource": "/subscriptions/sub-1/resourceGroups/rg-prod/providers/Microsoft.KeyVault/vaults/cloudpulse-kv",
        "resource_type": "key_vault",
        "severity": "MEDIUM",
        "category": "Secrets",
        "compliance_framework": "NIST CSF V1.1 PR.IP-4",
        "description": "Azure Key Vault does not have purgeProtectionEnabled: true. Accidental deletion could cause unrecoverable secret loss.",
        "recommendation": "Enable purgeProtection and softDeleteRetentionInDays: 90 on Key Vault resource.",
        "risk_score": 5.4,
        "confidence": 0.93,
        "status": "OPEN",
        "evidence": [
            {
                "type": "configuration",
                "source": "Azure Resource Manager API",
                "message": "enablePurgeProtection = False, enableSoftDelete = True",
                "severity": "MEDIUM",
                "details": {"vault_name": "cloudpulse-kv"},
            },
        ],
    },
    {
        "scan_name": "GCP Compute Instance Using Default Compute Engine Service Account",
        "provider": "GCP",
        "region": "us-central1",
        "resource": "projects/cloudpulse-prod/zones/us-central1-a/instances/worker-node-1",
        "resource_type": "compute_instance",
        "severity": "MEDIUM",
        "category": "IAM",
        "compliance_framework": "GCP Security Health Analytics",
        "description": "VM instance is configured with default Compute Engine SA [PROJECT_NUMBER]-compute@developer.gserviceaccount.com containing Editor access.",
        "recommendation": "Create dedicated custom service account with minimal granular IAM roles.",
        "risk_score": 5.2,
        "confidence": 0.89,
        "status": "OPEN",
        "evidence": [
            {
                "type": "configuration",
                "source": "GCP Compute Engine API",
                "message": "serviceAccounts[0].email = 123456789-compute@developer.gserviceaccount.com",
                "severity": "MEDIUM",
                "details": {"instance": "worker-node-1"},
            },
        ],
    },
    {
        "scan_name": "Unrestricted Inbound Access to Kubernetes API Server (0.0.0.0/0:6443)",
        "provider": "Kubernetes",
        "region": "global",
        "resource": "k8s://production/control-plane-api",
        "resource_type": "k8s_cluster",
        "severity": "MEDIUM",
        "category": "Network",
        "compliance_framework": "CIS Kubernetes Benchmark v1.8",
        "description": "Kubernetes API Server endpoint is reachable from 0.0.0.0/0 on port 6443.",
        "recommendation": "Restrict control plane master endpoint access to authorized bastion CIDR blocks.",
        "risk_score": 5.0,
        "confidence": 0.95,
        "status": "OPEN",
        "evidence": [
            {
                "type": "network",
                "source": "K8s API Server Endpoint Audit",
                "message": "API Server public endpoint reachable: https://34.120.45.12:6443",
                "severity": "MEDIUM",
                "details": {"cluster_name": "prod-k8s-us-central1"},
            },
        ],
    },
    {
        "scan_name": "GCP Cloud Storage Bucket Without Object Versioning & Lifecycle Encryption Policies",
        "provider": "GCP",
        "region": "europe-west1",
        "resource": "gs://cloudpulse-audit-logs",
        "resource_type": "storage_bucket",
        "severity": "MEDIUM",
        "category": "Storage",
        "compliance_framework": "HIPAA Security Rule § 164.312",
        "description": "GCS bucket storage lacks Object Versioning and Lifecycle Retention locks required for immutable audit trails.",
        "recommendation": "Enable gsutil versioning set on gs://cloudpulse-audit-logs and attach retention policy.",
        "risk_score": 4.8,
        "confidence": 0.91,
        "status": "RESOLVED",
        "evidence": [
            {
                "type": "configuration",
                "source": "GCP Storage API",
                "message": "versioning.enabled = False, retentionPolicy = null",
                "severity": "MEDIUM",
                "details": {"bucket": "cloudpulse-audit-logs"},
            },
        ],
    },

    # --- 3 LOW FINDINGS ---
    {
        "scan_name": "AWS IAM User Without Multi-Factor Authentication (MFA) Enforced",
        "provider": "AWS",
        "region": "global",
        "resource": "arn:aws:iam::123456789012:user/deployer-service-user",
        "resource_type": "iam_user",
        "severity": "LOW",
        "category": "IAM",
        "compliance_framework": "CIS AWS Foundations 1.1",
        "description": "IAM user deployer-service-user has console password access enabled without active MFA device attached.",
        "recommendation": "Attach IAM MFA policy or convert user account to IAM Service Role for automated pipelines.",
        "risk_score": 2.8,
        "confidence": 0.98,
        "status": "OPEN",
        "evidence": [
            {
                "type": "iam",
                "source": "AWS IAM Credential Report",
                "message": "mfa_active = False, password_enabled = True",
                "severity": "LOW",
                "details": {"user": "deployer-service-user"},
            },
        ],
    },
    {
        "scan_name": "Azure Network Security Group Missing Default Ingress Deny Logging",
        "provider": "Azure",
        "region": "eastus",
        "resource": "/subscriptions/sub-1/resourceGroups/rg-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-web",
        "resource_type": "nsg",
        "severity": "LOW",
        "category": "Network",
        "compliance_framework": "Azure Security Benchmark v3",
        "description": "Network Security Group nsg-web does not have Flow Logs sent to Log Analytics workspace.",
        "recommendation": "Enable Network Watcher NSG flow logs and traffic analytics.",
        "risk_score": 2.4,
        "confidence": 0.88,
        "status": "ACCEPTED_RISK",
        "evidence": [
            {
                "type": "logging",
                "source": "Azure Network Watcher",
                "message": "flowLogs.enabled = False",
                "severity": "LOW",
                "details": {"nsg": "nsg-web"},
            },
        ],
    },
    {
        "scan_name": "GCP VPC Flow Logs Disabled on Subnet prod-useast1-vpc",
        "provider": "GCP",
        "region": "us-east1",
        "resource": "projects/cloudpulse-prod/regions/us-east1/subnetworks/prod-useast1-vpc",
        "resource_type": "vpc_subnet",
        "severity": "LOW",
        "category": "Network",
        "compliance_framework": "CIS GCP Foundation 3.8",
        "description": "VPC flow logging is disabled on subnet prod-useast1-vpc. Prevents network forensic tracing.",
        "recommendation": "Set enableFlowLogs: true with aggregationInterval: INTERVAL_5_SEC.",
        "risk_score": 2.2,
        "confidence": 0.92,
        "status": "OPEN",
        "evidence": [
            {
                "type": "logging",
                "source": "GCP Compute Network API",
                "message": "enableFlowLogs = False",
                "severity": "LOW",
                "details": {"subnet": "prod-useast1-vpc"},
            },
        ],
    },
]


class SecurityDetectionEngine:
    def generate_findings(self, provider_filter: str | None = None) -> list[dict[str, Any]]:
        """
        Generates realistic, deterministic security findings across AWS, Azure, GCP, and Kubernetes.
        """
        now = datetime.now(UTC)
        results: list[dict[str, Any]] = []

        for idx, item in enumerate(DETECTION_FIXTURES):
            prov = item["provider"]
            if provider_filter and provider_filter.upper() != "ALL" and prov.upper() != provider_filter.upper():
                continue

            detected_at = now - timedelta(hours=(idx + 1) * 3, minutes=12)
            item_copy = dict(item)
            item_copy["first_detected_at"] = detected_at
            item_copy["last_detected_at"] = now - timedelta(minutes=15)
            results.append(item_copy)

        return results


security_detection_engine = SecurityDetectionEngine()
