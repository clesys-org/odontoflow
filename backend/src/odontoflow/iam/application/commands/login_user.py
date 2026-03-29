"""Use case: Login user."""

from __future__ import annotations

from dataclasses import dataclass

from odontoflow.iam.domain.repositories import MembershipRepository, UserRepository
from odontoflow.iam.domain.services import PasswordService, TokenService
from odontoflow.shared.domain.errors import NotFoundError, ValidationError


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str
    user_id: str
    email: str
    full_name: str
    role: str
    tenant_id: str
    clinic_name: str


class LoginUserCommand:
    def __init__(
        self,
        user_repo: UserRepository,
        membership_repo: MembershipRepository,
    ):
        self._user_repo = user_repo
        self._membership_repo = membership_repo

    async def execute(self, email: str, password: str) -> LoginResult:
        user = await self._user_repo.get_by_email(email.lower())
        if not user:
            raise NotFoundError("User", email)

        if not PasswordService.verify_password(password, user.password_hash):
            raise ValidationError("Credenciais invalidas")

        # Buscar primeiro tenant
        memberships = await self._membership_repo.get_by_user(user.id)
        if not memberships:
            raise ValidationError("Usuario sem clinica associada")

        membership = memberships[0]

        # Gerar tokens
        access_token = TokenService.create_access_token(
            user_id=user.id,
            tenant_id=membership.tenant_id,
            role=membership.role.value,
            email=user.email,
            full_name=user.full_name,
        )
        refresh_token = TokenService.create_refresh_token(user.id)

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=membership.role.value,
            tenant_id=str(membership.tenant_id),
            clinic_name="",  # Populated by router
        )
