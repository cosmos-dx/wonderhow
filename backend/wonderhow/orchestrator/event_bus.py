from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)

EventHandler = Callable[[dict], Awaitable[None]]


class EventBus:
    """Simple in-process async pub/sub event bus."""

    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._queue: asyncio.Queue[tuple[str, dict]] = asyncio.Queue()
        self._running = False

    def subscribe(self, event_type: str, handler: EventHandler):
        self._handlers[event_type].append(handler)

    async def publish(self, event_type: str, data: dict):
        await self._queue.put((event_type, data))

    async def run(self):
        self._running = True
        while self._running:
            try:
                event_type, data = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            handlers = self._handlers.get(event_type, [])
            for handler in handlers:
                try:
                    await handler(data)
                except Exception:
                    logger.exception("Event handler error for %s", event_type)

    def stop(self):
        self._running = False
