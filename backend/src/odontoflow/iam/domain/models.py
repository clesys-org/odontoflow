"""IAM Bounded Context — Domain Models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot, Entity
from odontoflow.shared.domain.types import PlanTier, UserRole


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"


class TenantStatus(str, Enum):
    ACTIVE = "ACTIVE"
    TRIAL = "TRIAL"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"


@dataclass
class User(AggregateRoot):
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    status: UserStatus = UserStatus.ACTIVE
    mfa_enabled: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Tenant(AggregateRoot):
    slug: str = ""
    name: str = ""
    cnpj: str | None = None
    phone: str | None = None
    email: str | None = None
    plan_tier: PlanTier = PlanTier.FREE
    schema_name: str = ""
    status: TenantStatus = TenantStatus.TRIAL
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TenantMembership(Entity):
    user_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    role: UserRole = UserRole.DENTIST
    permissions: list[str] = field(default_factory=list)
