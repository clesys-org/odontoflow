"""API Router: Website Builder endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from odontoflow.api.deps import get_current_user, get_website_repo
from odontoflow.api.schemas.website import (
    CreateWebsiteRequest,
    PublicWebsiteResponse,
    ServiceItemResponse,
    UpdateWebsiteRequest,
    WebsiteResponse,
)
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.errors import ConflictError, NotFoundError, ValidationError
from odontoflow.website.application.commands.create_website import (
    CreateWebsiteCommand,
    ServiceItemInput,
)
from odontoflow.website.application.commands.toggle_publish import TogglePublishCommand
from odontoflow.website.application.commands.update_website import UpdateWebsiteCommand
from odontoflow.website.application.commands.update_website import (
    ServiceItemInput as UpdateServiceItemInput,
)
from odontoflow.website.application.queries.get_public_website import GetPublicWebsiteQuery
from odontoflow.website.application.queries.get_website import GetWebsiteQuery
from odontoflow.website.domain.models import ClinicWebsite

router = APIRouter(
    prefix="/api/v1",
    tags=["website"],
)

public_router = APIRouter(
    prefix="/api/v1/public",
    tags=["website-public"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _website_to_response(w: ClinicWebsite) -> WebsiteResponse:
    return WebsiteResponse(
        id=str(w.id),
        clinic_name=w.clinic_name,
        slug=w.slug,
        tagline=w.tagline,
        description=w.description,
        phone=w.phone,
        whatsapp=w.whatsapp,
        email=w.email,
        address=w.address,
        logo_url=w.logo_url,
        primary_color=w.primary_color,
        services=[
            ServiceItemResponse(
                name=s.name,
                description=s.description,
                icon=s.icon,
            )
            for s in w.services
        ],
        working_hours_text=w.working_hours_text,
        social_links=w.social_links,
        seo_title=w.seo_title,
        seo_description=w.seo_description,
        google_maps_embed=w.google_maps_embed,
        booking_enabled=w.booking_enabled,
        published=w.published,
        created_at=w.created_at.isoformat(),
        updated_at=w.updated_at.isoformat(),
    )


def _website_to_public_response(w: ClinicWebsite) -> PublicWebsiteResponse:
    return PublicWebsiteResponse(
        clinic_name=w.clinic_name,
        slug=w.slug,
        tagline=w.tagline,
        description=w.description,
        phone=w.phone,
        whatsapp=w.whatsapp,
        email=w.email,
        address=w.address,
        logo_url=w.logo_url,
        primary_color=w.primary_color,
        services=[
            ServiceItemResponse(
                name=s.name,
                description=s.description,
                icon=s.icon,
            )
            for s in w.services
        ],
        working_hours_text=w.working_hours_text,
        social_links=w.social_links,
        seo_title=w.seo_title,
        seo_description=w.seo_description,
        google_maps_embed=w.google_maps_embed,
        booking_enabled=w.booking_enabled,
    )


# ---------------------------------------------------------------------------
# Authenticated endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/website",
    response_model=WebsiteResponse,
)
async def get_website(
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_website_repo),
):
    """Obtem configuracao do site da clinica."""
    query = GetWebsiteQuery(tenant_id=current_user.tenant_id)
    try:
        website = await query.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Site da clinica nao encontrado")
    return _website_to_response(website)


@router.post(
    "/website",
    response_model=WebsiteResponse,
    status_code=201,
)
async def create_website(
    req: CreateWebsiteRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_website_repo),
):
    """Cria site da clinica."""
    cmd = CreateWebsiteCommand(
        tenant_id=current_user.tenant_id,
        clinic_name=req.clinic_name,
        slug=req.slug,
        tagline=req.tagline,
        description=req.description,
        phone=req.phone,
        whatsapp=req.whatsapp,
        email=req.email,
        address=req.address,
        primary_color=req.primary_color,
        services=[
            ServiceItemInput(name=s.name, description=s.description, icon=s.icon)
            for s in req.services
        ],
        working_hours_text=req.working_hours_text,
    )
    try:
        website = await cmd.execute(repo)
    except ConflictError as e:
        raise HTTPException(409, e.message)
    except ValidationError as e:
        raise HTTPException(422, e.message)
    return _website_to_response(website)


@router.put(
    "/website",
    response_model=WebsiteResponse,
)
async def update_website(
    req: UpdateWebsiteRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_website_repo),
):
    """Atualiza site da clinica."""
    services_input = None
    if req.services is not None:
        services_input = [
            UpdateServiceItemInput(name=s.name, description=s.description, icon=s.icon)
            for s in req.services
        ]

    cmd = UpdateWebsiteCommand(
        tenant_id=current_user.tenant_id,
        clinic_name=req.clinic_name,
        tagline=req.tagline,
        description=req.description,
        phone=req.phone,
        whatsapp=req.whatsapp,
        email=req.email,
        address=req.address,
        logo_url=req.logo_url,
        primary_color=req.primary_color,
        services=services_input,
        working_hours_text=req.working_hours_text,
        social_links=req.social_links,
        seo_title=req.seo_title,
        seo_description=req.seo_description,
        google_maps_embed=req.google_maps_embed,
        booking_enabled=req.booking_enabled,
    )
    try:
        website = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Site da clinica nao encontrado")
    except ValidationError as e:
        raise HTTPException(422, e.message)
    return _website_to_response(website)


@router.patch(
    "/website/publish",
    response_model=WebsiteResponse,
)
async def toggle_publish(
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_website_repo),
):
    """Alterna publicacao do site."""
    cmd = TogglePublishCommand(tenant_id=current_user.tenant_id)
    try:
        website = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Site da clinica nao encontrado")
    except ValidationError as e:
        raise HTTPException(422, e.message)
    return _website_to_response(website)


# ---------------------------------------------------------------------------
# Public endpoints (no auth)
# ---------------------------------------------------------------------------


@public_router.get(
    "/clinics/{slug}",
    response_model=PublicWebsiteResponse,
)
async def get_public_clinic(
    slug: str,
    repo=Depends(get_website_repo),
):
    """Obtem informacoes publicas da clinica (sem autenticacao)."""
    query = GetPublicWebsiteQuery(slug=slug)
    try:
        website = await query.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Clinica nao encontrada")
    return _website_to_public_response(website)


@public_router.get(
    "/clinics/{slug}/booking-slots",
)
async def get_booking_slots(
    slug: str,
    date: str = Query(..., description="Data no formato YYYY-MM-DD"),
    type: str = Query("consulta", description="Tipo de agendamento"),
    repo=Depends(get_website_repo),
):
    """Retorna horarios disponiveis para agendamento publico."""
    # Validate clinic exists and is published
    query = GetPublicWebsiteQuery(slug=slug)
    try:
        website = await query.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Clinica nao encontrada")

    if not website.booking_enabled:
        raise HTTPException(400, "Agendamento online desabilitado para esta clinica")

    # TODO: integrate with scheduling BC to return real available slots
    return {
        "clinic": slug,
        "date": date,
        "type": type,
        "slots": [],
        "message": "Integracao com agenda em desenvolvimento",
    }
