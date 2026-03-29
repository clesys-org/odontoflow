"""Testes das classes base Entity e AggregateRoot."""

from uuid import uuid4

from odontoflow.shared.domain.entity import AggregateRoot, DomainEvent, Entity


class TestEntity:
    def test_has_default_id(self):
        e = Entity()
        assert e.id is not None

    def test_equality_by_id(self):
        uid = uuid4()
        e1 = Entity(id=uid)
        e2 = Entity(id=uid)
        assert e1 == e2

    def test_inequality(self):
        assert Entity() != Entity()

    def test_hashable(self):
        e = Entity()
        s = {e}
        assert e in s


class TestAggregateRoot:
    def test_collects_events(self):
        agg = AggregateRoot()
        event = DomainEvent()
        agg.add_event(event)
        events = agg.collect_events()
        assert len(events) == 1
        assert events[0] is event

    def test_collect_clears_events(self):
        agg = AggregateRoot()
        agg.add_event(DomainEvent())
        agg.collect_events()
        assert len(agg.collect_events()) == 0


class TestDomainEvent:
    def test_has_id_and_timestamp(self):
        event = DomainEvent()
        assert event.event_id is not None
        assert event.occurred_at is not None
