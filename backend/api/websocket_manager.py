"""
WebSocket Manager for real-time test progress updates.
"""
from typing import Dict, Set
from fastapi import WebSocket
import logging
import json

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts messages to subscribed clients.
    """

    def __init__(self):
        """Initialize WebSocket manager."""
        # Dict mapping test_id to set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, test_id: str):
        """
        Accept a new WebSocket connection for a specific test.

        Args:
            websocket: WebSocket connection
            test_id: Test ID to subscribe to
        """
        await websocket.accept()

        if test_id not in self.active_connections:
            self.active_connections[test_id] = set()

        self.active_connections[test_id].add(websocket)
        logger.info(f"WebSocket connected for test {test_id}. Total connections: {len(self.active_connections[test_id])}")

    def disconnect(self, websocket: WebSocket, test_id: str):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
            test_id: Test ID
        """
        if test_id in self.active_connections:
            self.active_connections[test_id].discard(websocket)

            # Clean up empty sets
            if not self.active_connections[test_id]:
                del self.active_connections[test_id]

            logger.info(f"WebSocket disconnected for test {test_id}")

    async def send_message(self, test_id: str, message: Dict):
        """
        Send a message to all clients subscribed to a test.

        Args:
            test_id: Test ID
            message: Message dict to send
        """
        if test_id not in self.active_connections:
            return

        # Convert message to JSON
        message_json = json.dumps(message)

        # Send to all connected clients for this test
        disconnected = set()
        for websocket in self.active_connections[test_id]:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Failed to send message to websocket: {e}")
                disconnected.add(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket, test_id)

    async def broadcast_progress(self, test_id: str, progress_message: str, progress_percentage: float = None):
        """
        Broadcast progress update to all clients.

        Args:
            test_id: Test ID
            progress_message: Progress message
            progress_percentage: Optional progress percentage (0-100)
        """
        message = {
            "type": "progress",
            "test_id": test_id,
            "message": progress_message,
            "timestamp": None  # Will be set by client
        }

        if progress_percentage is not None:
            message["progress_percentage"] = progress_percentage

        await self.send_message(test_id, message)

    async def broadcast_evaluation(self, test_id: str, evaluation_data: Dict):
        """
        Broadcast new evaluation to all clients.

        Args:
            test_id: Test ID
            evaluation_data: Evaluation data dict
        """
        message = {
            "type": "evaluation",
            "test_id": test_id,
            "data": evaluation_data
        }

        await self.send_message(test_id, message)

    async def broadcast_status(self, test_id: str, status: str):
        """
        Broadcast test status change to all clients.

        Args:
            test_id: Test ID
            status: New status (running, completed, failed)
        """
        message = {
            "type": "status",
            "test_id": test_id,
            "status": status
        }

        await self.send_message(test_id, message)

    async def broadcast_error(self, test_id: str, error_message: str):
        """
        Broadcast error to all clients.

        Args:
            test_id: Test ID
            error_message: Error message
        """
        message = {
            "type": "error",
            "test_id": test_id,
            "message": error_message
        }

        await self.send_message(test_id, message)


# Global WebSocket manager instance
ws_manager = WebSocketManager()
