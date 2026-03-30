"""Use case — Faturar guia TISS."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.insurance.domain.models import TISSRequest
from odontoflow.insurance.domain.repositories import TISSRequestRepository
from odontoflow.shared.domain.errors import NotFoundError


@dataclass
class BillTISSCommand:
    """Input data para faturamento de guia TISS."""

    request_id: UUID = field(default=None)

    async def execute(self, repo: TISSRequestRepository) -> TISSRequest:
        request = await repo.get_by_id(self.request_id)
        if not request:
            raise NotFoundError("TISSRequest", str(self.request_id))

        request.bill()
        await repo.update(request)
        return request
