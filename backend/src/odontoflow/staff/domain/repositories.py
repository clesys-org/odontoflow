"""Staff Repository Protocols."""
from __future__ import annotations

from datetime import date
from typing import Optional, Protocol
from uuid import UUID

from odontoflow.staff.domain.models import ProductionEntry, StaffMember


class StaffRepository(Protocol):
    async def get_by_id(self, staff_id: UUID) -> Optional[StaffMember]: ...

    async def get_all(self, tenant_id: UUID, active_only: bool = True) -> list[StaffMember]: ...

    async def save(self, member: StaffMember) -> None: ...

    async def update(self, member: StaffMember) -> None: ...


class ProductionRepository(Protocol):
    async def get_by_staff(
        self,
        staff_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[ProductionEntry]: ...

    async def save(self, entry: ProductionEntry) -> None: ...
