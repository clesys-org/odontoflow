"""Query — Listar operadoras de convenio."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.insurance.domain.models import InsuranceProvider
from odontoflow.insurance.domain.repositories import InsuranceProviderRepository


@dataclass
class ListInsuranceProvidersQuery:
    """Input data para listagem de operadoras."""

    tenant_id: UUID = field(default=None)
    active_only: bool = True

    async def execute(self, repo: InsuranceProviderRepository) -> list[InsuranceProvider]:
        return await repo.get_all(
            tenant_id=self.tenant_id,
            active_only=self.active_only,
        )
