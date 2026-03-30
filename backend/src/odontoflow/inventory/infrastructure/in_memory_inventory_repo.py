"""In-memory implementation of Inventory repositories for testing."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from odontoflow.inventory.domain.models import Material, Supplier


class InMemoryMaterialRepository:
    """Dict-based material repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, Material] = {}

    async def get_by_id(self, material_id: UUID) -> Optional[Material]:
        return self._store.get(material_id)

    async def get_all(
        self,
        tenant_id: UUID,
        low_stock_only: bool = False,
    ) -> list[Material]:
        materials = [
            m for m in self._store.values()
            if m.tenant_id == tenant_id and m.active
        ]
        if low_stock_only:
            materials = [m for m in materials if m.is_low_stock]
        return materials

    async def save(self, material: Material) -> None:
        self._store[material.id] = material

    async def update(self, material: Material) -> None:
        self._store[material.id] = material


class InMemorySupplierRepository:
    """Dict-based supplier repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, Supplier] = {}

    async def get_by_id(self, supplier_id: UUID) -> Optional[Supplier]:
        return self._store.get(supplier_id)

    async def get_all(self, tenant_id: UUID) -> list[Supplier]:
        return [
            s for s in self._store.values()
            if s.tenant_id == tenant_id
        ]

    async def save(self, supplier: Supplier) -> None:
        self._store[supplier.id] = supplier
