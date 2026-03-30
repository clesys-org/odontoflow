"""In-memory implementation of Staff repositories for testing."""
from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from odontoflow.staff.domain.models import ProductionEntry, StaffMember


class InMemoryStaffRepository:
    """Dict-based staff repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, StaffMember] = {}

    async def get_by_id(self, staff_id: UUID) -> Optional[StaffMember]:
        return self._store.get(staff_id)

    async def get_all(self, tenant_id: UUID, active_only: bool = True) -> list[StaffMember]:
        members = [m for m in self._store.values() if m.tenant_id == tenant_id]
        if active_only:
            members = [m for m in members if m.active]
        return members

    async def save(self, member: StaffMember) -> None:
        self._store[member.id] = member

    async def update(self, member: StaffMember) -> None:
        self._store[member.id] = member


class InMemoryProductionRepository:
    """Dict-based production repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, ProductionEntry] = {}

    async def get_by_staff(
        self,
        staff_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[ProductionEntry]:
        entries = [e for e in self._store.values() if e.staff_id == staff_id]
        if start_date:
            entries = [e for e in entries if e.date >= start_date]
        if end_date:
            entries = [e for e in entries if e.date <= end_date]
        return sorted(entries, key=lambda e: e.date, reverse=True)

    async def save(self, entry: ProductionEntry) -> None:
        self._store[entry.id] = entry
