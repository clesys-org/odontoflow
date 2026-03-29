"""Shared Kernel — Event Bus in-process (pub/sub async)."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any

from odontoflow.shared.domain.entity import DomainEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventBus:
    """Event bus in-process com suporte a handlers assincronos."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)
        logger.debug("Handler %s subscribed to %s", handler.__name__, event_type.__name__)

    def unsubscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    async def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        if not handlers:
            logger.debug("No handlers for %s", event_type.__name__)
            return

        logger.info(
            "Publishing %s (id=%s) to %d handler(s)",
            event_type.__name__,
            event.event_id,
            len(handlers),
        )

        tasks = [self._safe_call(handler, event) for handler in handlers]
        await asyncio.gather(*tasks)

    async def _safe_call(self, handler: EventHandler, event: DomainEvent) -> None:
        try:
            await handler(event)
        except Exception:
            logger.exception(
                "Error in handler %s for event %s",
                handler.__name__,
                type(event).__name__,
            )
