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
from odontoflow.billing.infrastructure.in_memory_billing_repo import InMemoryInvoiceRepository
from odontoflow.clinical.infrastructure.in_memory_clinical_repo import InMemoryClinicalRepository
from odontoflow.insurance.infrastructure.in_memory_insurance_repo import (
    InMemoryInsuranceProviderRepository,
    InMemoryTISSRequestRepository,
)
from odontoflow.inventory.infrastructure.in_memory_inventory_repo import (
    InMemoryMaterialRepository,
    InMemorySupplierRepository,
)
from odontoflow.patient.infrastructure.in_memory_patient_repo import InMemoryPatientRepository
from odontoflow.scheduling.infrastructure.in_memory_scheduling_repo import (
    InMemoryAppointmentRepository,
    InMemoryProviderScheduleRepository,
)
from odontoflow.staff.infrastructure.in_memory_staff_repo import (
    InMemoryProductionRepository,
    InMemoryStaffRepository,
)
from odontoflow.treatment.infrastructure.in_memory_treatment_repo import (
    InMemoryProcedureCatalogRepository,
    InMemoryTreatmentPlanRepository,
)
from odontoflow.analytics.infrastructure.analytics_aggregator import AnalyticsAggregator
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.types import UserRole
from odontoflow.shared.event_bus import EventBus

# Singletons (in-memory repos — sera substituido por PostgreSQL)
_user_repo = InMemoryUserRepository()
_tenant_repo = InMemoryTenantRepository()
_membership_repo = InMemoryMembershipRepository()
_patient_repo = InMemoryPatientRepository()
_clinical_repo = InMemoryClinicalRepository()
_appointment_repo = InMemoryAppointmentRepository()
_provider_schedule_repo = InMemoryProviderScheduleRepository()
_treatment_plan_repo = InMemoryTreatmentPlanRepository()
_procedure_catalog_repo = InMemoryProcedureCatalogRepository()
_invoice_repo = InMemoryInvoiceRepository()
_insurance_provider_repo = InMemoryInsuranceProviderRepository()
_tiss_request_repo = InMemoryTISSRequestRepository()
_material_repo = InMemoryMaterialRepository()
_supplier_repo = InMemorySupplierRepository()
_staff_repo = InMemoryStaffRepository()
_production_repo = InMemoryProductionRepository()
_analytics_aggregator = AnalyticsAggregator(
    patient_repo=_patient_repo,
    appointment_repo=_appointment_repo,
    invoice_repo=_invoice_repo,
)

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


def get_clinical_repo() -> InMemoryClinicalRepository:
    return _clinical_repo


def get_appointment_repo() -> InMemoryAppointmentRepository:
    return _appointment_repo


def get_provider_schedule_repo() -> InMemoryProviderScheduleRepository:
    return _provider_schedule_repo


def get_treatment_plan_repo() -> InMemoryTreatmentPlanRepository:
    return _treatment_plan_repo


def get_procedure_catalog_repo() -> InMemoryProcedureCatalogRepository:
    return _procedure_catalog_repo


def get_invoice_repo() -> InMemoryInvoiceRepository:
    return _invoice_repo


def get_insurance_provider_repo() -> InMemoryInsuranceProviderRepository:
    return _insurance_provider_repo


def get_tiss_request_repo() -> InMemoryTISSRequestRepository:
    return _tiss_request_repo


def get_material_repo() -> InMemoryMaterialRepository:
    return _material_repo


def get_supplier_repo() -> InMemorySupplierRepository:
    return _supplier_repo


def get_staff_repo() -> InMemoryStaffRepository:
    return _staff_repo


def get_production_repo() -> InMemoryProductionRepository:
    return _production_repo


def get_analytics_aggregator() -> AnalyticsAggregator:
    return _analytics_aggregator


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
