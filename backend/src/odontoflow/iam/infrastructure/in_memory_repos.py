"""In-memory repository implementations for testing and initial development."""

from __future__ import annotations

from uuid import UUID

from odontoflow.iam.domain.models import Tenant, TenantMembership, User


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users.values() if u.email == email), None)

    async def save(self, user: User) -> None:
        self._users[user.id] = user

    async def update(self, user: User) -> None:
        self._users[user.id] = user


class InMemoryTenantRepository:
    def __init__(self) -> None:
        self._tenants: dict[UUID, Tenant] = {}

    async def get_by_id(self, tenant_id: UUID) -> Tenant | None:
        return self._tenants.get(tenant_id)

    async def get_by_slug(self, slug: str) -> Tenant | None:
        return next((t for t in self._tenants.values() if t.slug == slug), None)

    async def save(self, tenant: Tenant) -> None:
        self._tenants[tenant.id] = tenant

    async def update(self, tenant: Tenant) -> None:
        self._tenants[tenant.id] = tenant


class InMemoryMembershipRepository:
    def __init__(self) -> None:
        self._memberships: dict[UUID, TenantMembership] = {}

    async def get_by_user_and_tenant(self, user_id: UUID, tenant_id: UUID) -> TenantMembership | None:
        return next(
            (m for m in self._memberships.values() if m.user_id == user_id and m.tenant_id == tenant_id),
            None,
        )

    async def get_by_tenant(self, tenant_id: UUID) -> list[TenantMembership]:
        return [m for m in self._memberships.values() if m.tenant_id == tenant_id]

    async def get_by_user(self, user_id: UUID) -> list[TenantMembership]:
        return [m for m in self._memberships.values() if m.user_id == user_id]

    async def save(self, membership: TenantMembership) -> None:
        self._memberships[membership.id] = membership

    async def delete(self, membership_id: UUID) -> bool:
        return self._memberships.pop(membership_id, None) is not None
