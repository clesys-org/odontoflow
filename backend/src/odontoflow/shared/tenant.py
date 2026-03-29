"""Multi-tenant context management via contextvars."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID

_current_tenant: ContextVar[TenantContext | None] = ContextVar("current_tenant", default=None)


@dataclass(frozen=True)
class TenantContext:
    tenant_id: UUID
    schema_name: str
    clinic_name: str


def get_current_tenant() -> TenantContext:
    ctx = _current_tenant.get()
    if ctx is None:
        raise RuntimeError("No tenant context set. Ensure tenant middleware is configured.")
    return ctx


def set_current_tenant(ctx: TenantContext) -> None:
    _current_tenant.set(ctx)


def clear_current_tenant() -> None:
    _current_tenant.set(None)
