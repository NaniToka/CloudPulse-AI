"""
Server Infrastructure REST API Endpoints.
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.models.user import User
from app.schemas.infrastructure import ServerCreate, ServerUpdate, ServerResponse
from app.services.server_service import server_service, ServerService

router = APIRouter()


@router.get("", response_model=List[ServerResponse], summary="List Monitored Servers")
async def list_servers(
    provider: Optional[str] = Query(None, description="Filter by cloud provider (AWS, GCP, Azure, on-prem)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (healthy, degraded, down, offline)"),
    search: Optional[str] = Query(None, description="Search server name, IP, hostname"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: ServerService = Depends(lambda: server_service),
):
    """Retrieve all monitored server nodes for the current user."""
    servers = await service.get_servers(
        db, user_id=current_user.id, provider=provider, status=status_filter, search=search
    )
    return [ServerResponse.model_validate(s) for s in servers]


@router.post("", response_model=ServerResponse, status_code=status.HTTP_201_CREATED, summary="Register Server")
async def create_server(
    payload: ServerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: ServerService = Depends(lambda: server_service),
):
    """Register a new server or cloud compute instance."""
    server = await service.create_server(db, user_id=current_user.id, payload=payload)
    return ServerResponse.model_validate(server)


@router.get("/{server_id}", response_model=ServerResponse, summary="Get Server Details")
async def get_server(
    server_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: ServerService = Depends(lambda: server_service),
):
    """Fetch details of a single server by ID."""
    server = await service.get_server(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return ServerResponse.model_validate(server)


@router.patch("/{server_id}", response_model=ServerResponse, summary="Update Server Status/Metrics")
async def update_server(
    server_id: uuid.UUID,
    payload: ServerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: ServerService = Depends(lambda: server_service),
):
    """Update server metadata or telemetry state."""
    server = await service.update_server(db, server_id, payload)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return ServerResponse.model_validate(server)


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove Server")
async def delete_server(
    server_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
    service: ServerService = Depends(lambda: server_service),
):
    """Delete a monitored server node."""
    success = await service.delete_server(db, server_id)
    if not success:
        raise HTTPException(status_code=404, detail="Server not found")
    return None
