"""
Provider Adapter Architecture for Autonomous Remediation Operations.
Defines explicit provider interfaces and deterministic simulation adapters.
"""

from __future__ import annotations

import abc
from typing import Any


class BaseProviderAdapter(abc.ABC):
    """Abstract Base Class for Cloud/K8s Remediation Provider Adapters."""

    @abc.abstractmethod
    async def check_resource(self, resource_name: str) -> dict[str, Any]:
        """Check target resource existence and status."""
        pass

    @abc.abstractmethod
    async def restart_resource(self, resource_name: str) -> dict[str, Any]:
        """Restart target resource."""
        pass

    @abc.abstractmethod
    async def scale_resource(self, resource_name: str, replicas: int) -> dict[str, Any]:
        """Scale target workload replicas."""
        pass

    @abc.abstractmethod
    async def stop_resource(self, resource_name: str) -> dict[str, Any]:
        """Stop target compute resource."""
        pass

    @abc.abstractmethod
    async def delete_resource(self, resource_name: str) -> dict[str, Any]:
        """Delete unneeded resource."""
        pass

    @abc.abstractmethod
    async def health_check(self, resource_name: str) -> dict[str, Any]:
        """Perform health check on resource."""
        pass

    @abc.abstractmethod
    async def rollback(self, resource_name: str, target_state: dict[str, Any]) -> dict[str, Any]:
        """Rollback resource state."""
        pass


class SimulationProviderAdapter(BaseProviderAdapter):
    """
    Deterministic Local Simulation Provider Adapter.
    Used when real cloud credentials are absent or SIMULATED mode is active.
    """

    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name

    async def check_resource(self, resource_name: str) -> dict[str, Any]:
        return {
            "status": "EXISTS",
            "provider": self.provider_name,
            "resource": resource_name,
            "simulated": True,
            "health": "UNHEALTHY",
            "message": f"Deterministic local simulation checked resource {resource_name}.",
        }

    async def restart_resource(self, resource_name: str) -> dict[str, Any]:
        return {
            "status": "SUCCESS",
            "action": "RESTART",
            "provider": self.provider_name,
            "resource": resource_name,
            "simulated": True,
            "previous_state": {"status": "UNHEALTHY", "restarts": 4},
            "new_state": {"status": "RUNNING", "restarts": 5},
            "message": f"[SIMULATION] Restarted resource {resource_name} on {self.provider_name}.",
        }

    async def scale_resource(self, resource_name: str, replicas: int) -> dict[str, Any]:
        return {
            "status": "SUCCESS",
            "action": "SCALE",
            "provider": self.provider_name,
            "resource": resource_name,
            "simulated": True,
            "previous_state": {"replicas": 2},
            "new_state": {"replicas": replicas},
            "message": f"[SIMULATION] Scaled workload {resource_name} to {replicas} replicas on {self.provider_name}.",
        }

    async def stop_resource(self, resource_name: str) -> dict[str, Any]:
        return {
            "status": "SUCCESS",
            "action": "STOP",
            "provider": self.provider_name,
            "resource": resource_name,
            "simulated": True,
            "previous_state": {"status": "RUNNING"},
            "new_state": {"status": "STOPPED"},
            "message": f"[SIMULATION] Stopped idle compute resource {resource_name} on {self.provider_name}.",
        }

    async def delete_resource(self, resource_name: str) -> dict[str, Any]:
        return {
            "status": "SUCCESS",
            "action": "DELETE",
            "provider": self.provider_name,
            "resource": resource_name,
            "simulated": True,
            "previous_state": {"status": "UNATTACHED"},
            "new_state": {"status": "DELETED"},
            "message": f"[SIMULATION] Deleted unattached storage {resource_name} on {self.provider_name}.",
        }

    async def health_check(self, resource_name: str) -> dict[str, Any]:
        return {
            "status": "HEALTHY",
            "provider": self.provider_name,
            "resource": resource_name,
            "simulated": True,
            "http_code": 200,
            "latency_ms": 14.2,
            "verified": True,
            "message": f"[SIMULATION] Health check passed for {resource_name}.",
        }

    async def rollback(self, resource_name: str, target_state: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "SUCCESS",
            "action": "ROLLBACK",
            "provider": self.provider_name,
            "resource": resource_name,
            "simulated": True,
            "restored_state": target_state,
            "message": f"[SIMULATION] Rolled back {resource_name} to previous state.",
        }


class AWSProviderAdapter(SimulationProviderAdapter):
    def __init__(self) -> None:
        super().__init__("AWS")


class AzureProviderAdapter(SimulationProviderAdapter):
    def __init__(self) -> None:
        super().__init__("Azure")


class GCPProviderAdapter(SimulationProviderAdapter):
    def __init__(self) -> None:
        super().__init__("GCP")


class KubernetesProviderAdapter(SimulationProviderAdapter):
    def __init__(self) -> None:
        super().__init__("Kubernetes")


def get_provider_adapter(provider: str, mode: str = "SIMULATED") -> BaseProviderAdapter:
    """
    Selects appropriate provider adapter.
    Defaults to SimulationProviderAdapter if mode is SIMULATED/DRY_RUN or credentials absent.
    """
    prov_upper = provider.upper()
    if prov_upper == "AWS":
        return AWSProviderAdapter()
    elif prov_upper == "AZURE":
        return AzureProviderAdapter()
    elif prov_upper == "GCP":
        return GCPProviderAdapter()
    elif prov_upper == "KUBERNETES":
        return KubernetesProviderAdapter()
    else:
        return SimulationProviderAdapter(provider)
