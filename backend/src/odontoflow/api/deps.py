"""Dependency injection container for FastAPI."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from odontoflow.iam.domain.services import TokenService
from odontoflow.iam.infrastructure.in_memory_repos import (
    InMemoryMembershipRepository,
    InMemoryTenantRepository,
    InMemoryUserRepository,
)
from odontoflow.patient.infrastructure.in_memory_patient_repo import InMemoryPatientRepository
from odontoflow.scheduling.infrastructure.in_memory_scheduling_repo import (
    InMemoryAppointmentRepository,
    InMemoryProviderScheduleRepository,
)
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.types import UserRole
from odontoflow.shared.event_bus import EventBus

# Singletons (in-memory repos — sera substituido por PostgreSQL)
_user_repo = InMemoryUserRepository()
_tenant_repo = InMemoryTenantRepository()
_membership_repo = InMemoryMembershipRepository()
_patient_repo = InMemoryPatientRepository()
_appointment_repo = InMemoryAppointmentRepository()
_provider_schedule_repo = InMemoryProviderScheduleRepository()

_bearer = HTTPBearer(auto_error=False)


def get_event_bus(request: Request) -> EventBus:
    return request.app.state.event_bus


def get_user_repo() -> InMemoryUserRepository:
    return _user_repo


def get_tenant_repo() -> InMemoryTenantRepository:
    return _tenant_repo


def get_membership_repo() -> InMemoryMembershipRepository:
    return _membership_repo


def get_patient_repo() -> InMemoryPatientRepository:
    return _patient_repo


def get_appointment_repo() -> InMemoryAppointmentRepository:
    return _appointment_repo


def get_provider_schedule_repo() -> InMemoryProviderScheduleRepository:
    return _provider_schedule_repo


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    if not credentials:
        raise HTTPException(401, "Token nao fornecido", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = TokenService.decode_token(credentials.credentials)
    except ValueError:
        raise HTTPException(401, "Token invalido", headers={"WWW-Authenticate": "Bearer"})

    if payload.get("type") != "access":
        raise HTTPException(401, "Token invalido (tipo errado)")

    return CurrentUser(
        user_id=UUID(payload["sub"]),
        email=payload["email"],
        full_name=payload["full_name"],
        tenant_id=UUID(payload["tenant_id"]),
        role=UserRole(payload["role"]),
    )
