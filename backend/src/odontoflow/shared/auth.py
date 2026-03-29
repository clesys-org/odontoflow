"""Auth types for dependency injection."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.shared.domain.types import UserRole


@dataclass(frozen=True)
class CurrentUser:
    user_id: UUID
    email: str
    full_name: str
    tenant_id: UUID
    role: UserRole
    permissions: list[str] = field(default_factory=list)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions or self.role in (UserRole.OWNER, UserRole.ADMIN)

    def is_provider(self) -> bool:
        return self.role in (UserRole.DENTIST, UserRole.OWNER)
