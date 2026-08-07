"""
Role-Based Access Control (RBAC) & Granular Permission Core Engine.
"""

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "Owner": [
        "Dashboard.Read",
        "Dashboard.Write",
        "Incidents.Manage",
        "Logs.Read",
        "Tracing.Read",
        "Security.Manage",
        "AI.Use",
        "Billing.Manage",
        "Settings.Manage",
    ],
    "Admin": [
        "Dashboard.Read",
        "Dashboard.Write",
        "Incidents.Manage",
        "Logs.Read",
        "Tracing.Read",
        "Security.Manage",
        "AI.Use",
        "Settings.Manage",
    ],
    "Manager": [
        "Dashboard.Read",
        "Dashboard.Write",
        "Incidents.Manage",
        "Logs.Read",
        "Tracing.Read",
        "AI.Use",
    ],
    "Engineer": [
        "Dashboard.Read",
        "Dashboard.Write",
        "Incidents.Manage",
        "Logs.Read",
        "Tracing.Read",
        "AI.Use",
    ],
    "Viewer": [
        "Dashboard.Read",
        "Logs.Read",
        "Tracing.Read",
    ],
}


def has_permission(role: str, permission: str) -> bool:
    """Check if a given role possesses a granular permission."""
    allowed = ROLE_PERMISSIONS.get(role, [])
    return permission in allowed


def get_all_permissions_matrix() -> dict[str, list[str]]:
    """Return the complete role permission matrix for UI rendering."""
    return ROLE_PERMISSIONS
