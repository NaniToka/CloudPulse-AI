"""
Digital Twin Infrastructure REST API Endpoints.
"""

import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.models.user import User
from app.models.digital_twin import InfrastructureTwin, SimulationScenario, SimulationExecution
from app.schemas.digital_twin_schemas import (
    InfrastructureTwinResponse,
    SimulationScenarioResponse,
    SimulationScenarioCreate,
    SimulationExecutionResponse,
    WhatIfQueryRequest,
    WhatIfQueryResponse,
    BlastRadiusDetailResponse,
)
from app.crud.crud_digital_twin import crud_twin, crud_scenario, crud_execution, crud_what_if
from app.services.digital_twin_service import digital_twin_service, DigitalTwinService

router = APIRouter()


@router.get("", response_model=InfrastructureTwinResponse, summary="Get Digital Twin")
async def get_twin(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: DigitalTwinService = Depends(lambda: digital_twin_service),
):
    """Retrieve the virtual Digital Twin topology graph and health score."""
    twin = await service.get_or_create_twin(db, user_id=current_user.id)
    return InfrastructureTwinResponse.model_validate(twin)


@router.get("/resources", summary="List Twin Virtual Resources")
async def get_twin_resources(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: DigitalTwinService = Depends(lambda: digital_twin_service),
):
    """List all virtual nodes, pods, databases, caches, and load balancers."""
    twin = await service.get_or_create_twin(db, user_id=current_user.id)
    return twin.virtual_resources


@router.get("/simulations", response_model=List[SimulationScenarioResponse], summary="List Simulation Scenarios")
async def list_scenarios(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: DigitalTwinService = Depends(lambda: digital_twin_service),
):
    """List available failure injection scenarios."""
    twin = await service.get_or_create_twin(db, user_id=current_user.id)
    scenarios = await service.get_scenarios(db, twin_id=twin.id, category=category)
    return [SimulationScenarioResponse.model_validate(s) for s in scenarios]


@router.post("/simulations", response_model=SimulationScenarioResponse, status_code=status.HTTP_201_CREATED, summary="Create Scenario")
async def create_scenario(
    payload: SimulationScenarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: DigitalTwinService = Depends(lambda: digital_twin_service),
):
    """Create a new custom chaos failure scenario."""
    twin = await service.get_or_create_twin(db, user_id=current_user.id)
    now = datetime.now(timezone.utc)
    sc = SimulationScenario(
        id=uuid.uuid4(),
        twin_id=twin.id,
        name=payload.name,
        category=payload.category,
        failure_type=payload.failure_type,
        target_resource=payload.target_resource,
        description=payload.description,
        parameters=payload.parameters,
        severity=payload.severity,
        created_at=now,
        updated_at=now,
    )
    db.add(sc)
    await db.commit()
    await db.refresh(sc)
    return SimulationScenarioResponse.model_validate(sc)


@router.post("/simulations/{scenario_id}/run", response_model=SimulationExecutionResponse, summary="Run Simulation")
async def run_simulation(
    scenario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: DigitalTwinService = Depends(lambda: digital_twin_service),
):
    """Execute failure simulation and calculate cascade blast radius."""
    twin = await service.get_or_create_twin(db, user_id=current_user.id)
    sc = await crud_scenario.get(db, id=scenario_id)
    if not sc or sc.twin_id != twin.id:
        raise HTTPException(status_code=404, detail="Simulation scenario not found")

    execution = await service.run_simulation(db, twin=twin, scenario=sc)
    return SimulationExecutionResponse.model_validate(execution)


@router.get("/simulations/history", response_model=List[SimulationExecutionResponse], summary="List History")
async def list_simulation_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: DigitalTwinService = Depends(lambda: digital_twin_service),
):
    """List historical simulation runs, risk scores, and financial losses."""
    twin = await service.get_or_create_twin(db, user_id=current_user.id)
    executions = await crud_execution.get_multi_by_twin(db, twin_id=twin.id)
    return [SimulationExecutionResponse.model_validate(e) for e in executions]


@router.get("/blast-radius/{scenario_id}", response_model=BlastRadiusDetailResponse, summary="Get Blast Radius")
async def get_blast_radius(
    scenario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: DigitalTwinService = Depends(lambda: digital_twin_service),
):
    """Inspect the blast radius overlay and cascade degradation map for a scenario."""
    twin = await service.get_or_create_twin(db, user_id=current_user.id)
    sc = await crud_scenario.get(db, id=scenario_id)
    if not sc or sc.twin_id != twin.id:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Run virtual calculation if not already executed
    execution = await service.run_simulation(db, twin=twin, scenario=sc)
    return BlastRadiusDetailResponse(
        scenario_id=sc.id,
        scenario_name=sc.name,
        risk_score=execution.risk_score,
        affected_services=execution.affected_services,
        financial_impact_usd=execution.financial_impact_usd,
        estimated_recovery_minutes=execution.estimated_recovery_minutes,
        blast_radius=execution.blast_radius,
        timeline=execution.predicted_timeline,
        recovery_steps=execution.recovery_steps,
    )


@router.post("/what-if", response_model=WhatIfQueryResponse, summary="Ask What-If Question")
async def ask_what_if(
    payload: WhatIfQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: DigitalTwinService = Depends(lambda: digital_twin_service),
):
    """Evaluate natural language What-If question using Gemini AI."""
    res = await service.evaluate_what_if(db, user_id=current_user.id, prompt=payload.query)
    return WhatIfQueryResponse.model_validate(res)
