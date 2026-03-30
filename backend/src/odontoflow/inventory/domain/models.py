"""Inventory (Estoque) — Domain Models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot, Entity
from odontoflow.shared.domain.errors import ValidationError


class StockMovementType(str, Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    ADJUSTMENT = "ADJUSTMENT"


@dataclass
class StockMovement(Entity):
    """Movimentacao de estoque."""

    material_id: UUID = field(default=None)
    movement_type: StockMovementType = StockMovementType.ENTRY
    quantity: int = 0
    reason: str = ""
    created_by: UUID = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Material(AggregateRoot):
    """Aggregate Root — Material odontologico em estoque."""

    tenant_id: UUID = field(default=None)
    name: str = ""
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str = "un"  # un, ml, g, cx
    current_stock: int = 0
    min_stock: int = 0
    cost_centavos: int = 0
    supplier: Optional[str] = None
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_low_stock(self) -> bool:
        """Retorna True se estoque atual esta abaixo do minimo."""
        return self.current_stock < self.min_stock

    def add_stock(self, quantity: int, reason: str) -> StockMovement:
        """Entrada de estoque."""
        if quantity <= 0:
            raise ValidationError("Quantidade de entrada deve ser maior que zero")
        if not reason or not reason.strip():
            raise ValidationError("Motivo da movimentacao e obrigatorio")
        self.current_stock += quantity
        return StockMovement(
            material_id=self.id,
            movement_type=StockMovementType.ENTRY,
            quantity=quantity,
            reason=reason.strip(),
        )

    def remove_stock(self, quantity: int, reason: str) -> StockMovement:
        """Saida de estoque."""
        if quantity <= 0:
            raise ValidationError("Quantidade de saida deve ser maior que zero")
        if not reason or not reason.strip():
            raise ValidationError("Motivo da movimentacao e obrigatorio")
        if quantity > self.current_stock:
            raise ValidationError(
                f"Estoque insuficiente: disponivel {self.current_stock}, solicitado {quantity}"
            )
        self.current_stock -= quantity
        return StockMovement(
            material_id=self.id,
            movement_type=StockMovementType.EXIT,
            quantity=quantity,
            reason=reason.strip(),
        )

    def adjust_stock(self, new_quantity: int, reason: str) -> StockMovement:
        """Ajuste de inventario (contagem fisica)."""
        if new_quantity < 0:
            raise ValidationError("Quantidade ajustada nao pode ser negativa")
        if not reason or not reason.strip():
            raise ValidationError("Motivo do ajuste e obrigatorio")
        diff = new_quantity - self.current_stock
        self.current_stock = new_quantity
        return StockMovement(
            material_id=self.id,
            movement_type=StockMovementType.ADJUSTMENT,
            quantity=diff,
            reason=reason.strip(),
        )

    def deactivate(self) -> None:
        self.active = False


@dataclass
class Supplier(Entity):
    """Fornecedor de materiais."""

    tenant_id: UUID = field(default=None)
    name: str = ""
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
