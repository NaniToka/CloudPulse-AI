"""
Approval Engine for Autonomous Cloud Operations.
Determines whether approval is required based on risk level, autonomy level,
environment, and user role.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autonomous import AutonomyPolicy


async def evaluate_approval_requirement(
    db: AsyncSession,
    *,
    action_type: str,
    environment: str,
    risk_level: str,
) -> dict[str, Any]:
    """
    Evaluates whether an action requires explicit human approval.
    """
    # Query active autonomy policy
    policy_stmt = select(AutonomyPolicy).where(AutonomyPolicy.is_active.is_(True))
    policy_res = await db.execute(policy_stmt)
    policy = policy_res.scalars().first()

    autonomy_level = policy.autonomy_level if policy else 1
    max_risk = policy.max_autonomous_risk if policy else "LOW"

    # Risk ranking helper
    risk_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    act_risk_val = risk_order.get(risk_level.upper(), 2)
    max_risk_val = risk_order.get(max_risk.upper(), 1)

    # Decision Matrix:
    # Level 0 (Observe): All executions require approval or are blocked.
    # Level 1 (Recommend): All actions require approval.
    # Level 2 (Require Approval): Medium/High/Critical require approval.
    # Level 3 (Auto Low-Risk): LOW risk auto-executes if policy allows; MEDIUM+ requires approval.
    # Level 4 (Policy Controlled): Auto-execute actions up to max_autonomous_risk threshold.

    if autonomy_level <= 1:
        requires_approval = True
        reason = f"Autonomy Level {autonomy_level} (Recommend/Observe Mode) requires explicit human approval for all actions."
    elif autonomy_level == 2:
        requires_approval = True
        reason = "Autonomy Level 2 configured: explicit approval required before remediation execution."
    elif autonomy_level == 3:
        if act_risk_val == 1:
            requires_approval = False
            reason = "Autonomy Level 3 configured: LOW-risk action permits automatic execution."
        else:
            requires_approval = True
            reason = f"Action risk '{risk_level}' exceeds Level 3 auto-execution threshold (LOW risk only)."
    else:  # Level 4
        if act_risk_val <= max_risk_val:
            requires_approval = False
            reason = f"Autonomy Level 4 configured: action risk '{risk_level}' is within allowed threshold '{max_risk}'."
        else:
            requires_approval = True
            reason = f"Action risk '{risk_level}' exceeds maximum policy autonomous risk threshold '{max_risk}'."

    # Production override guardrail
    if environment.lower() == "production" and risk_level.upper() in ("HIGH", "CRITICAL"):
        requires_approval = True
        reason = f"Production environment guardrail: {risk_level} risk actions unconditionally require approval."

    status = "PENDING" if requires_approval else "NOT_REQUIRED"

    return {
        "requires_approval": requires_approval,
        "approval_status": status,
        "autonomy_level": autonomy_level,
        "max_risk_allowed": max_risk,
        "reason": reason,
    }
