"""Inventory Repository Protocols."""
from __future__ import annotations

from typing import Optional, Protocol
from uuid import UUID

from odontoflow.inventory.domain.models import Material, Supplier


class MaterialRepository(Protocol):
    async def get_by_id(self, material_id: UUID) -> Optional[Material]: ...

    async def get_all(
        self,
        tenant_id: UUID,
        low_stock_only: bool = False,
    ) -> list[Material]: ...

    async def save(self, material: Material) -> None: ...

    async def update(self, material: Material) -> None: ...


class SupplierRepository(Protocol):
    async def get_by_id(self, supplier_id: UUID) -> Optional[Supplier]: ...

    async def get_all(self, tenant_id: UUID) -> list[Supplier]: ...

    async def save(self, supplier: Supplier) -> None: ...
