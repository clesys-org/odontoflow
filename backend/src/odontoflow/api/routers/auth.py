"""API Router: Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from odontoflow.api.deps import (
    get_current_user,
    get_membership_repo,
    get_tenant_repo,
    get_user_repo,
)
from odontoflow.api.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from odontoflow.iam.application.commands.login_user import LoginUserCommand
from odontoflow.iam.application.commands.register_user import RegisterUserCommand
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.errors import ConflictError, NotFoundError, ValidationError

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(
    req: RegisterRequest,
    user_repo=Depends(get_user_repo),
    tenant_repo=Depends(get_tenant_repo),
    membership_repo=Depends(get_membership_repo),
):
    """Registra novo usuario + clinica."""
    cmd = RegisterUserCommand(user_repo, tenant_repo, membership_repo)
    try:
        result = await cmd.execute(
            email=req.email,
            password=req.password,
            full_name=req.full_name,
            clinic_name=req.clinic_name,
            clinic_slug=req.clinic_slug,
        )
    except ConflictError as e:
        raise HTTPException(409, e.message)
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    user_repo=Depends(get_user_repo),
    membership_repo=Depends(get_membership_repo),
):
    """Autentica usuario e retorna tokens JWT."""
    cmd = LoginUserCommand(user_repo, membership_repo)
    try:
        result = await cmd.execute(email=req.email, password=req.password)
    except (NotFoundError, ValidationError):
        raise HTTPException(401, "Credenciais invalidas")

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    tenant_repo=Depends(get_tenant_repo),
):
    """Retorna perfil do usuario autenticado."""
    tenant = await tenant_repo.get_by_id(current_user.tenant_id)
    clinic_name = tenant.name if tenant else ""

    return UserResponse(
        id=str(current_user.user_id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        tenant_id=str(current_user.tenant_id),
        clinic_name=clinic_name,
    )
