"""In-memory implementation of Insurance repositories for testing."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from odontoflow.insurance.domain.models import InsuranceProvider, TISSRequest, TISSStatus


class InMemoryInsuranceProviderRepository:
    """Dict-based insurance provider repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, InsuranceProvider] = {}

    async def get_by_id(self, provider_id: UUID) -> Optional[InsuranceProvider]:
        return self._store.get(provider_id)

    async def get_all(
        self, tenant_id: UUID, active_only: bool = True
    ) -> list[InsuranceProvider]:
        providers = [
            p for p in self._store.values()
            if p.tenant_id == tenant_id
        ]
        if active_only:
            providers = [p for p in providers if p.active]
        return providers

    async def save(self, provider: InsuranceProvider) -> None:
        self._store[provider.id] = provider

    async def update(self, provider: InsuranceProvider) -> None:
        self._store[provider.id] = provider


class InMemoryTISSRequestRepository:
    """Dict-based TISS request repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, TISSRequest] = {}

    async def get_by_id(self, request_id: UUID) -> Optional[TISSRequest]:
        return self._store.get(request_id)

    async def get_all(
        self,
        tenant_id: UUID,
        status: Optional[TISSStatus] = None,
        patient_id: Optional[UUID] = None,
    ) -> list[TISSRequest]:
        requests = [
            r for r in self._store.values()
            if r.tenant_id == tenant_id
        ]
        if status:
            requests = [r for r in requests if r.status == status]
        if patient_id:
            requests = [r for r in requests if r.patient_id == patient_id]
        return requests

    async def save(self, request: TISSRequest) -> None:
        self._store[request.id] = request

    async def update(self, request: TISSRequest) -> None:
        self._store[request.id] = request
