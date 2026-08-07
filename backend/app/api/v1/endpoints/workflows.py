"""
Workflow Automation REST API Endpoints.
"""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.crud.crud_workflow import crud_workflow, crud_workflow_execution
from app.models.user import User
from app.models.workflow import Workflow
from app.schemas.workflow_schemas import (
    WorkflowAIGenerateRequest,
    WorkflowApprovalDecision,
    WorkflowCreate,
    WorkflowExecutionResponse,
    WorkflowResponse,
    WorkflowTemplateResponse,
    WorkflowUpdate,
)
from app.services.workflow_engine_service import WorkflowEngineService, workflow_engine_service

router = APIRouter()


@router.get("", response_model=list[WorkflowResponse], summary="List Workflows")
async def list_workflows(
    status: str | None = Query(None, description="Filter by status (active, paused, draft)"),
    trigger_type: str | None = Query(None, description="Filter by trigger type"),
    search: str | None = Query(None, description="Search workflow name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: WorkflowEngineService = Depends(lambda: workflow_engine_service),
):
    """Retrieve user's automation workflows."""
    workflows = await service.get_workflows(
        db, user_id=current_user.id, status=status, trigger_type=trigger_type, search=search
    )
    return [WorkflowResponse.model_validate(w) for w in workflows]


@router.get(
    "/templates", response_model=list[WorkflowTemplateResponse], summary="List Workflow Templates"
)
async def list_templates(
    category: str | None = Query(
        None, description="Filter by category (Kubernetes, Security, Incident, Cost)"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: WorkflowEngineService = Depends(lambda: workflow_engine_service),
):
    """Retrieve pre-built enterprise automation templates."""
    templates = await service.get_templates(db, category=category)
    return [WorkflowTemplateResponse.model_validate(t) for t in templates]


@router.get(
    "/history", response_model=list[WorkflowExecutionResponse], summary="List Execution History"
)
async def list_history(
    workflow_id: uuid.UUID | None = Query(None, description="Filter by workflow ID"),
    status: str | None = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Retrieve recent workflow execution runs and duration metrics."""
    executions = await crud_workflow_execution.get_multi_by_user(
        db, user_id=current_user.id, workflow_id=workflow_id, status=status
    )
    return [WorkflowExecutionResponse.model_validate(e) for e in executions]


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Workflow",
)
async def create_workflow(
    payload: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Create a new automation workflow definition."""
    now = datetime.now(UTC)
    wf = Workflow(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        status=payload.status,
        trigger_type=payload.trigger_type,
        trigger_config=payload.trigger_config,
        nodes=payload.nodes,
        edges=payload.edges,
        tags=payload.tags,
        version=1,
        created_at=now,
        updated_at=now,
    )
    db.add(wf)
    await db.commit()
    await db.refresh(wf)
    return WorkflowResponse.model_validate(wf)


@router.get("/{workflow_id}", response_model=WorkflowResponse, summary="Get Workflow")
async def get_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Get workflow definition, nodes, and edges by ID."""
    wf = await crud_workflow.get(db, id=workflow_id)
    if not wf or wf.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse.model_validate(wf)


@router.put("/{workflow_id}", response_model=WorkflowResponse, summary="Update Workflow")
async def update_workflow(
    workflow_id: uuid.UUID,
    payload: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Update workflow nodes, edges, or configuration."""
    wf = await crud_workflow.get(db, id=workflow_id)
    if not wf or wf.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workflow not found")

    update_dict = payload.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.now(UTC)
    update_dict["version"] = wf.version + 1
    updated = await crud_workflow.update(db, db_obj=wf, obj_in=update_dict)
    return WorkflowResponse.model_validate(updated)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Workflow")
async def delete_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Delete a workflow definition."""
    wf = await crud_workflow.get(db, id=workflow_id)
    if not wf or wf.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    await crud_workflow.remove(db, id=workflow_id)


@router.post(
    "/{workflow_id}/execute",
    response_model=WorkflowExecutionResponse,
    summary="Trigger Workflow Execution",
)
async def execute_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: WorkflowEngineService = Depends(lambda: workflow_engine_service),
):
    """Execute an automated workflow immediately via DAG runner."""
    wf = await crud_workflow.get(db, id=workflow_id)
    if not wf or wf.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workflow not found")

    execution = await service.execute_workflow(db, workflow=wf, trigger_source="manual")
    return WorkflowExecutionResponse.model_validate(execution)


@router.post(
    "/{workflow_id}/approve",
    response_model=WorkflowExecutionResponse,
    summary="Decide Approval Gate",
)
async def approve_workflow(
    workflow_id: uuid.UUID,
    payload: WorkflowApprovalDecision,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: WorkflowEngineService = Depends(lambda: workflow_engine_service),
):
    """Approve or reject a paused workflow execution gate."""
    # Find execution with this approval
    executions = await crud_workflow_execution.get_multi_by_user(
        db, user_id=current_user.id, workflow_id=workflow_id
    )
    if not executions:
        raise HTTPException(status_code=404, detail="Execution not found")

    exec_target = executions[0]
    result = await service.decide_approval(
        db,
        execution_id=exec_target.id,
        approval_id=payload.approval_id,
        decision=payload.decision,
        reason=payload.reason,
    )
    return WorkflowExecutionResponse.model_validate(result)


@router.post("/generate-ai", summary="Generate Workflow using Gemini AI")
async def generate_workflow_ai(
    payload: WorkflowAIGenerateRequest,
    current_user: User = Depends(require_active_user),
    service: WorkflowEngineService = Depends(lambda: workflow_engine_service),
):
    """Synthesize natural language prompt into executable workflow DAG."""
    return await service.generate_workflow_from_ai(payload.prompt)
