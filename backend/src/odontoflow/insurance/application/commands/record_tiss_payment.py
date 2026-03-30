"""Use case — Registrar pagamento de guia TISS."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.insurance.domain.models import TISSRequest
from odontoflow.insurance.domain.repositories import TISSRequestRepository
from odontoflow.shared.domain.errors import NotFoundError


@dataclass
class RecordTISSPaymentCommand:
    """Input data para registro de pagamento de guia TISS."""

    request_id: UUID = field(default=None)
    paid_amount_centavos: int = 0
    glosa_amount_centavos: int = 0
    glosa_reason: Optional[str] = None

    async def execute(self, repo: TISSRequestRepository) -> TISSRequest:
        request = await repo.get_by_id(self.request_id)
        if not request:
            raise NotFoundError("TISSRequest", str(self.request_id))

        request.record_payment(
            paid_amount_centavos=self.paid_amount_centavos,
            glosa_amount_centavos=self.glosa_amount_centavos,
            glosa_reason=self.glosa_reason,
        )
        await repo.update(request)
        return request
