"""Query — Listar profissionais."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from odontoflow.staff.domain.models import StaffMember
from odontoflow.staff.domain.repositories import StaffRepository


@dataclass
class ListStaffQuery:
    tenant_id: UUID
    active_only: bool = True

    async def execute(self, repo: StaffRepository) -> list[StaffMember]:
        return await repo.get_all(self.tenant_id, active_only=self.active_only)
