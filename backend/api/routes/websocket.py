"""
WebSocket endpoint for real-time test execution updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio
import json

router = APIRouter()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/test/{test_id}")
async def websocket_test_updates(websocket: WebSocket, test_id: str):
    """WebSocket endpoint for real-time test execution updates"""
    await websocket.accept()
    active_connections[test_id] = websocket

    try:
        # Keep connection alive and send updates
        while True:
            # Wait for messages from client (ping/pong)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                # Echo back for ping/pong
                await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                # Send periodic status updates
                from src.tests.config import TestConfigManager

                with TestConfigManager() as manager:
                    test = manager.get(test_id)
                    if test:
                        await websocket.send_json({
                            "type": "status_update",
                            "test_id": test_id,
                            "status": test.status.value
                        })

    except WebSocketDisconnect:
        if test_id in active_connections:
            del active_connections[test_id]


async def send_test_update(test_id: str, message: dict):
    """Send update to connected WebSocket client"""
    if test_id in active_connections:
        try:
            await active_connections[test_id].send_json(message)
        except Exception:
            # Connection closed, remove it
            del active_connections[test_id]
