"""Use case: Register new user + clinic."""

from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID

from odontoflow.iam.domain.models import Tenant, TenantMembership, TenantStatus, User
from odontoflow.iam.domain.repositories import MembershipRepository, TenantRepository, UserRepository
from odontoflow.iam.domain.services import PasswordService, TokenService
from odontoflow.shared.domain.errors import ConflictError, ValidationError
from odontoflow.shared.domain.types import PlanTier, UserRole


@dataclass
class RegisterResult:
    user: User
    tenant: Tenant
    membership: TenantMembership
    access_token: str
    refresh_token: str


class RegisterUserCommand:
    def __init__(
        self,
        user_repo: UserRepository,
        tenant_repo: TenantRepository,
        membership_repo: MembershipRepository,
    ):
        self._user_repo = user_repo
        self._tenant_repo = tenant_repo
        self._membership_repo = membership_repo

    async def execute(
        self,
        email: str,
        password: str,
        full_name: str,
        clinic_name: str,
        clinic_slug: str,
    ) -> RegisterResult:
        # Validacoes
        if len(password) < 8:
            raise ValidationError("Senha deve ter no minimo 8 caracteres")

        slug = clinic_slug.lower().strip()
        if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", slug):
            raise ValidationError("Slug deve conter apenas letras minusculas, numeros e hifens")

        # Unicidade
        existing_user = await self._user_repo.get_by_email(email.lower())
        if existing_user:
            raise ConflictError("Email ja cadastrado")

        existing_tenant = await self._tenant_repo.get_by_slug(slug)
        if existing_tenant:
            raise ConflictError("Slug ja em uso")

        # Criar user
        user = User(
            email=email.lower(),
            password_hash=PasswordService.hash_password(password),
            full_name=full_name,
        )
        await self._user_repo.save(user)

        # Criar tenant
        schema_name = f"tenant_{re.sub(r'[^a-z0-9]', '_', slug)}"
        tenant = Tenant(
            slug=slug,
            name=clinic_name,
            email=email.lower(),
            plan_tier=PlanTier.FREE,
            schema_name=schema_name,
            status=TenantStatus.TRIAL,
        )
        await self._tenant_repo.save(tenant)

        # Criar membership (OWNER)
        membership = TenantMembership(
            user_id=user.id,
            tenant_id=tenant.id,
            role=UserRole.OWNER,
            permissions=[],
        )
        await self._membership_repo.save(membership)

        # Gerar tokens
        access_token = TokenService.create_access_token(
            user_id=user.id,
            tenant_id=tenant.id,
            role=UserRole.OWNER.value,
            email=user.email,
            full_name=user.full_name,
        )
        refresh_token = TokenService.create_refresh_token(user.id)

        return RegisterResult(
            user=user,
            tenant=tenant,
            membership=membership,
            access_token=access_token,
            refresh_token=refresh_token,
        )
