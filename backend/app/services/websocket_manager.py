"""
WebSocket Connection Manager for Incident Management Center real-time updates.
"""

from typing import List, Dict, Any
from fastapi import WebSocket
import structlog

log = structlog.get_logger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts real-time incident notifications."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        log.info("websocket_client_connected", active_total=len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            log.info("websocket_client_disconnected", active_total=len(self.active_connections))

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket) -> None:
        try:
            await websocket.send_json(message)
        except Exception as e:
            log.warning("websocket_send_failed", error=str(e))

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast event to all connected WebSocket clients."""
        log.info("websocket_broadcasting", event_type=message.get("event"), active_clients=len(self.active_connections))
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                log.warning("websocket_broadcast_failed_for_client", error=str(e))
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)


# Singleton instance
incident_ws_manager = ConnectionManager()
