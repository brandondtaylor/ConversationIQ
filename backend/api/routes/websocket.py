"""
WebSocket endpoint for real-time test execution updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.api.websocket_manager import ws_manager
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/test/{test_id}")
async def websocket_test_updates(websocket: WebSocket, test_id: str):
    """
    WebSocket endpoint for real-time test execution updates.

    Clients can connect to receive:
    - Progress updates
    - Status changes
    - New evaluation results
    - Error messages
    """
    await ws_manager.connect(websocket, test_id)

    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for any message from client
            data = await websocket.receive_text()

            # Client can send ping to keep alive
            if data == "ping":
                await websocket.send_text('{"type": "pong"}')

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, test_id)
        logger.info(f"Client disconnected from test {test_id}")
    except Exception as e:
        logger.error(f"WebSocket error for test {test_id}: {e}")
        ws_manager.disconnect(websocket, test_id)
