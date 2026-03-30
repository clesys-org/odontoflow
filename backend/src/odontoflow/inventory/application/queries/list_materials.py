"""Query — Listar materiais."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.inventory.domain.models import Material
from odontoflow.inventory.domain.repositories import MaterialRepository


@dataclass
class ListMaterialsQuery:
    """Input data para listagem de materiais."""

    tenant_id: UUID = field(default=None)
    low_stock_only: bool = False

    async def execute(self, repo: MaterialRepository) -> list[Material]:
        return await repo.get_all(
            tenant_id=self.tenant_id,
            low_stock_only=self.low_stock_only,
        )
