"""
Action Catalog & Controlled Action Registry for Autonomous Operations.
"""

from __future__ import annotations

from typing import Any


class ActionDefinition:
    """Represents a controlled remediation action declaration."""

    def __init__(
        self,
        action_type: str,
        domain: str,
        provider: str,
        risk_level: str,
        description: str,
        required_permissions: list[str],
        supports_dry_run: bool = True,
        supports_simulation: bool = True,
        supports_rollback: bool = True,
        requires_approval: bool = True,
    ) -> None:
        self.action_type = action_type
        self.domain = domain
        self.provider = provider
        self.risk_level = risk_level  # LOW, MEDIUM, HIGH, CRITICAL
        self.description = description
        self.required_permissions = required_permissions
        self.supports_dry_run = supports_dry_run
        self.supports_simulation = supports_simulation
        self.supports_rollback = supports_rollback
        self.requires_approval = requires_approval

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_type": self.action_type,
            "domain": self.domain,
            "provider": self.provider,
            "risk_level": self.risk_level,
            "description": self.description,
            "required_permissions": self.required_permissions,
            "supports_dry_run": self.supports_dry_run,
            "supports_simulation": self.supports_simulation,
            "supports_rollback": self.supports_rollback,
            "requires_approval": self.requires_approval,
        }


# Controlled Remediation Actions Registry
ACTION_REGISTRY: dict[str, ActionDefinition] = {
    "RESTART_SERVICE": ActionDefinition(
        action_type="RESTART_SERVICE",
        domain="INCIDENT",
        provider="AWS",
        risk_level="LOW",
        description="Restart unhealthy production microservice instance or container.",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=True,
        requires_approval=False,
    ),
    "RESTART_K8S_POD": ActionDefinition(
        action_type="RESTART_K8S_POD",
        domain="KUBERNETES",
        provider="Kubernetes",
        risk_level="LOW",
        description="Gracefully restart crashlooping or unhealthy Kubernetes pod.",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=True,
        requires_approval=False,
    ),
    "SCALE_K8S_DEPLOYMENT": ActionDefinition(
        action_type="SCALE_K8S_DEPLOYMENT",
        domain="CAPACITY",
        provider="Kubernetes",
        risk_level="MEDIUM",
        description="Scale Kubernetes deployment replica count up to handle high load/saturation.",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=True,
        requires_approval=True,
    ),
    "SCALE_WORKLOAD_DOWN": ActionDefinition(
        action_type="SCALE_WORKLOAD_DOWN",
        domain="FINOPS",
        provider="Kubernetes",
        risk_level="MEDIUM",
        description="Scale over-provisioned workload replica count down to eliminate cost waste.",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=True,
        requires_approval=True,
    ),
    "CLEAR_TEMP_STORAGE": ActionDefinition(
        action_type="CLEAR_TEMP_STORAGE",
        domain="CAPACITY",
        provider="AWS",
        risk_level="LOW",
        description="Purge temporary files, build caches, and ephemeral log buffers.",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=False,
        requires_approval=False,
    ),
    "ROTATE_WORKLOAD": ActionDefinition(
        action_type="ROTATE_WORKLOAD",
        domain="SECURITY",
        provider="Kubernetes",
        risk_level="MEDIUM",
        description="Perform zero-downtime rolling update of workload pods.",
        required_permissions=["Security.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=True,
        requires_approval=True,
    ),
    "DRAIN_K8S_NODE": ActionDefinition(
        action_type="DRAIN_K8S_NODE",
        domain="KUBERNETES",
        provider="Kubernetes",
        risk_level="HIGH",
        description="Cordon and safely drain pods from degraded Kubernetes node.",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=True,
        requires_approval=True,
    ),
    "STOP_IDLE_COMPUTE": ActionDefinition(
        action_type="STOP_IDLE_COMPUTE",
        domain="FINOPS",
        provider="GCP",
        risk_level="HIGH",
        description="Stop unutilized or idle compute instance identified by FinOps.",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=True,
        requires_approval=True,
    ),
    "RESIZE_OVERSIZED_RESOURCE": ActionDefinition(
        action_type="RESIZE_OVERSIZED_RESOURCE",
        domain="FINOPS",
        provider="Azure",
        risk_level="HIGH",
        description="Right-size oversized database or compute instance size class.",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=True,
        requires_approval=True,
    ),
    "REDUCE_EXCESSIVE_LOGGING": ActionDefinition(
        action_type="REDUCE_EXCESSIVE_LOGGING",
        domain="FINOPS",
        provider="AWS",
        risk_level="LOW",
        description="Adjust log verbosity level from DEBUG to INFO to control telemetry ingestion costs.",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=True,
        requires_approval=False,
    ),
    "ARCHIVE_OLD_LOGS": ActionDefinition(
        action_type="ARCHIVE_OLD_LOGS",
        domain="CAPACITY",
        provider="AWS",
        risk_level="LOW",
        description="Transition old log files to cold storage (Glacier/S3 Deep Archive).",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=False,
        requires_approval=False,
    ),
    "REMOVE_UNATTACHED_STORAGE": ActionDefinition(
        action_type="REMOVE_UNATTACHED_STORAGE",
        domain="FINOPS",
        provider="AWS",
        risk_level="CRITICAL",
        description="Delete unattached EBS volumes / unmapped block storage disks.",
        required_permissions=["Security.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=False,
        requires_approval=True,
    ),
    "RESOLVE_SERVICE_DEPENDENCY": ActionDefinition(
        action_type="RESOLVE_SERVICE_DEPENDENCY",
        domain="INCIDENT",
        provider="AWS",
        risk_level="MEDIUM",
        description="Reroute traffic or failover to secondary healthy service dependency node.",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=True,
        requires_approval=True,
    ),
    "TRIGGER_WORKFLOW": ActionDefinition(
        action_type="TRIGGER_WORKFLOW",
        domain="GOVERNANCE",
        provider="Kubernetes",
        risk_level="LOW",
        description="Trigger predefined automated workflow template.",
        required_permissions=["Incidents.Manage"],
        supports_dry_run=True,
        supports_simulation=True,
        supports_rollback=True,
        requires_approval=False,
    ),
}


def get_action_definition(action_type: str) -> ActionDefinition | None:
    return ACTION_REGISTRY.get(action_type.upper())


def list_action_definitions() -> list[dict[str, Any]]:
    return [act.to_dict() for act in ACTION_REGISTRY.values()]
