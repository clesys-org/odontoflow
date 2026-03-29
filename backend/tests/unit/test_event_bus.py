"""Testes do EventBus."""

import pytest

from odontoflow.shared.domain.entity import DomainEvent
from odontoflow.shared.event_bus import EventBus


class TestEventBus:
    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        bus = EventBus()
        received = []

        async def handler(event: DomainEvent):
            received.append(event)

        bus.subscribe(DomainEvent, handler)
        event = DomainEvent()
        await bus.publish(event)

        assert len(received) == 1
        assert received[0] is event

    @pytest.mark.asyncio
    async def test_handler_error_does_not_break_others(self):
        bus = EventBus()
        results = []

        async def failing_handler(event: DomainEvent):
            raise ValueError("boom")

        async def good_handler(event: DomainEvent):
            results.append("ok")

        bus.subscribe(DomainEvent, failing_handler)
        bus.subscribe(DomainEvent, good_handler)
        await bus.publish(DomainEvent())

        assert results == ["ok"]

    @pytest.mark.asyncio
    async def test_no_handlers(self):
        bus = EventBus()
        await bus.publish(DomainEvent())  # Should not raise

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        bus = EventBus()
        received = []

        async def handler(event: DomainEvent):
            received.append(event)

        bus.subscribe(DomainEvent, handler)
        bus.unsubscribe(DomainEvent, handler)
        await bus.publish(DomainEvent())

        assert len(received) == 0
