from __future__ import annotations

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from wonderhow.models.message import ChatMessage

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, group_slug: str):
        await websocket.accept()
        if group_slug not in self.active:
            self.active[group_slug] = []
        self.active[group_slug].append(websocket)
        logger.info("WebSocket connected to group: %s (total: %d)",
                     group_slug, len(self.active[group_slug]))

    def disconnect(self, websocket: WebSocket, group_slug: str):
        if group_slug in self.active:
            self.active[group_slug] = [
                ws for ws in self.active[group_slug] if ws is not websocket
            ]

    async def broadcast_to_group(self, group_id: str, message: ChatMessage):
        from wonderhow.main import orchestrator
        group = None
        for g in orchestrator.group_manager.get_all_groups():
            if g.id == group_id:
                group = g
                break
        if not group:
            return

        slug = group.slug
        connections = self.active.get(slug, [])
        data = message.model_dump(mode="json")

        dead = []
        for ws in connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect(ws, slug)

    async def broadcast_all(self, message: ChatMessage):
        await self.broadcast_to_group(message.group_id, message)


manager = ConnectionManager()


@router.websocket("/chat/{group_slug}")
async def websocket_endpoint(websocket: WebSocket, group_slug: str):
    from wonderhow.main import orchestrator

    await manager.connect(websocket, group_slug)
    orchestrator.register_ws_callback(manager.broadcast_all)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
                msg_type = data.get("type", "")
                if msg_type == "user_message":
                    text = data.get("text", "").strip()
                    username = data.get("username", "User")
                    if text:
                        await orchestrator.handle_user_message(group_slug, text, username)
            except json.JSONDecodeError:
                logger.debug("Non-JSON WS message: %s", raw[:100])
    except WebSocketDisconnect:
        manager.disconnect(websocket, group_slug)
        logger.info("WebSocket disconnected from group: %s", group_slug)
