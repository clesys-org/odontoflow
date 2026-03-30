"""Query — Listar fornecedores."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.inventory.domain.models import Supplier
from odontoflow.inventory.domain.repositories import SupplierRepository


@dataclass
class ListSuppliersQuery:
    """Input data para listagem de fornecedores."""

    tenant_id: UUID = field(default=None)

    async def execute(self, repo: SupplierRepository) -> list[Supplier]:
        return await repo.get_all(tenant_id=self.tenant_id)
