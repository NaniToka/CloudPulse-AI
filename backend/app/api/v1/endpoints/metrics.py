"""
Real-Time Observability Platform API Endpoints & WebSocket Router.
"""

import asyncio

import structlog
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.metrics_service import (
    MetricsService,
    generate_live_telemetry_point,
    metrics_service,
)
from app.services.websocket_manager import ConnectionManager

log = structlog.get_logger(__name__)

router = APIRouter()
metrics_ws_manager = ConnectionManager()


def get_metrics_service() -> MetricsService:
    return metrics_service


@router.get("/current", summary="Get current live metric point")
async def get_current_metrics(
    db: AsyncSession = Depends(get_db),
    service: MetricsService = Depends(get_metrics_service),
):
    """Retrieve current single live telemetry metric point."""
    current_point = await service.get_current(db)
    return {
        "current": current_point,
        "is_live": True,
        "update_interval_ms": 2000,
    }


@router.get("/history", summary="Get telemetry history sliding window")
async def get_metrics_history(
    limit: int = Query(
        300, ge=10, le=1000, description="Max data points to return (sliding window)"
    ),
    db: AsyncSession = Depends(get_db),
    service: MetricsService = Depends(get_metrics_service),
):
    """Retrieve up to 300 historical telemetry points for sliding window visualizations."""
    history = await service.get_history(db, limit=limit)
    return {
        "history": history,
        "total_points": len(history),
        "buffer_size": 300,
    }


@router.websocket("/ws")
async def metrics_websocket_endpoint(websocket: WebSocket):
    """Real-time WebSocket endpoint streaming telemetry metrics every 2 seconds."""
    await metrics_ws_manager.connect(websocket)
    log.info("metrics_websocket_client_connected")
    try:
        while True:
            # Stream fresh telemetry point every 2000ms
            telemetry_point = generate_live_telemetry_point()
            payload = {
                "event": "telemetry_update",
                "data": telemetry_point,
            }
            await websocket.send_json(payload)
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        metrics_ws_manager.disconnect(websocket)
        log.info("metrics_websocket_client_disconnected")
    except Exception as exc:
        metrics_ws_manager.disconnect(websocket)
        log.error("metrics_websocket_error", error=str(exc))
