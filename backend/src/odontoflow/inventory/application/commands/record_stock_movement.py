"""Use case — Registrar movimentacao de estoque."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.inventory.domain.models import Material, StockMovement, StockMovementType
from odontoflow.inventory.domain.repositories import MaterialRepository
from odontoflow.shared.domain.errors import NotFoundError, ValidationError


@dataclass
class RecordStockMovementCommand:
    """Input data para movimentacao de estoque."""

    material_id: UUID = field(default=None)
    movement_type: StockMovementType = StockMovementType.ENTRY
    quantity: int = 0
    reason: str = ""
    created_by: UUID = field(default=None)

    async def execute(self, repo: MaterialRepository) -> tuple[Material, StockMovement]:
        material = await repo.get_by_id(self.material_id)
        if not material:
            raise NotFoundError("Material", str(self.material_id))

        if self.movement_type == StockMovementType.ENTRY:
            movement = material.add_stock(self.quantity, self.reason)
        elif self.movement_type == StockMovementType.EXIT:
            movement = material.remove_stock(self.quantity, self.reason)
        elif self.movement_type == StockMovementType.ADJUSTMENT:
            movement = material.adjust_stock(self.quantity, self.reason)
        else:
            raise ValidationError(f"Tipo de movimentacao invalido: {self.movement_type}")

        movement.created_by = self.created_by
        await repo.update(material)
        return material, movement
