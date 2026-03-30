"""Use case — Submeter guia TISS."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.insurance.domain.models import TISSItem, TISSRequest
from odontoflow.insurance.domain.repositories import TISSRequestRepository
from odontoflow.shared.domain.errors import ValidationError


@dataclass
class TISSItemInput:
    tuss_code: str = ""
    description: str = ""
    tooth_number: Optional[int] = None
    quantity: int = 1


@dataclass
class SubmitTISSCommand:
    """Input data para submissao de guia TISS."""

    tenant_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    provider_id: UUID = field(default=None)
    insurance_provider_id: UUID = field(default=None)
    treatment_plan_id: Optional[UUID] = None
    items: list[TISSItemInput] = field(default_factory=list)

    async def execute(self, repo: TISSRequestRepository) -> TISSRequest:
        if not self.items:
            raise ValidationError("Guia TISS precisa ter ao menos um item")

        tiss_items = [
            TISSItem(
                tuss_code=item.tuss_code,
                description=item.description,
                tooth_number=item.tooth_number,
                quantity=item.quantity,
            )
            for item in self.items
        ]

        request = TISSRequest(
            tenant_id=self.tenant_id,
            patient_id=self.patient_id,
            provider_id=self.provider_id,
            insurance_provider_id=self.insurance_provider_id,
            treatment_plan_id=self.treatment_plan_id,
            items=tiss_items,
        )

        request.submit()
        await repo.save(request)
        return request
