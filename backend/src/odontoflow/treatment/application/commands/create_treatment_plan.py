"""Use case — Criar plano de tratamento."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.errors import ValidationError
from odontoflow.treatment.domain.models import TreatmentItem, TreatmentPlan
from odontoflow.treatment.domain.repositories import TreatmentPlanRepository


@dataclass
class TreatmentItemInput:
    phase_number: int = 1
    phase_name: str = ""
    procedure_id: Optional[UUID] = None
    tuss_code: str = ""
    description: str = ""
    tooth_number: Optional[int] = None
    surface: Optional[str] = None
    quantity: int = 1
    unit_price_centavos: int = 0
    sort_order: int = 0


@dataclass
class CreateTreatmentPlanCommand:
    """Input data para criacao de plano de tratamento."""

    patient_id: UUID = field(default=None)
    provider_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    title: str = ""
    items: list[TreatmentItemInput] = field(default_factory=list)
    discount_centavos: int = 0

    async def execute(self, repo: TreatmentPlanRepository) -> TreatmentPlan:
        if not self.title or not self.title.strip():
            raise ValidationError("Titulo do plano e obrigatorio.")

        plan = TreatmentPlan(
            patient_id=self.patient_id,
            provider_id=self.provider_id,
            tenant_id=self.tenant_id,
            title=self.title.strip(),
            discount_centavos=self.discount_centavos,
        )

        for item_input in self.items:
            item = TreatmentItem(
                plan_id=plan.id,
                phase_number=item_input.phase_number,
                phase_name=item_input.phase_name,
                procedure_id=item_input.procedure_id,
                tuss_code=item_input.tuss_code,
                description=item_input.description,
                tooth_number=item_input.tooth_number,
                surface=item_input.surface,
                quantity=item_input.quantity,
                unit_price_centavos=item_input.unit_price_centavos,
                sort_order=item_input.sort_order,
            )
            plan.add_item(item)

        await repo.save(plan)
        return plan
