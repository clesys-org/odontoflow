"""Staff Bounded Context — Domain Models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot, Entity


class CommissionType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"


@dataclass(frozen=True)
class CommissionRule:
    """Value Object — regra de comissao por categoria de procedimento."""

    procedure_category: Optional[str] = None  # None = aplica a todos
    commission_type: CommissionType = CommissionType.PERCENTAGE
    value: int = 0  # porcentagem (0-100) ou centavos fixos

    def calculate_commission(self, revenue_centavos: int) -> int:
        """Calcula comissao baseada na receita."""
        if self.commission_type == CommissionType.PERCENTAGE:
            return int(revenue_centavos * self.value / 100)
        return self.value


@dataclass
class StaffMember(AggregateRoot):
    """Aggregate Root — profissional da clinica."""

    tenant_id: UUID = field(default=None)
    user_id: UUID = field(default=None)
    full_name: str = ""
    cro_number: Optional[str] = None
    specialty: Optional[str] = None
    commission_rules: list[CommissionRule] = field(default_factory=list)
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def deactivate(self) -> None:
        if not self.active:
            raise ValueError("Profissional ja esta inativo")
        self.active = False

    def activate(self) -> None:
        if self.active:
            raise ValueError("Profissional ja esta ativo")
        self.active = True

    def add_commission_rule(self, rule: CommissionRule) -> None:
        self.commission_rules.append(rule)

    def get_commission_for(
        self, procedure_category: Optional[str], revenue_centavos: int
    ) -> int:
        """Retorna comissao para uma categoria. Regra especifica > regra geral."""
        specific = [
            r for r in self.commission_rules
            if r.procedure_category == procedure_category and procedure_category is not None
        ]
        if specific:
            return specific[0].calculate_commission(revenue_centavos)

        general = [r for r in self.commission_rules if r.procedure_category is None]
        if general:
            return general[0].calculate_commission(revenue_centavos)

        return 0


@dataclass
class ProductionEntry(Entity):
    """Entity — registro de producao de um profissional."""

    staff_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    treatment_item_id: Optional[UUID] = None
    procedure_description: str = ""
    revenue_centavos: int = 0
    commission_centavos: int = 0
    patient_name: str = ""
    date: date = field(default_factory=lambda: date.today())
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
