"""Treatment Plans — Domain Models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot, Entity
from odontoflow.shared.domain.errors import ValidationError
from odontoflow.shared.domain.events import TreatmentItemCompleted, TreatmentPlanApproved
from odontoflow.shared.domain.types import TreatmentPlanStatus


class ItemStatus(str, Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class ProcedureCatalog(Entity):
    """Catalogo de procedimentos odontologicos (TUSS)."""

    tuss_code: str = ""
    description: str = ""
    category: str = ""
    default_price_centavos: int = 0
    active: bool = True

    def deactivate(self) -> None:
        self.active = False


@dataclass
class TreatmentItem(Entity):
    """Item individual de um plano de tratamento."""

    plan_id: UUID = field(default=None)
    phase_number: int = 1
    phase_name: str = ""
    procedure_id: Optional[UUID] = None
    tuss_code: str = ""
    description: str = ""
    tooth_number: Optional[int] = None
    surface: Optional[str] = None
    quantity: int = 1
    unit_price_centavos: int = 0
    status: ItemStatus = ItemStatus.PENDING
    executed_at: Optional[datetime] = None
    executed_by: Optional[str] = None
    sort_order: int = 0


@dataclass
class TreatmentPlan(AggregateRoot):
    """Aggregate Root — Plano de tratamento odontologico."""

    patient_id: UUID = field(default=None)
    provider_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    title: str = ""
    status: TreatmentPlanStatus = TreatmentPlanStatus.DRAFT
    items: list[TreatmentItem] = field(default_factory=list)
    discount_centavos: int = 0
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def total_value_centavos(self) -> int:
        total = sum(item.unit_price_centavos * item.quantity for item in self.items)
        return total - self.discount_centavos

    def approve(self, by: str) -> None:
        if self.status not in (TreatmentPlanStatus.DRAFT, TreatmentPlanStatus.PROPOSED):
            raise ValidationError(
                f"Plano nao pode ser aprovado no status {self.status.value}"
            )
        self.status = TreatmentPlanStatus.APPROVED
        self.approved_at = datetime.now(timezone.utc)
        self.approved_by = by
        self.add_event(
            TreatmentPlanApproved(
                plan_id=self.id,
                patient_id=self.patient_id,
                total_value_centavos=self.total_value_centavos,
                tenant_id=self.tenant_id,
            )
        )

    def start(self) -> None:
        if self.status != TreatmentPlanStatus.APPROVED:
            raise ValidationError(
                f"Plano precisa estar APPROVED para iniciar, status atual: {self.status.value}"
            )
        self.status = TreatmentPlanStatus.IN_PROGRESS

    def complete(self) -> None:
        if self.status != TreatmentPlanStatus.IN_PROGRESS:
            raise ValidationError(
                f"Plano precisa estar IN_PROGRESS para completar, status atual: {self.status.value}"
            )
        pending = [
            i for i in self.items
            if i.status not in (ItemStatus.COMPLETED, ItemStatus.CANCELLED)
        ]
        if pending:
            raise ValidationError(
                f"Existem {len(pending)} item(ns) nao finalizados no plano"
            )
        self.status = TreatmentPlanStatus.COMPLETED

    def cancel(self) -> None:
        if self.status == TreatmentPlanStatus.COMPLETED:
            raise ValidationError("Plano ja concluido nao pode ser cancelado")
        self.status = TreatmentPlanStatus.CANCELLED

    def add_item(self, item: TreatmentItem) -> None:
        item.plan_id = self.id
        self.items.append(item)

    def execute_item(self, item_id: UUID, executed_by: str) -> TreatmentItem:
        item = next((i for i in self.items if i.id == item_id), None)
        if not item:
            raise ValidationError(f"Item {item_id} nao encontrado no plano")
        if item.status != ItemStatus.PENDING and item.status != ItemStatus.SCHEDULED:
            raise ValidationError(
                f"Item nao pode ser executado no status {item.status.value}"
            )
        item.status = ItemStatus.COMPLETED
        item.executed_at = datetime.now(timezone.utc)
        item.executed_by = executed_by
        self.add_event(
            TreatmentItemCompleted(
                plan_id=self.id,
                item_id=item.id,
                procedure_code=item.tuss_code,
                tenant_id=self.tenant_id,
            )
        )
        return item

    def remove_item(self, item_id: UUID) -> None:
        item = next((i for i in self.items if i.id == item_id), None)
        if not item:
            raise ValidationError(f"Item {item_id} nao encontrado no plano")
        if item.status == ItemStatus.COMPLETED:
            raise ValidationError("Item ja executado nao pode ser removido")
        self.items.remove(item)
