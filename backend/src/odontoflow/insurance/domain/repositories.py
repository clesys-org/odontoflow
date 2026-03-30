"""Insurance Repository Protocols."""
from __future__ import annotations

from typing import Optional, Protocol
from uuid import UUID

from odontoflow.insurance.domain.models import InsuranceProvider, TISSRequest, TISSStatus


class InsuranceProviderRepository(Protocol):
    async def get_by_id(self, provider_id: UUID) -> Optional[InsuranceProvider]: ...

    async def get_all(self, tenant_id: UUID, active_only: bool = True) -> list[InsuranceProvider]: ...

    async def save(self, provider: InsuranceProvider) -> None: ...

    async def update(self, provider: InsuranceProvider) -> None: ...


class TISSRequestRepository(Protocol):
    async def get_by_id(self, request_id: UUID) -> Optional[TISSRequest]: ...

    async def get_all(
        self,
        tenant_id: UUID,
        status: Optional[TISSStatus] = None,
        patient_id: Optional[UUID] = None,
    ) -> list[TISSRequest]: ...

    async def save(self, request: TISSRequest) -> None: ...

    async def update(self, request: TISSRequest) -> None: ...
